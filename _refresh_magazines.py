"""Refresh verified magazine metadata from configured official sources.

Only titles, explicit publication dates and article URLs are collected. A failed
or empty response preserves every existing article for that publication. This
script never evaluates publisher JavaScript or synthesizes article contents.
Missing independent notes receive explicitly labelled title-based reading questions.

Usage: python _refresh_magazines.py [--dry-run] [--today YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
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
PER_PUBLICATION = 80
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
    if publication.get("parser") in ("cn", "rss"):
        if publication["parser"] == "cn":
            from _magazines_cn import collect as provider_collect
        else:
            from _magazines_rss import collect as provider_collect
        return provider_collect(publication, today, timeout, fetch_text, official_url,
                                article, parse_html, limit=PER_PUBLICATION)
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
            url = "https://www.yicai.com/vip" + path
            try:
                rows.append(article(publication, item.get("NewsTitle"), url,
                                    item.get("CreateDate"), today))
            except (TypeError, ValueError) as error:
                # An index/short label in the official feed cannot discard
                # other independently validated stories in the same response.
                details.append({"url": url, "status": "unavailable", "reason": error_text(error)})
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
        # Partial list text can include a category/teaser when a detail fetch
        # fails. Do not splice that new headline onto an earlier article date.
        if (not row.get("publishedAt") and old.get("publishedAt")
                and row.get("title") != old.get("title")):
            merged["title"] = old["title"]
            merged["checkedAt"] = old["checkedAt"]
        if old.get("summaryBasis") == "title-and-publication" and merged.get("title") != old.get("title"):
            merged["summary"] = ""
            merged.pop("summaryBasis", None)
        if merged["url"] not in {x["url"] for x in fresh}:
            fresh.append(merged)
    old_rows = [dict(row) for row in previous if row.get("publication") == publication
                and row["url"] not in {x["url"] for x in fresh}]
    # A successful older feed must not push newer verified articles out when
    # another feed of the same publication temporarily fails. Only explicit
    # source dates determine recency; undated rows remain at the end.
    combined = sorted(fresh + old_rows,
                      key=lambda row: row.get("publishedAt") or "", reverse=True)
    # Keep explicit reading selections and current official ranking entries
    # when the rolling feed reaches its cap. Curation is reapplied by exact
    # title/URL; a successfully refreshed ranking clears dropped hot flags.
    regular = combined[:PER_PUBLICATION]
    kept = {row["url"] for row in regular}
    selected = [row for row in combined[PER_PUBLICATION:]
                if (row.get("featuredReason") or row.get("hotRank"))
                and row["url"] not in kept]
    return regular + selected


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
            record = {"publication": publication, "title": old["title"],
                "url": old["url"], "publishedAt": old.get("publishedAt"),
                "checkedAt": old.get("checkedAt"),
                "verification": "Retained from an earlier successful source report; not fetched this run."}
            fields = ("hotRank", "hotSource", "hotLabel", "hotCheckedAt")
            if old.get("hotRank") and all(old.get(k) == row.get(k) for k in fields):
                record.update({k: old[k] for k in fields if k in old})
            retained.append(record)
    return retained


def refresh(publications, previous, today, timeout, prior_report=None, workers=1):
    def refresh_one(original):
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
            if evidence.get("hotStatus") == "ok" or evidence.get("hotLists"):
                # A newly verified list replaces its previous membership. A
                # failed list fetch leaves the last known ranks and dates.
                current_hot = {row["url"] for row in incoming if row.get("hotRank")}
                for row in rows:
                    if row["url"] not in current_hot:
                        for field in ("hotRank", "hotSource", "hotLabel", "hotCheckedAt"):
                            row.pop(field, None)
            report.update(status="ok", **evidence)
        except Exception as error:
            reason = error_text(error)
            publication.update(status="unavailable", note=publication["sourceNote"] +
                               " 本次自动核查未成功，保留已核实文章。")
            rows = [row for row in previous if row.get("publication") == publication["id"]]
            report.update(status="unavailable", reason=reason, articles=[])
        report["retainedArticles"] = retained_evidence(rows, publication["id"], prior_report)
        return publication, rows, report
    if workers > 1:
        with ThreadPoolExecutor(max_workers=min(workers, len(publications))) as pool:
            results = list(pool.map(refresh_one, publications))
    else:
        results = [refresh_one(p) for p in publications]
    output = [result[0] for result in results]
    all_articles = [row for result in results for row in result[1]]
    reports = [result[2] for result in results]
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


def apply_editorial(rows, editorial):
    """Apply explicit site curation only while its exact article still matches."""
    if not isinstance(editorial, dict) or not isinstance(editorial.get("articles"), list):
        raise ValueError("Editorial selections must contain an article list")
    selected = {}
    for item in editorial["articles"]:
        if (not isinstance(item, dict) or not isinstance(item.get("reason"), str)
                or not item["reason"].strip() or not isinstance(item.get("priority"), int)):
            raise ValueError("Every editorial selection needs a reason and priority")
        selected[(item.get("publication"), item.get("url"), item.get("title"))] = item
    for row in rows:
        row.pop("featuredReason", None)
        row.pop("featuredPriority", None)
        item = selected.get((row["publication"], row["url"], row["title"]))
        if item:
            row.update(featuredReason=item["reason"], featuredPriority=item["priority"])
    return rows


def ensure_reading_guides(rows, publications):
    """Add reading questions, never pretend to summarize an unread article.

    Only title and publication category are used. Existing authored notes and all
    source facts, dates and rankings remain intact; the basis is visible in text.
    """
    categories = {p["id"]: p.get("category", "") for p in publications}
    angles = [
        (r"电池|储能|负极|正极|battery|batteries|electrode|electroly", "区分材料性能、器件表现与应用条件；原文给了哪些循环、能量密度或对照证据，哪些仍待验证？"),
        (r"聚变|超导|fusion|plasma|superconduct", "分清理论、实验装置与工程应用；关注稳定性、能量收支和验证条件，避免把单点突破当成可用系统。"),
        (r"量子|quantum|entangl|qubit", "先分清研究对象、观测量与实验条件；哪些结论依赖理想模型，作者如何排除其他解释？"),
        (r"宇宙|星系|行星|黑洞|space|galax|planet|black hole|cosmic|astronom", "把直接观测与模型推断分开记录；结论依赖哪些仪器、样本和误差范围，还有哪些替代解释？"),
        (r"气候|碳排|气温|climate|warming|carbon emission", "核对空间范围、时间尺度与基线；分清观测趋势、情景预测和政策判断，关注不确定性如何表达。"),
        (r"药|癌|疫苗|疾病|血糖|植入|cancer|vaccine|disease|implant|blood sugar|therapy|treatment", "先确认是细胞、动物还是人体证据，再看对照、样本量和风险；科研报道的可能性不能直接当作个人诊疗建议。"),
        (r"脑|记忆|睡眠|brain|memory|sleep|neuron", "区分相关性、实验干预与机制解释；留意参与者范围、测量方法和结果能否迁移到日常生活。"),
        (r"基因|蛋白|细胞|gene|protein|cell|dna|rna", "记录研究尺度、实验体系和关键对照；作者从分子现象推到生物功能时，还需要补上哪些验证？"),
        (r"动物|生态|鸟|森林|animal|bird|forest|species|ecolog", "关注观察地点、季节与样本范围；把物种行为、环境压力和人的解释分开，核对结论的适用边界。"),
        (r"数学|几何|拓扑|math|geometr|topolog|prime", "先写清问题的定义与假设，再找关键论证；哪些是已证明结果，哪些是数值迹象或尚未解决的猜想？"),
        (r"机器人|robot|自动驾驶|无人驾驶", "区分演示、基准评测与真实场景部署；重点核对任务边界、失效情形、数据条件和人工介入。"),
        (r"人工智能|大模型|算力|英伟达|OpenAI|\bAI\b|algorithm|artificial intelligence", "区分模型能力、产品体验与商业承诺；核对具体任务、比较基线、数据限制与使用成本，避免把演示当成普遍能力。"),
        (r"汽车|燃油|新能源车|car market|automaker", "从产品、成本与渠道三处看竞争；核对销量和利润的口径及时间范围，思考技术路线变化如何传到企业经营。"),
        (r"电力|电网|能源|买电|energy|electricity|power grid", "区分装机、实际发电与可调度能力；关注供需时段、基础设施和成本由谁承担，再判断方案的适用条件。"),
        (r"利率|加息|美联储|汇率|人民币|通胀|inflation|interest rate", "先核对指标定义、统计时点和传导路径；把已发生的数据与政策预期分开，留意结论依赖的经济情景。"),
        (r"投资|融资|IPO|上市|理财|基金|赚钱|亏损|亏了|ipo|invest|stock market", "核对收入、利润、现金流与估值各自的口径；关注风险由谁承担以及信息是否完整，不从报道直接推出交易决定。"),
        (r"消费|零食|品牌|超市|李宁|安踏|阿迪|爱马仕|快时尚|Uniqlo|Lemaire", "观察需求、定价、渠道与品牌定位如何相互作用；区分个别案例和市场趋势，核对数据时间及样本范围。"),
        (r"职场|员工|打工|工程师|求职|就业|裁员|工作|job|worker|employment", "从岗位、组织和个人选择三个层面读；核对案例背景与制度约束，思考哪些经验可迁移、哪些依赖特定条件。"),
        (r"学校|大学|教育|阅读力|老师|学生|养育|父母|孩子|education|school|parent", "区分个体经验、调查结果与教育主张；关注年龄、家庭及制度背景，避免把单一案例变成对所有人的要求。"),
        (r"总统|总理|大选|政治|政党|选举|战争|中东|美国|英国|北爱|加沙|election|president|war\b", "先梳理事件时间线和各方立场；把已核实事实、当事人说法与作者判断分开，再看制度和历史背景如何影响解释。"),
        (r"访|人物|艺术家|作家|画师|诗人|演员|专栏|访谈|interview|artist|writer", "留意受访者或作者的具体经历、表达语境与选择；把个人叙述和可核实事实分开，记录一个值得继续追问的问题。"),
        (r"电影|剧|银幕|诺兰|足球|冠军|梅西|music|film|cinema", "区分作品或赛事本身、产业环境和个人评价；找出支撑判断的具体细节，避免只记住评分、输赢或热度。"),
    ]
    defaults = {
        "科学新知": "先确认研究问题、证据类型与验证条件；记录一个关键变量和一项限制，分清观测、推断与应用设想。",
        "商业财经": "核对商业模式、成本与利益分配；把案例叙述和数据证据分开，观察结论适用于什么市场与时间范围。",
        "人物纪实": "沿着具体经历和选择阅读；注意叙述者视角及可核实细节，保留人物处境，避免把个体经验当作普遍答案。",
        "时事观察": "先整理事件时间线、来源与各方说法；区分报道事实、因果解释和评论，检查是否遗漏关键背景。",
        "生活人文": "从作者选取的细节与观察角度入手；区分个人体验、文化解释与普遍判断，记录一个与你自身经验相关的问题。",
    }
    added = 0
    for row in rows:
        if clean(row.get("summary")):
            continue
        title = clean(row.get("title"))
        angle = next((text for pattern, text in angles if re.search(pattern, title, re.I)),
                     defaults.get(categories.get(row.get("publication")),
                                  "先明确文章讨论的对象与问题；区分事实、观点和推断，找出支撑结论的证据与尚未回答的问题。"))
        row["summary"] = "据标题的阅读切入点：《" + title + "》。" + angle
        row["summaryBasis"] = "title-and-publication"
        added += 1
    return added


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print metadata report; write no files")
    parser.add_argument("--today", type=date.fromisoformat,
                        default=date.today(), help="Explicit check date for reproducible checks")
    parser.add_argument("--data", type=Path, default=ROOT / "magazines.js")
    parser.add_argument("--report", type=Path, default=ROOT / "_magazines_refresh.json")
    parser.add_argument("--editorial", type=Path, default=ROOT / "_magazines_editorial.json")
    parser.add_argument("--timeout", type=float, default=12)
    parser.add_argument("--workers", type=int, default=4,
                        help="Independent official-source workers (1-6)")
    args = parser.parse_args()
    if not 0 < args.timeout <= 60:
        parser.error("--timeout must be greater than zero and no more than 60 seconds")
    if not 1 <= args.workers <= 6:
        parser.error("--workers must be between 1 and 6")
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
                                            prior_report=prior_report, workers=args.workers)
        if args.editorial.exists():
            articles = apply_editorial(articles, json.loads(args.editorial.read_text(encoding="utf-8-sig")))
        added_guides = ensure_reading_guides(articles, publications)
        report["readingGuides"] = {"added": added_guides, "basis": "Title and publication category only; explicitly labelled reading questions, not a claim to have read or summarized the full article."}
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
