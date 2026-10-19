"""Metadata-only collectors for verified Chinese magazine publishers.

No publisher JavaScript is evaluated. Dates come from labelled article metadata
or the publisher's explicit JSON fields, never from URL paths or issue dates.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from html import unescape
import json
import re
from urllib.parse import urljoin, urlsplit


def clean(value):
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


def ssr(text):
    match = re.search(r"window\.__INITIAL_DATA__\s*=\s*([\s\S]*?);window\.__USE_VITE__", text)
    if not match:
        raise ValueError("Official New Weekly SSR metadata is absent")
    return json.loads(match.group(1))


def items(value):
    if isinstance(value, dict):
        if value.get("articleUid") and value.get("title"):
            yield value
        for child in value.values():
            yield from items(child)
    elif isinstance(value, list):
        for child in value:
            yield from items(child)


def timestamp(value):
    if not isinstance(value, (int, float)) or not 946684800000 <= value < 4102444800000:
        return None
    return datetime.fromtimestamp(value / 1000, timezone(timedelta(hours=8))).date().isoformat()


def collect(publication, today, timeout, fetch_text, official_url, article, parse_html, limit=60):
    host = urlsplit(publication["url"]).hostname
    feed = publication.get("feedUrl") or publication["url"]
    hosts = publication["hosts"]
    evidence = {"listUrl": feed, "articles": [], "details": []}
    rows, seen = [], set()

    def add(title, url, published=None, **extra):
        title = clean(title)
        if "{{" in title or "}}" in title:
            return
        try:
            url = official_url(url, hosts, feed)
            if url in seen or len(title) < 4:
                return
            row = article(publication, title, url, published, today)
        except (ValueError, TypeError):
            return
        if row.get("publishedAt") and row["publishedAt"] > today:
            return
        seen.add(url)
        row.update(extra)
        rows.append(row)

    if host in ("neweekly.com.cn", "www.neweekly.com.cn"):
        # The apex domain currently serves the official SSR site; www is 404.
        text, final = fetch_text(feed, hosts, timeout)
        data = ssr(text)
        index = data.get("indexStore", {}).get("data", {})
        # Homepage editorial content and daily feed; omit paid magazine issue
        # tables with no article date rather than borrowing an issue date.
        for key in ("header", "daily", "video"):
            for item in items(index.get(key)):
                if item.get("moTitle") == "商业":
                    continue
                add(item["title"], "https://neweekly.com.cn/article/" + item["articleUid"],
                    timestamp(item.get("factTime")))
        list_urls = ["https://neweekly.com.cn/daily"]
        for column in index.get("column", []):
            if isinstance(column, dict) and isinstance(column.get("id"), int):
                list_urls.append("https://neweekly.com.cn/column/" + str(column["id"]))
        for url in list_urls[:5]:
            try:
                body, resolved = fetch_text(url, hosts, timeout)
                doc = ssr(body)
                contents = (doc.get("dailyStore", {}).get("list", []) if "/daily" in url else
                            doc.get("columnStore", {}).get("articleList", []))
                for item in contents:
                    if not isinstance(item, dict) or not item.get("articleUid") or item.get("moTitle") == "商业":
                        continue
                    add(item.get("title"), "https://neweekly.com.cn/article/" + item["articleUid"],
                        timestamp(item.get("factTime")))
                evidence["details"].append({"url": resolved, "status": "ok", "items": len(contents)})
            except Exception as error:
                evidence["details"].append({"url": url, "status": "unavailable", "reason": str(error)[:180]})
    elif host == "www.infzm.com":
        # Same endpoint used by the public homepage HotContents component.
        hot_url = "https://www.infzm.com/hot_contents?format=json"
        text, resolved = fetch_text(hot_url, hosts, timeout)
        payload = json.loads(text)
        hot = payload.get("data", {}).get("hot_contents")
        if payload.get("code") != 200 or not isinstance(hot, list):
            raise ValueError("Official Southern Weekly hot-article response is absent")
        for rank, item in enumerate(hot, 1):
            if not isinstance(item, dict) or not isinstance(item.get("id"), int):
                continue
            add(item.get("subject"), "https://www.infzm.com/contents/" + str(item["id"]),
                item.get("publish_time"), hotRank=rank, hotSource=hot_url,
                hotLabel="南方周末热门文章", hotCheckedAt=today)
        evidence["hotList"] = {"url": hot_url, "asOf": today,
                               "label": "南方周末官网热门文章顺序；不代表跨刊综合热度", "items": len(hot)}
        evidence["hotStatus"] = "ok"
        evidence["hotLists"] = [evidence["hotList"]]
        # Explicit JSON list pages avoid noisy nested anchor text and expose dates.
        for url in ("https://www.infzm.com/contents?term_id=1&format=json",
                    "https://www.infzm.com/contents?term_id=998&format=json"):
            try:
                text, final = fetch_text(url, hosts, timeout)
                doc = json.loads(text)
                contents = doc.get("data", {}).get("contents", [])
                if not isinstance(contents, list):
                    continue
                for item in contents:
                    if not isinstance(item, dict) or not isinstance(item.get("id"), int):
                        continue
                    add(item.get("subject"), "https://www.infzm.com/contents/" + str(item["id"]),
                        item.get("publish_time"))
                evidence["details"].append({"url": final, "status": "ok", "items": len(contents)})
            except Exception as error:
                evidence["details"].append({"url": url, "status": "unavailable", "reason": str(error)[:180]})
    else:
        text, final = fetch_text(feed, hosts, timeout)
        candidates = []
        list_pages = [(final, text)]
        if host == "www.inewsweek.cn":
            for channel in ("society", "finance", "world", "wh"):
                url = "https://www.inewsweek.cn/" + channel + "/"
                try:
                    body, resolved = fetch_text(url, hosts, timeout)
                    list_pages.append((resolved, body))
                except Exception as error:
                    evidence["details"].append({"url": url, "status": "unavailable", "reason": str(error)[:180]})
        if host == "magazine.caijing.com.cn":
            # Follow actual current issue link, never invent an issue identifier.
            links = parse_html(text).links
            issues = list(dict.fromkeys(link["url"].strip().replace("http://", "https://", 1)
                                        for link in links
                                        if re.search(r"/caijingmagazine/\d{4}/\d+/", link["url"])))
            normalized = []
            for issue in issues:
                if issue.startswith("http://"):
                    issue = "https://" + issue[7:]
                issue = official_url(issue, hosts, final)
                if issue not in normalized:
                    normalized.append(issue)
            if normalized:
                list_pages = []
                for issue in normalized[:6]:
                    try:
                        body, resolved = fetch_text(issue, hosts, timeout)
                        list_pages.append((resolved, body))
                        evidence["details"].append({"url": resolved, "status": "ok"})
                    except Exception as error:
                        evidence["details"].append({"url": issue, "status": "unavailable", "reason": str(error)[:180]})
        if host == "weekly.caixin.com":
            links = parse_html(text).links
            issue = next((link["url"] for link in links
                          if re.search(r"weekly\.caixin\.com/\d{4}/cw\d+/", link["url"])), None)
            if issue:
                body, resolved = fetch_text(official_url(issue, hosts, final), hosts, timeout)
                list_pages.append((resolved, body))
        for base, body in list_pages:
            for link in parse_html(body).links:
                raw = link.get("url", "")
                # Verified publishers use HTTP links in HTTPS issue directories.
                if raw.startswith("http://"):
                    raw = "https://" + raw[7:]
                try:
                    url = official_url(raw, hosts, base)
                except ValueError:
                    continue
                path = urlsplit(url).path
                valid = ((host == "www.nfpeople.com" and re.fullmatch(r"/article/\d+", path)) or
                         (host == "www.inewsweek.cn" and re.fullmatch(r"/(?:society|finance|world|wh|politics|auto)/\d{4}-\d{2}-\d{2}/\d+\.shtml", path)) or
                         (host == "magazine.caijing.com.cn" and re.fullmatch(r"/\d{8}/\d+\.shtml", path)) or
                         (host == "weekly.caixin.com" and re.fullmatch(r"/(?:m/)?\d{4}-\d{2}-\d{2}/\d+\.html", path)))
                title = clean(link.get("text") or link.get("title"))
                if valid and 4 <= len(title) <= 200 and url not in {c[1] for c in candidates}:
                    candidates.append((title, url))
        if host == "www.nfpeople.com":
            # Homepage also contains a permanent old interview/photo archive.
            candidates.sort(key=lambda c: int(c[1].rsplit("/", 1)[1]), reverse=True)
        candidates = candidates[:limit]

        def detail(candidate):
            title, url = candidate
            try:
                body, final = fetch_text(url, hosts, timeout)
                page = parse_html(body)
                published = next((page.meta.get(k) for k in
                                  ("article:published_time", "publishdate", "pubdate", "datePublished")
                                  if page.meta.get(k)), None)
                patterns = {
                    "www.nfpeople.com": r'日期\s*[：:]\s*(\d{4}-\d{2}-\d{2})',
                    "www.inewsweek.cn": r'<div\s+class=["\x27]editor["\x27][^>]*>[\s\S]*?(\d{4}-\d{2}-\d{2})',
                    "magazine.caijing.com.cn": r'<span\s+class=["\x27]news_date["\x27][^>]*>\s*(\d{4}-\d{2}-\d{2})',
                    "weekly.caixin.com": r'id=["\x27]pubtime_baidu["\x27][^>]*>\s*(\d{4}-\d{2}-\d{2})',
                }
                if not published:
                    match = re.search(patterns.get(host, r"(?!x)x"), body)
                    published = match.group(1) if match else None
                # Prefer the exact story heading over a parent link containing
                # category labels, teasers or homepage marketing prefixes.
                # Caijing's h1 is a logo and og:title is an SEO title with the
                # complete breadcrumb appended. Its issue directory is exact.
                headline = (None if host == "magazine.caijing.com.cn" else
                            page.meta.get("og:title") or (page.h1[0] if page.h1 else None))
                if headline and len(clean(headline)) >= 4:
                    headline = clean(headline)
                    if "{{" not in headline and "}}" not in headline:
                        title = headline
                return title, final, published, {"url": final, "status": "ok", "publishedAt": published}
            except Exception as error:
                return title, url, None, {"url": url, "status": "unavailable", "reason": str(error)[:180]}

        with ThreadPoolExecutor(max_workers=6) as pool:
            for title, url, published, proof in pool.map(detail, candidates):
                add(title, url, published)
                evidence["details"].append(proof)
    if not rows:
        raise ValueError("No verified article metadata found for this publisher")
    rows.sort(key=lambda row: (row.get("publishedAt") or "", row["url"]), reverse=True)
    rows = rows[:limit]
    evidence["articles"] = rows
    return rows, evidence
