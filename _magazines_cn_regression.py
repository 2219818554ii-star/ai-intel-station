"""Offline regression tests for Chinese publisher metadata and rank evidence.

Run: python _magazines_cn_regression.py
Fixtures reproduce only the official structures observed during verification;
all fetches are mocked and no publisher prose or network requests are needed.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json
import unittest
from unittest.mock import patch

import _magazines_cn as cn
import _refresh_magazines as refresh


TODAY = "2026-10-19"
HOT_URL = "https://www.infzm.com/hot_contents?format=json"
NORMAL_URL = "https://www.infzm.com/contents?term_id=1&format=json"


def publication(identity, url):
    return {"id": identity, "name": identity, "url": url, "feedUrl": url,
            "hosts": [url.split("/")[2]], "parser": "cn", "note": "fixture",
            "lastSuccessAt": "2026-10-18"}


def json_ssr(value):
    return ("<script>window.__INITIAL_DATA__=" + json.dumps(value, ensure_ascii=False)
            + ";window.__USE_VITE__=false</script>")


class OfflineFetch:
    def __init__(self, documents):
        self.documents = documents
        self.requested = []

    def __call__(self, url, hosts, timeout):
        refresh.official_url(url, hosts)
        self.requested.append(url)
        value = self.documents.get(url, OSError("Fixture source unavailable"))
        if isinstance(value, Exception):
            raise value
        if isinstance(value, tuple):
            text, final = value
            refresh.official_url(final, hosts)
            return text, final
        return value, url


def collect(pub, documents, limit=60):
    fetch = OfflineFetch(documents)
    rows, evidence = cn.collect(pub, TODAY, 1, fetch, refresh.official_url,
                                refresh.article, refresh.parse_html, limit=limit)
    return rows, evidence, fetch.requested


class ChineseMagazineRegression(unittest.TestCase):
    def test_ssr_is_json_and_does_not_evaluate_publisher_code(self):
        payload = {"indexStore": {"data": {"header": {"articleUid": "shp001",
                    "title": "JSON中的正常题名", "factTime": 1792324837000}}}}
        self.assertEqual(cn.ssr(json_ssr(payload)), payload)
        script = ("window.__INITIAL_DATA__=(function(){throw new Error('never execute')})()"
                  ";window.__USE_VITE__=false")
        with self.assertRaises(json.JSONDecodeError):
            cn.ssr(script)
        with self.assertRaises(ValueError):
            cn.ssr("<html>Access denied</html>")

    def test_facttime_is_milliseconds_and_uses_beijing_day(self):
        # UTC 16:30 is already the following calendar day in Beijing.
        instant = datetime(2026, 10, 18, 16, 30, tzinfo=timezone.utc)
        self.assertEqual(cn.timestamp(int(instant.timestamp() * 1000)), "2026-10-19")
        self.assertEqual(cn.timestamp(1792324837000), "2026-10-18")
        for invalid in (None, "1792324837000", 1792324837, 0, -1, float("inf"), True):
            with self.subTest(invalid=invalid):
                self.assertIsNone(cn.timestamp(invalid))

    def test_ssr_deduplication_unknown_dates_and_partial_failure(self):
        pub = publication("neweekly", "https://neweekly.com.cn/")
        item = {"articleUid": "shp001", "title": "主页真实文章", "factTime": 1792324837000}
        documents = {
            pub["url"]: json_ssr({"indexStore": {"data": {"header": item,
                    "column": [{"id": 10071}]}}}),
            "https://neweekly.com.cn/daily": json_ssr({"dailyStore": {"list": [item,
                {"articleUid": "shp002", "title": "没有明确时间的文章", "factTime": None},
                {"articleUid": "shp003", "title": "未来发布时间文章", "factTime": 1893456000000},
                {"articleUid": "shp004", "title": "官网商业推广示例", "moTitle": "商业"}]}}),
            "https://neweekly.com.cn/column/10071": OSError("temporarily blocked"),
        }
        rows, evidence, _ = collect(pub, documents)
        self.assertEqual(len(rows), 2)
        by_url = {row["url"]: row for row in rows}
        self.assertEqual(by_url["https://neweekly.com.cn/article/shp001"]["publishedAt"], "2026-10-18")
        self.assertIsNone(by_url["https://neweekly.com.cn/article/shp002"]["publishedAt"])
        self.assertTrue(any(detail["status"] == "unavailable" for detail in evidence["details"]))
        self.assertEqual(evidence["articles"], rows)

    def test_southern_weekly_rank_is_not_latest_order_or_synthetic_score(self):
        pub = publication("infzm", "https://www.infzm.com/")
        documents = {
            HOT_URL: json.dumps({"code": 200, "data": {"hot_contents": [
                {"id": 101, "subject": "榜单第一篇旧文章", "publish_time": "2026-10-13 10:00:00"},
                {"id": 102, "subject": "榜单第二篇新文章", "publish_time": "2026-10-18 11:00:00"}]}}),
            NORMAL_URL: json.dumps({"data": {"contents": [
                {"id": 103, "subject": "最新但没有热榜名次", "publish_time": "2026-10-19 09:00:00"},
                {"id": 102, "subject": "榜单第二篇新文章", "publish_time": "2026-10-18 11:00:00"}]}}),
        }
        rows, evidence, _ = collect(pub, documents)
        self.assertEqual([row["url"].rsplit("/", 1)[1] for row in rows], ["103", "102", "101"])
        self.assertNotIn("hotRank", rows[0])
        self.assertEqual([row["hotRank"] for row in rows[1:]], [2, 1])
        for row in rows[1:]:
            self.assertEqual(row["hotSource"], HOT_URL)
            self.assertEqual(row["hotLabel"], "南方周末热门文章")
            self.assertEqual(row["hotCheckedAt"], TODAY)
            self.assertNotIn("hotScore", row)
        self.assertEqual(evidence["hotStatus"], "ok")
        self.assertEqual(evidence["hotLists"][0]["asOf"], TODAY)
        self.assertEqual(evidence["hotLists"][0]["url"], HOT_URL)

    def test_southern_weekly_invalid_hot_response_fails_closed(self):
        pub = publication("infzm", "https://www.infzm.com/")
        for invalid in ({"code": 403, "data": {"hot_contents": []}},
                        {"code": 200, "data": {"hot_contents": {}}}):
            with self.subTest(payload=invalid), self.assertRaises(ValueError):
                collect(pub, {HOT_URL: json.dumps(invalid)})

    def test_nfpeople_explicit_date_and_official_host_only(self):
        pub = publication("nfpeople", "https://www.nfpeople.com/")
        good = "https://www.nfpeople.com/article/123"
        documents = {
            pub["url"]: ('<a href="/article/123">列表准确题名</a>'
                '<a href="https://www.nfpeople.com.evil.invalid/article/124">冒名站点文章</a>'
                '<a href="https://www.nfpeople.com@evil.invalid/article/125">凭据伪装文章</a>'
                '<a href="javascript:alert(1)">脚本伪装文章</a>'),
            good: '<h1>文章准确题名</h1><p class="source">稿源：南方人物周刊 日期：2026-10-05</p>',
        }
        rows, _, requested = collect(pub, documents)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "文章准确题名")
        self.assertEqual(rows[0]["publishedAt"], "2026-10-05")
        self.assertEqual(set(requested), {pub["url"], good})

    def test_restricted_detail_retains_verified_list_title_without_date(self):
        pub = publication("nfpeople", "https://www.nfpeople.com/")
        url = "https://www.nfpeople.com/article/123"
        rows, evidence, _ = collect(pub, {
            pub["url"]: '<a href="/article/123">已由列表核实的文章</a>',
            url: OSError("HTTP 403"),
        })
        self.assertEqual(rows[0]["title"], "已由列表核实的文章")
        self.assertIsNone(rows[0]["publishedAt"])
        self.assertEqual(evidence["details"][0]["status"], "unavailable")

    def test_caijing_issue_dates_and_logo_are_not_article_metadata(self):
        pub = publication("caijing", "https://magazine.caijing.com.cn/")
        issue = "https://magazine.caijing.com.cn/caijingmagazine/2026/259/"
        story = "https://magazine.caijing.com.cn/20261012/5187289.shtml"
        undated = "https://magazine.caijing.com.cn/20261012/5187290.shtml"
        documents = {
            pub["url"]: ('<a href="http://magazine.caijing.com.cn/caijingmagazine/2026/259/">当期</a>'
                         '<a href="//magazine.caijing.com.cn/caijingmagazine/2026/259/">重复当期</a>'),
            issue: ('<div>出版日期：2026-10-12</div>'
                '<a href="http://magazine.caijing.com.cn/20261012/5187289.shtml">目录的精确标题</a>'
                '<a href="/20261012/5187290.shtml">文章发布日期未知</a>'),
            story: ('<h1>财经网品牌标志</h1>'
                '<meta property="og:title" content="目录的精确标题_频道_财经网">'
                '<span class="news_date">2026-10-11</span>'),
            undated: '<h1>财经网品牌标志</h1><p>本期出版日期：2026-10-12</p>',
        }
        rows, _, requested = collect(pub, documents)
        by_url = {row["url"]: row for row in rows}
        self.assertEqual(by_url[story]["title"], "目录的精确标题")
        self.assertEqual(by_url[story]["publishedAt"], "2026-10-11")
        self.assertIsNone(by_url[undated]["publishedAt"])
        self.assertEqual(requested.count(issue), 1)
        self.assertTrue(all(url.startswith("https://") for url in requested))

    def test_caixin_template_fragments_are_omitted_and_url_date_not_guessed(self):
        pub = publication("caixin", "https://weekly.caixin.com/")
        good = "https://weekly.caixin.com/2026-10-17/123456.html"
        bad = "https://weekly.caixin.com/2026-10-18/123457.html"
        documents = {
            pub["url"]: ('<a href="/2026-10-17/123456.html">准确的列表标题</a>'
                         '<a href="/2026-10-18/123457.html">{{错误模板标题</a>'),
            good: '<h1>{{模板变量</h1><p>2026年第40期 出版日期：2026-10-19</p>',
            bad: '<h1>{{错误模板标题</h1>',
        }
        rows, _, _ = collect(pub, documents)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "准确的列表标题")
        self.assertIsNone(rows[0]["publishedAt"])

    def test_redirect_to_unapproved_host_is_rejected(self):
        pub = publication("nfpeople", "https://www.nfpeople.com/")
        with self.assertRaises(ValueError):
            collect(pub, {pub["url"]: ("<html>redirect</html>", "https://evil.invalid/")})

    def test_empty_or_navigation_only_sources_raise(self):
        pub = publication("nfpeople", "https://www.nfpeople.com/")
        for body in ("", "<a href='/about'>关于我们</a>", "<h1>访问受限</h1>"):
            with self.subTest(body=body), self.assertRaises(ValueError):
                collect(pub, {pub["url"]: body})

    def test_root_failure_keeps_previous_article_rank_and_source_date(self):
        pub = publication("infzm", "https://www.infzm.com/")
        old = [{"publication": "infzm", "title": "之前核实的热榜文章",
                "url": "https://www.infzm.com/contents/101", "publishedAt": "2026-10-13",
                "checkedAt": "2026-10-18", "hotRank": 1, "hotSource": HOT_URL,
                "hotLabel": "南方周末热门文章", "hotCheckedAt": "2026-10-18"}]
        original = deepcopy(old)
        with patch.object(refresh, "collect", side_effect=OSError("HTTP 403")):
            pubs, rows, report = refresh.refresh([pub], old, TODAY, 1)
        self.assertEqual(rows, original)
        self.assertEqual(pubs[0]["lastSuccessAt"], "2026-10-18")
        self.assertEqual(report["sources"][0]["status"], "unavailable")

    def test_root_new_hot_list_removes_old_membership_but_keeps_article(self):
        pub = publication("infzm", "https://www.infzm.com/")
        old = [{"publication": "infzm", "title": "退出热榜的旧文",
                "url": "https://www.infzm.com/contents/101", "publishedAt": "2026-10-13",
                "hotRank": 1, "hotSource": HOT_URL, "hotLabel": "南方周末热门文章",
                "hotCheckedAt": "2026-10-18"}]
        incoming = [{"publication": "infzm", "title": "今天新上榜文章",
                     "url": "https://www.infzm.com/contents/102", "publishedAt": "2026-10-14",
                     "hotRank": 1, "hotSource": HOT_URL, "hotLabel": "南方周末热门文章",
                     "hotCheckedAt": TODAY}]
        with patch.object(refresh, "collect", return_value=(incoming, {"hotStatus": "ok"})):
            _, rows, _ = refresh.refresh([pub], old, TODAY, 1)
        old_row = next(row for row in rows if row["url"].endswith("/101"))
        self.assertEqual(old_row["publishedAt"], "2026-10-13")
        self.assertFalse(any(key.startswith("hot") for key in old_row))

    def test_root_detail_failure_does_not_erase_known_publication_date(self):
        url = "https://weekly.caixin.com/2026-10-17/123456.html"
        old = [{"publication": "caixin", "title": "之前核实的文章", "url": url,
                "publishedAt": "2026-10-16", "summary": "已保存的阅读提示"}]
        incoming = [{"publication": "caixin", "title": "之前核实的文章", "url": url,
                     "publishedAt": None, "summary": "", "checkedAt": TODAY}]
        rows = refresh.merge_articles(old, incoming, "caixin")
        self.assertEqual(rows[0]["publishedAt"], "2026-10-16")
        self.assertEqual(rows[0]["summary"], "已保存的阅读提示")


if __name__ == "__main__":
    unittest.main(verbosity=2)
