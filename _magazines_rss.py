"""Official magazine RSS metadata and two verified publisher popularity lists.

The caller owns network policy, article validation and merging with old records.
Only Quanta's explicit Past Week / Most Read Articles block and Science News'
explicit Trending Stories block can add popularity metadata. An RSS order is
never treated as popularity, and URL paths are never used as publication dates.
"""
from __future__ import annotations

from datetime import date, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import xml.etree.ElementTree as ET


def _clean(value):
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, value):
        self.parts.append(value)


def _title(value):
    parser = _Text()
    parser.feed(str(value or ""))
    return _clean("".join(parser.parts))


def _date(value):
    """Read an explicit feed timestamp, retaining its source's calendar day."""
    value = str(value or "").strip()
    if not value:
        return None
    match = re.match(r"^(\d{4}-\d{2}-\d{2})(?:$|[T\s])", value)
    if match:
        try:
            # Do not shift a 23:00 -04:00 publication into the following UTC day.
            return date.fromisoformat(match.group(1)).isoformat()
        except ValueError:
            return None
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


def _canonical(value):
    parsed = urlsplit(value)
    query = [(key, val) for key, val in parse_qsl(parsed.query, keep_blank_values=True)
             if not key.lower().startswith("utm_")
             and key.lower() not in ("mc_cid", "mc_eid")]
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path,
                       urlencode(query), ""))


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _feed_rows(text, pub, today, base, official_url, article, limit):
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.I):
        raise ValueError("RSS document contains an unsupported DTD or entity")
    root = ET.fromstring(text)
    if _local(root.tag) not in ("rss", "RDF", "feed"):
        raise ValueError("Expected an official RSS, RDF or Atom document")
    atom = _local(root.tag) == "feed"
    rows, seen = [], set()
    for element in root.iter():
        if _local(element.tag) != ("entry" if atom else "item"):
            continue
        fields = {}
        link = None
        for child in element:
            key = _local(child.tag)
            fields.setdefault(key, "".join(child.itertext()))
            if key != "link":
                continue
            if atom:
                if child.get("rel", "alternate") == "alternate":
                    link = child.get("href") or link
            elif child.text:
                link = child.text
        # RSS1 uses dc:date; Atom's `updated` is not a publication timestamp.
        published = _date(fields.get("published") if atom else
                          fields.get("pubDate") or fields.get("date"))
        if published and published > today:
            continue
        try:
            url = _canonical(official_url(link or "", pub["hosts"], base))
            if not link or url in seen:
                continue
            row = article(pub, _title(fields.get("title")), url, published, today)
        except (TypeError, ValueError):
            continue
        seen.add(url)
        rows.append(row)
        if len(rows) >= limit:
            break
    if not rows:
        raise ValueError("Official feed contains no validated article metadata")
    return rows, ("Atom" if atom else "RSS1/RDF" if _local(root.tag) == "RDF" else "RSS2")


def _quanta_hot(text):
    """Read only the observed publisher sidebar, not arbitrary page links."""
    start = re.search(r"<div\b[^>]*class=['\"][^'\"]*\bpopular\b[^'\"]*['\"]", text)
    if not start:
        raise ValueError("Quanta's official popular sidebar is absent")
    end = text.find("</aside>", start.start())
    if end < 0:
        raise ValueError("Quanta's popular sidebar boundary is absent")
    block = text[start.start():end]
    if not re.search(r">\s*Past Week\s*</p>", block) or not re.search(
            r">\s*Most Read Articles\s*</h3>", block):
        raise ValueError("Quanta's verified Past Week / Most Read labels are absent")
    rows = []
    for match in re.finditer(r"<a\b([^>]*)>([\s\S]*?)</a>", block):
        attrs, content = match.groups()
        if not re.search(r"\bclass=['\"][^'\"]*\bcard-list__title\b", attrs):
            continue
        href = re.search(r"\bhref=['\"]([^'\"]+)['\"]", attrs)
        if href:
            rows.append({"title": _title(content), "url": unescape(href.group(1)),
                         "publishedAt": None})
    if not rows:
        raise ValueError("Quanta's official Most Read list is empty")
    return rows, "Past Week · Most Read Articles", "Past Week", (
        "Official Past Week Most Read Articles list, in the order displayed; "
        "the publisher does not supply view counts.")


def _sciencenews_hot(text):
    start = re.search(r'<section\b[^>]*class=[\'\"][^\'\"]*\btrending-stories__wrapper', text)
    if not start:
        raise ValueError("Science News' official Trending Stories section is absent")
    end = text.find("</section>", start.start())
    if end < 0:
        raise ValueError("Science News' trending section boundary is absent")
    block = text[start.start():end]
    if not re.search(r"Trending\s+Stories\s*<", block):
        raise ValueError("Science News' verified Trending Stories label is absent")
    rows = []
    for item in re.findall(r"<li\b[^>]*>([\s\S]*?)</li>", block):
        title = re.search(r"<h3\b[^>]*>\s*<a\b[^>]*href=['\"]([^'\"]+)['\"][^>]*>"
                          r"([\s\S]*?)</a>\s*</h3>", item)
        if not title:
            continue
        stamp = re.search(r"<time\b[^>]*\bdatetime=['\"]([^'\"]+)['\"]", item)
        rows.append({"title": _title(title.group(2)), "url": unescape(title.group(1)),
                     "publishedAt": _date(stamp.group(1)) if stamp else None})
    if not rows:
        raise ValueError("Science News' official Trending Stories list is empty")
    return rows, "Trending Stories", None, (
        "Official Trending Stories section in display order; the publisher "
        "does not show view counts or a statistical time window.")


def collect(pub, today, timeout, fetch_text, official_url, article, parse_html, limit=60):
    """Return (rows, evidence), using only explicitly configured official URLs.

    Config: parser='rss', feedUrl and/or feedUrls; optional hotFeedUrl for the
    verified Quanta or Science News homepage. A partial feed failure is recorded;
    a total failure raises, allowing the caller to preserve previously checked
    metadata. `parse_html` is accepted for the shared collector interface.
    """
    if isinstance(today, (date, datetime)):
        today = today.isoformat()[:10]
    date.fromisoformat(today)
    limit = max(1, min(int(limit), 200))
    feeds = pub.get("feedUrls") or []
    if isinstance(feeds, str):
        feeds = [feeds]
    feeds = list(feeds)
    if pub.get("feedUrl"):
        feeds.insert(0, pub["feedUrl"])
    feeds = list(dict.fromkeys(feeds))
    rows_by_url, details, list_url, hot_lists = {}, [], None, []
    for feed in feeds:
        try:
            feed = official_url(feed, pub["hosts"])
            text, final = fetch_text(feed, pub["hosts"], timeout)
            final = official_url(final, pub["hosts"])
            rows, fmt = _feed_rows(text, pub, today, final, official_url, article, limit)
            for row in rows:
                old = rows_by_url.get(row["url"])
                if not old or (not old.get("publishedAt") and row.get("publishedAt")):
                    rows_by_url[row["url"]] = row
            list_url = list_url or final
            details.append({"url": final, "status": "ok", "format": fmt,
                            "articles": len(rows)})
        except Exception as error:
            details.append({"url": feed, "status": "unavailable",
                            "reason": _clean(error)[:300]})
    hot_url = pub.get("hotFeedUrl")
    hot_urls = []
    if hot_url:
        try:
            hot_url = official_url(hot_url, pub["hosts"])
            source = urlsplit(hot_url)
            parser = {"www.quantamagazine.org": _quanta_hot,
                      "www.sciencenews.org": _sciencenews_hot}.get(source.hostname)
            if not parser or source.path not in ("", "/") or source.query:
                raise ValueError("No verified popularity parser for this configured URL")
            text, final = fetch_text(hot_url, pub["hosts"], timeout)
            final = official_url(final, pub["hosts"])
            resolved = urlsplit(final)
            if resolved.hostname != source.hostname or resolved.path not in ("", "/"):
                raise ValueError("Popularity source redirected away from verified homepage")
            items, label, window, metric = parser(text)
            hot_items, seen = [], set()
            for item in items:
                if len(hot_items) >= limit:
                    break
                try:
                    url = _canonical(official_url(item["url"], pub["hosts"], final))
                    if url in seen or (item["publishedAt"] and item["publishedAt"] > today):
                        continue
                    row = article(pub, item["title"], url, item["publishedAt"], today)
                except (TypeError, ValueError):
                    continue
                seen.add(url)
                rank = len(hot_items) + 1
                old = rows_by_url.get(url)
                if old:
                    row = old.copy()
                    if not row.get("publishedAt") and item.get("publishedAt"):
                        row["publishedAt"] = item["publishedAt"]
                row.update(hotRank=rank, hotSource=final, hotLabel=label,
                           hotCheckedAt=today)
                rows_by_url[url] = row
                hot_urls.append(url)
                hot_items.append({"rank": rank, "title": row["title"], "url": url,
                                  "publishedAt": row.get("publishedAt")})
            if not hot_items:
                raise ValueError("Official popularity list has no validated entries")
            list_id = ("quanta-past-week-most-read" if source.hostname == "www.quantamagazine.org"
                       else "sciencenews-trending")
            hot_lists.append({"id": list_id, "publication": pub["id"], "title": label,
                              "sourceUrl": final, "asOf": today, "metric": metric,
                              "window": window, "items": hot_items})
            list_url = list_url or final
            details.append({"url": final, "status": "ok", "type": "official-hot-list",
                            "articles": len(hot_items), "label": label})
        except Exception as error:
            details.append({"url": hot_url, "status": "unavailable", "type": "official-hot-list",
                            "reason": _clean(error)[:300]})
    if not rows_by_url:
        raise ValueError("No verified RSS or official popularity metadata: " +
                         "; ".join(item.get("reason", "") for item in details)[:600])
    # Keep actual popularity-list entries even when a long feed reaches the cap.
    hot_rows = [rows_by_url[url] for url in hot_urls[:limit]]
    remainder = sorted((row for url, row in rows_by_url.items() if url not in set(hot_urls)),
                       key=lambda row: row.get("publishedAt") or "", reverse=True)
    rows = hot_rows + remainder[:max(0, limit - len(hot_rows))]
    rows.sort(key=lambda row: row.get("publishedAt") or "", reverse=True)
    evidence = {"listUrl": list_url, "articles": rows, "details": details,
                "hotLists": hot_lists}
    if hot_url:
        evidence["hotStatus"] = "ok" if hot_lists else "unavailable"
    return rows, evidence
