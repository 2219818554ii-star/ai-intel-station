"""Refresh verified magazine metadata from configured official sources.

Only titles, explicit publication dates and article URLs are collected. A failed
or empty response preserves every existing article for that publication. This
script never evaluates publisher JavaScript or synthesizes article summaries.

Usage: python _refresh_magazines.py [--dry-run] [--today YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import gzip
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request
import zlib

ROOT = Path(__file__).resolve().parent
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
MAX_BYTES = 3_000_000
PER_PUBLICATION = 24
MAX_DETAIL_REQUESTS = 8


def clean(value):
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


def explicit_date(value):
    match = re.match(r"^(\d{4}-\d{2}-\d{2})(?:$|[T\s])", str(value or "").strip())
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1)).isoformat()
    except ValueError:
        return None


def official_url(value, hosts, base=""):
    """Accept only configured exact HTTPS hosts, including redirects."""
    result = urlsplit(urljoin(base, unescape(str(value or ""))))
    allowed = {str(host).lower().rstrip(".") for host in hosts}
    try:
        valid = (result.scheme == "https" and result.hostname in allowed
                 and not result.username and not result.password
                 and result.port in (None, 443))
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("URL is outside this publication's configured HTTPS hosts")
    return urlunsplit((result.scheme, result.netloc, result.path or "/", result.query, ""))


class OfficialRedirect(HTTPRedirectHandler):
    # Some publishers return a redirect challenge loop; do not spend the daily
    # task following the same challenge repeatedly or call that a fresh list.
    max_repeats = 2
    max_redirections = 3

    def __init__(self, hosts):
        self.hosts = hosts

    def redirect_request(self, request, response, code, message, headers, newurl):
        official_url(newurl, self.hosts, request.full_url)
        return super().redirect_request(request, response, code, message, headers, newurl)


def fetch_text(url, hosts, timeout):
    url = official_url(url, hosts)
    request = Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity",
                                   "Accept": "application/json,text/html,application/xhtml+xml"})
    with build_opener(OfficialRedirect(hosts)).open(request, timeout=timeout) as response:
        final = official_url(response.geturl(), hosts)
        if response.status != 200:
            raise ValueError("HTTP %s; no verified article list" % response.status)
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Response exceeds metadata size limit")
        encoding = response.headers.get("Content-Encoding", "").lower()
        if encoding == "gzip":
            raw = gzip.decompress(raw)
        elif encoding == "deflate":
            raw = zlib.decompress(raw)
        if len(raw) > MAX_BYTES:
            raise ValueError("Decoded response exceeds metadata size limit")
        if not raw.strip():
            raise ValueError("Empty response; no verified article list")
        charset = response.headers.get_content_charset() or "utf-8"
        try:
            text = raw.decode(charset)
        except (LookupError, UnicodeDecodeError):
            text = raw.decode("gb18030")
    return text, final


class MetadataHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.current = None
        self.heading = None
        self.h1 = []
        self.title = []
        self.in_title = False
        self.meta = {}
        self.plain = []
        self.skip = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "a":
            self.current = {"url": attrs.get("href", ""), "text": [],
                            "title": attrs.get("title", "")}
        if tag == "h1":
            self.heading = []
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            self.meta[attrs.get("property") or attrs.get("name", "")] = attrs.get("content", "")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag == "a" and self.current is not None:
            item = self.current
            item["text"] = clean(" ".join(item["text"])) or clean(item["title"])
            self.links.append(item)
            self.current = None
        if tag == "h1" and self.heading is not None:
            self.h1.append(clean(" ".join(self.heading)))
            self.heading = None
        if tag == "title":
            self.in_title = False

    def handle_data(self, value):
        if self.skip:
            return
        self.plain.append(value)
        if self.current is not None:
            self.current["text"].append(value)
        if self.heading is not None:
            self.heading.append(value)
        if self.in_title:
            self.title.append(value)


def parse_html(text):
    parser = MetadataHTML()
    parser.feed(text)
    return parser


def article(publication, title, url, published, today):
    title = clean(title)
    if not 4 <= len(title) <= 200 or re.search(r"<|>|javascript:", title, re.I):
        raise ValueError("Missing or invalid article title")
    return {"publication": publication["id"], "title": title,
            "url": official_url(url, publication["hosts"]),
            "publishedAt": explicit_date(published), "summary": "", "checkedAt": today}


def detail_metadata(url, publication, timeout, *, allow_title=False):
    text, final = fetch_text(url, publication["hosts"], timeout)
    page = parse_html(text)
    title = page.h1[0] if page.h1 else page.meta.get("og:title", "")
    if allow_title:
        # Lifeweek's h1 is the site logo (“三联生活周刊”), not the story.
        # Its verified page title carries the actual article and this suffix.
        title_tag = clean(" ".join(page.title))
        if not title_tag.endswith("-三联生活网"):
            raise ValueError("Official Lifeweek article title signature is absent")
        title = title_tag.removesuffix("-三联生活网").strip()
        if title in ("三联生活周刊", "三联生活网"):
            raise ValueError("Site branding cannot be accepted as an article title")
    published = next((page.meta[key] for key in
                      ("article:published_time", "publishdate", "pubdate", "datePublished")
                      if key in page.meta), None)
    # This is an explicitly labelled article timestamp, never a path or issue date.
    if not published:
        found = re.search(r"发表时间[：:]\s*(\d{4}-\d{2}-\d{2})(?:\s+\d{2}:\d{2})?",
                          clean(" ".join(page.plain)))
        published = found.group(1) if found else None
    return title, published, final, page


def collect(publication, today, timeout):
    """Return a verified list and metadata-only fetch evidence."""
    feed = publication.get("feedUrl") or publication["url"]
    text, final = fetch_text(feed, publication["hosts"], timeout)
    hostname = urlsplit(final).hostname
    rows, details = [], []
    if hostname in ("www.yicai.com", "yicai.com") and "/api/ajax/getlistbypid" in final:
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("Unexpected official magazine JSON response")
        for item in data[:PER_PUBLICATION]:
            if not isinstance(item, dict) or item.get("ChannelName") != "第一财经杂志":
                continue
            path = item.get("url", "")
            if not re.fullmatch(r"/news/\d+\.html", path):
                continue
            rows.append(article(publication, item.get("NewsTitle"),
                                "https://www.yicai.com/vip" + path,
                                item.get("CreateDate"), today))
    elif hostname == "www.lifeweek.com.cn" and "/magazine" in urlsplit(final).path:
        # Nuxt shares values through parameters. Read only the active magazine's
        # actual IDs, then use each article page's title; never eval the bundle.
        ref = re.search(r"activePeriodicalRecommend:([A-Za-z_$][\w$]*)", text)
        if not ref:
            raise ValueError("Active magazine recommendation block is absent")
        block = re.search(re.escape(ref.group(1)) + r"\.rltArticleList=\[([\s\S]*?)\];", text)
        if not block:
            raise ValueError("Active magazine article list is absent")
        ids = list(dict.fromkeys(re.findall(r"\bid:(\d+),title:", block.group(1))))
        for identifier in ids[:PER_PUBLICATION]:
            url = "https://www.lifeweek.com.cn/article/" + identifier
            try:
                title, published, resolved, _ = detail_metadata(url, publication, timeout,
                                                               allow_title=True)
                rows.append(article(publication, title, resolved, published, today))
                details.append({"url": resolved, "status": "ok", "title": title})
            except Exception as error:
                details.append({"url": url, "status": "unavailable", "reason": error_text(error)})
    elif hostname in ("boyamedia.com", "www.boyamedia.com", "m.boyamedia.com"):
        expected = "category-rw" if publication["id"] == "renwu" else "category-bk"
        if expected not in urlsplit(final).path:
            raise ValueError("Require the verified publication channel, not the mixed publisher homepage")
        page = parse_html(text)
        seen = set()
        for link in page.links:
            try:
                url = official_url(link["url"], publication["hosts"], final)
            except ValueError:
                continue
            if not re.fullmatch(r"/sys-nd/\d+\.html", urlsplit(url).path) or url in seen:
                continue
            seen.add(url)
            try:
                title, published, resolved, detail = detail_metadata(url, publication, timeout)
                body = clean(" ".join(detail.plain))
                marker = r"人物\s*作者" if publication["id"] == "renwu" else r"博客\s*作者"
                if not re.search(marker, body):
                    raise ValueError("Article publication attribution could not be confirmed")
                rows.append(article(publication, title, resolved, published, today))
                details.append({"url": resolved, "status": "ok", "title": title})
            except Exception as error:
                details.append({"url": url, "status": "unavailable", "reason": error_text(error)})
            if len(seen) >= MAX_DETAIL_REQUESTS:
                break
    elif hostname == "www.pedaily.cn" and urlsplit(final).path.rstrip("/") == "/media/m439":
        page = parse_html(text)
        if "商界传媒集团官方账号" not in clean(" ".join(page.plain)):
            raise ValueError("Official Shangjie account identification is absent")
        seen = set()
        for link in page.links:
            try:
                url = official_url(link["url"], publication["hosts"], final)
            except ValueError:
                continue
            if (urlsplit(url).hostname != "news.pedaily.cn"
                    or not re.fullmatch(r"/\d{6}/\d+\.shtml", urlsplit(url).path) or url in seen):
                continue
            seen.add(url)
            try:
                title, published, resolved, detail = detail_metadata(url, publication, timeout)
                body = clean(" ".join(detail.plain))
                if not re.search(r"合作伙伴\s*商界\s*授权发布", body):
                    raise ValueError("Article is not attributed as authorized by Shangjie")
                if not published:
                    stamp = re.search(r"\b(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}\b", body)
                    published = stamp.group(1) if stamp else None
                rows.append(article(publication, title, resolved, published, today))
                details.append({"url": resolved, "status": "ok", "title": title})
            except Exception as error:
                details.append({"url": url, "status": "unavailable", "reason": error_text(error)})
            if len(seen) >= MAX_DETAIL_REQUESTS:
                break
    else:
        # Do not widen to arbitrary same-host recommendations or aggregator feeds.
        raise ValueError("No verified publication-specific metadata parser is configured")
    if not rows:
        reason = "No trustworthy publication-specific articles found; old entries retained"
        if details:
            reason += "; " + details[0].get("reason", "article metadata absent")
        raise ValueError(reason)
    return rows, {"listUrl": final, "articles": rows, "details": details}


def error_text(error):
    if isinstance(error, HTTPError):
        return "HTTP %s; source unavailable, not classified as a dead link" % error.code
    return clean(str(error))[:300]


def read_assignment(source, name):
    match = re.search(r"\bwindow\." + re.escape(name) + r"\s*=\s*", source)
    if not match:
        raise ValueError("Missing JSON assignment window." + name)
    value, length = json.JSONDecoder().raw_decode(source[match.end():])
    return value, (match.end(), match.end() + length)


def write_assignments(source, assignments):
    edits = []
    for name, value in assignments.items():
        _, (start, end) = read_assignment(source, name)
        # The build inlines this JS inside <script>. JSON escaping is needed in
        # addition to the renderer's HTML escaping, including editorial blurbs.
        encoded = json.dumps(value, ensure_ascii=False, indent=2).replace("<", "\\u003c")
        edits.append((start, end, encoded))
    for start, end, value in sorted(edits, reverse=True):
        source = source[:start] + value + source[end:]
    return source


def merge_articles(previous, incoming, publication):
    known = {row["url"]: row for row in previous if row.get("publication") == publication}
    fresh = []
    for row in incoming:
        old = known.get(row["url"], {})
        merged = {**old, **row}
        merged["summary"] = old.get("summary", "")
        # A missing timestamp from today's list does not erase a known source date.
        merged["publishedAt"] = row.get("publishedAt") or old.get("publishedAt")
        if merged["url"] not in {x["url"] for x in fresh}:
            fresh.append(merged)
    old_rows = [row for row in previous if row.get("publication") == publication
                and row["url"] not in {x["url"] for x in fresh}]
    return (fresh + old_rows)[:PER_PUBLICATION]


def retained_evidence(rows, publication, prior_report):
    """Carry source evidence forward; the data file cannot certify itself."""
    verified = {}
    for source in (prior_report or {}).get("sources", []):
        if source.get("publication") != publication:
            continue
        evidence = list(source.get("retainedArticles", []))
        if source.get("status") == "ok":
            evidence += source.get("articles", [])
        for old in evidence:
            key = (old.get("title"), old.get("url"), old.get("publishedAt"))
            verified[key] = old
    retained = []
    for row in rows:
        key = (row.get("title"), row.get("url"), row.get("publishedAt"))
        if key in verified:
            old = verified[key]
            retained.append({"publication": publication, "title": old["title"],
                "url": old["url"], "publishedAt": old.get("publishedAt"),
                "checkedAt": old.get("checkedAt"),
                "verification": "Retained from an earlier successful source report; not fetched this run."})
    return retained


def refresh(publications, previous, today, timeout, prior_report=None):
    output, all_articles, reports = [], [], []
    for original in publications:
        publication = dict(original)
        publication["checkedAt"] = today
        # Keep the editorial description/access note separate from a transient
        # failure, so tomorrow's success does not retain yesterday's warning.
        publication["sourceNote"] = publication.get("sourceNote", publication.get("note", ""))
        report = {"publication": publication["id"], "checkedAt": today,
                  "attemptedUrl": publication.get("feedUrl") or publication["url"]}
        try:
            incoming, evidence = collect(publication, today, timeout)
            publication.update(status="ok", lastSuccessAt=today,
                               note=publication["sourceNote"])
            rows = merge_articles(previous, incoming, publication["id"])
            report.update(status="ok", **evidence)
        except Exception as error:
            reason = error_text(error)
            publication.update(status="unavailable", note=publication["sourceNote"] +
                               " 本次自动核查未成功，保留已核实文章。")
            rows = [row for row in previous if row.get("publication") == publication["id"]]
            report.update(status="unavailable", reason=reason, articles=[])
        report["retainedArticles"] = retained_evidence(rows, publication["id"], prior_report)
        output.append(publication)
        all_articles.extend(rows)
        reports.append(report)
    return output, all_articles, {"checkedAt": today,
        "attemptedAt": datetime.now(timezone.utc).isoformat(), "sources": reports,
        "policy": "Official metadata only; failed sources preserve previous entries and dates; no full text."}


def atomic_write(path, text):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".magazines-", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(text)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print metadata report; write no files")
    parser.add_argument("--today", type=date.fromisoformat,
                        default=date.today(), help="Explicit check date for reproducible checks")
    parser.add_argument("--data", type=Path, default=ROOT / "magazines.js")
    parser.add_argument("--report", type=Path, default=ROOT / "_magazines_refresh.json")
    parser.add_argument("--timeout", type=float, default=12)
    args = parser.parse_args()
    if not 0 < args.timeout <= 60:
        parser.error("--timeout must be greater than zero and no more than 60 seconds")
    try:
        source = args.data.read_text(encoding="utf-8")
        publications, _ = read_assignment(source, "MAGAZINES")
        previous, _ = read_assignment(source, "MAGAZINE_ARTICLES")
        if not isinstance(publications, list) or not publications or not isinstance(previous, list):
            raise ValueError("Magazine data must contain nonempty publication and article arrays")
        if any(not isinstance(row, dict) for row in publications + previous):
            raise ValueError("Publication and article entries must be JSON objects")
        ids = [row.get("id") for row in publications]
        if any(not identifier for identifier in ids) or len(ids) != len(set(ids)):
            raise ValueError("Publication identities must be nonempty and unique")
        if any(not isinstance(row.get("hosts"), list) or not row["hosts"] for row in publications):
            raise ValueError("Each publication requires an explicit official host allowlist")
        if any(row.get("publication") not in ids or not isinstance(row.get("url"), str)
               for row in previous):
            raise ValueError("Previous articles must retain valid publication and URL identities")
        prior_report = {}
        if args.report.exists():
            prior_report = json.loads(args.report.read_text(encoding="utf-8-sig"))
            if not isinstance(prior_report, dict) or not isinstance(prior_report.get("sources", []), list):
                raise ValueError("Previous metadata report has an invalid evidence structure")
        updated, articles, report = refresh(publications, previous, args.today.isoformat(), args.timeout,
                                            prior_report=prior_report)
        if args.dry_run:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            rendered = write_assignments(source, {"MAGAZINES_CHECKED": args.today.isoformat(),
                "MAGAZINES": updated, "MAGAZINE_ARTICLES": articles})
            atomic_write(args.data, rendered)
            atomic_write(args.report, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
            for item in report["sources"]:
                print("%s: %s (%d verified article metadata records)" %
                      (item["publication"], item["status"], len(item["articles"])))
            print("Report:", args.report)
        return 0 if any(item["status"] == "ok" for item in report["sources"]) else 1
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print("Magazine refresh failed: " + error_text(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
