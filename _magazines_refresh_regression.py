"""Offline regressions for real magazine metadata and refresh failure modes.

Run: python _magazines_refresh_regression.py
No publisher is contacted. The small Lifeweek fixture preserves the important
structure observed on its real pages: the h1 is branding, the title is the story,
and the displayed issue date is not an article publication timestamp.
"""
from __future__ import annotations

import contextlib
from copy import deepcopy
from email.message import Message
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.request import Request


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("magazine_refresh_under_test", ROOT / "_refresh_magazines.py")
refresh_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh_module)

DAY_ONE = "2026-10-19"
DAY_TWO = "2026-10-20"
DAY_THREE = "2026-10-21"


def publication(identifier="lifeweek"):
    if identifier == "yimagazine":
        return {
            "id": identifier,
            "name": "第一财经",
            "hosts": ["www.yicai.com"],
            "url": "https://www.yicai.com/vip/product/55/",
            "feedUrl": "https://www.yicai.com/api/ajax/getlistbypid?page=1&id=55&type=3",
            "note": "原《第一财经周刊》，现为月刊；全文可能需要订阅。",
        }
    return {
        "id": identifier,
        "name": "三联生活周刊",
        "hosts": ["www.lifeweek.com.cn"],
        "url": "https://www.lifeweek.com.cn/magazine?magazineid=1",
        "feedUrl": "https://www.lifeweek.com.cn/magazine?magazineid=1",
        "note": "期刊日期与单篇日期分开，数字刊全文可能需要订阅。",
    }


def old_article(identifier="lifeweek"):
    return {
        "publication": identifier,
        "title": "观察、理解与控制",
        "url": "https://www.lifeweek.com.cn/article/274426",
        "publishedAt": "2026-10-16",
        "checkedAt": "2026-10-18",
        "summary": "独立撰写的阅读方向应在刷新时保留。",
    }


def source_file(publications, articles):
    return "\n".join(
        "window.%s = %s;" % (name, json.dumps(value, ensure_ascii=False))
        for name, value in (
            ("MAGAZINES_CHECKED", DAY_ONE),
            ("MAGAZINES", publications),
            ("MAGAZINE_ARTICLES", articles),
        )
    ) + "\n"


class FakeResponse:
    def __init__(self, body=b"[]", status=200, url="https://www.yicai.com/list"):
        self.status = status
        self.url = url
        self.body = body
        self.headers = Message()
        self.headers["Content-Type"] = "application/json; charset=utf-8"
        self.requested_size = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def geturl(self):
        return self.url

    def read(self, size):
        self.requested_size = size
        return self.body[:size]


class MagazineRefreshRegressions(unittest.TestCase):
    def test_invalid_short_feed_label_does_not_discard_valid_magazine_stories(self):
        pub = publication("yimagazine")
        response = json.dumps([
            {"ChannelName": "第一财经杂志", "url": "/news/123.html", "NewsTitle": "目录", "CreateDate": DAY_ONE},
            {"ChannelName": "第一财经杂志", "url": "/news/124.html", "NewsTitle": "一篇可核实的商业文章", "CreateDate": DAY_ONE},
            {"ChannelName": "其他频道", "url": "/news/125.html", "NewsTitle": "其他频道不能混入", "CreateDate": DAY_ONE}
        ], ensure_ascii=False)
        with patch.object(refresh_module, "fetch_text", return_value=(response, pub["feedUrl"])):
            rows, proof = refresh_module.collect(pub, DAY_ONE, 1)
        self.assertEqual([row["title"] for row in rows], ["一篇可核实的商业文章"])
        self.assertEqual(rows[0]["publishedAt"], DAY_ONE)
        self.assertEqual(len(proof["details"]), 1)

    def setUp(self):
        # A forgotten network mock fails locally instead of contacting a source.
        self.network_guard = patch.object(
            refresh_module, "build_opener", side_effect=AssertionError("Network is forbidden in this regression")
        )
        self.network_guard.start()
        self.addCleanup(self.network_guard.stop)

    def test_lifeweek_logo_heading_does_not_replace_story_or_invent_date(self):
        pub = publication()
        url = "https://www.lifeweek.com.cn/article/274426"
        html = """<!doctype html><html><head>
          <title>观察、理解与控制-三联生活网</title></head><body>
          <h1>三联生活周刊</h1><div>2026年10月19日 总第1411期</div>
          <script>window.__NUXT__={zhuanlan:{pubTime:"2026-10-19"}};</script>
          </body></html>"""
        with patch.object(refresh_module, "fetch_text", return_value=(html, url)):
            title, published, resolved, _ = refresh_module.detail_metadata(url, pub, 1, allow_title=True)
        self.assertEqual(title, "观察、理解与控制")
        self.assertIsNone(published)
        self.assertEqual(resolved, url)

    def test_lifeweek_selects_only_active_publication_ids(self):
        pub = publication()
        listing = """<script>
          X.rltArticleList=[{id:999,title:"另一本刊物"}];
          R.rltArticleList=[{id:274426,title:S},{id:274427,title:T}];
          var state={activePeriodicalRecommend:R};
          </script>"""
        titles = {"274426": "观察、理解与控制", "274427": "什么才是真正重要的科学"}
        visited = []

        def fetch(url, _hosts, _timeout):
            visited.append(url)
            if url == pub["feedUrl"]:
                return listing, url
            identifier = url.rsplit("/", 1)[-1]
            if identifier not in titles:
                raise AssertionError("Mixed publication article was requested")
            return "<title>%s-三联生活网</title><h1>三联生活周刊</h1>" % titles[identifier], url

        with patch.object(refresh_module, "fetch_text", side_effect=fetch):
            rows, _ = refresh_module.collect(pub, DAY_ONE, 1)
        self.assertEqual([row["title"] for row in rows], list(titles.values()))
        self.assertTrue(all(row["publishedAt"] is None for row in rows))
        self.assertFalse(any("999" in url for url in visited))

    def test_lifeweek_branding_page_cannot_be_a_verified_story(self):
        pub = publication()
        url = "https://www.lifeweek.com.cn/article/274426"
        for html in ("<title>三联生活周刊-三联生活网</title><h1>三联生活周刊</h1>",
                     "<title>访问验证</title><h1>三联生活周刊</h1>"):
            with self.subTest(html=html), patch.object(refresh_module, "fetch_text", return_value=(html, url)):
                with self.assertRaises(ValueError):
                    refresh_module.detail_metadata(url, pub, 1, allow_title=True)

    def test_urls_require_https_exact_host_and_no_credentials_or_custom_port(self):
        hosts = ["www.yicai.com"]
        unsafe = (
            "http://www.yicai.com/x",
            "https://www.yicai.com.evil.example/x",
            "https://evil.example/x",
            "https://user@www.yicai.com/x",
            "https://user:secret@www.yicai.com/x",
            "https://www.yicai.com:8443/x",
            "javascript:alert(1)",
            "file:///C:/private.txt",
        )
        for url in unsafe:
            with self.subTest(url=url), self.assertRaises(ValueError):
                refresh_module.official_url(url, hosts)
        self.assertEqual(
            refresh_module.official_url("/vip/news/103394820.html#section", hosts, "https://www.yicai.com/"),
            "https://www.yicai.com/vip/news/103394820.html",
        )

    def test_redirect_cannot_leave_publication_allowlist(self):
        handler = refresh_module.OfficialRedirect(["www.yicai.com"])
        request = Request("https://www.yicai.com/source")
        with self.assertRaises(ValueError):
            handler.redirect_request(request, None, 302, "Found", {}, "https://evil.example/source")

    def test_fetch_passes_timeout_and_bounds_metadata_read(self):
        response = FakeResponse()
        opener = Mock()
        opener.open.return_value = response
        with patch.object(refresh_module, "build_opener", return_value=opener):
            text, final = refresh_module.fetch_text(response.url, ["www.yicai.com"], 2.5)
        self.assertEqual(text, "[]")
        self.assertEqual(final, response.url)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 2.5)
        self.assertEqual(response.requested_size, refresh_module.MAX_BYTES + 1)

    def test_empty_success_http_response_is_not_verified(self):
        for response in (FakeResponse(body=b""), FakeResponse(status=204)):
            opener = Mock()
            opener.open.return_value = response
            with self.subTest(status=response.status), patch.object(refresh_module, "build_opener", return_value=opener):
                with self.assertRaises(ValueError):
                    refresh_module.fetch_text(response.url, ["www.yicai.com"], 1)

    def test_source_failure_preserves_articles_and_original_dates(self):
        pubs = [publication(), publication("yimagazine")]
        previous = [old_article(), {**old_article("yimagazine"),
            "url": "https://www.yicai.com/vip/news/103394820.html", "publishedAt": None}]
        original = deepcopy(previous)
        with patch.object(refresh_module, "collect", side_effect=TimeoutError("Source timeout")):
            updated, retained, report = refresh_module.refresh(pubs, previous, DAY_TWO, 1)
        self.assertEqual(previous, original)
        self.assertEqual(retained, original)
        self.assertTrue(all(row["status"] == "unavailable" for row in updated))
        self.assertTrue(all(row["articles"] == [] for row in report["sources"]))

    def test_empty_json_list_preserves_old_articles(self):
        pub = publication("yimagazine")
        previous = [{**old_article("yimagazine"), "url": "https://www.yicai.com/vip/news/103394820.html"}]
        with patch.object(refresh_module, "fetch_text", return_value=("[]", pub["feedUrl"])):
            _, retained, report = refresh_module.refresh([pub], previous, DAY_TWO, 1)
        self.assertEqual(retained, previous)
        self.assertEqual(report["sources"][0]["status"], "unavailable")

    def test_unqualified_or_invalid_dates_are_absent(self):
        for value in ("10-19", "2026-02-30", "昨天", "/2026/1019", "", None):
            with self.subTest(value=value):
                self.assertIsNone(refresh_module.explicit_date(value))
        self.assertEqual(refresh_module.explicit_date("2026-10-15T17:30:00+08:00"), "2026-10-15")

    def test_inline_script_terminator_is_escaped_and_json_roundtrips(self):
        pubs = [publication()]
        payload = [{**old_article(), "title": '新闻 </ScRiPt><script>alert("x")</script>',
                    "summary": "导读也可能含 </SCRIPT> 与 < 比较符。"}]
        rendered = refresh_module.write_assignments(source_file(pubs, []), {"MAGAZINE_ARTICLES": payload})
        self.assertIsNone(re.search(r"</script", rendered, re.I))
        self.assertIn("\\u003c", rendered)
        decoded, _ = refresh_module.read_assignment(rendered, "MAGAZINE_ARTICLES")
        self.assertEqual(decoded, payload)

    def test_success_then_repeated_failures_preserve_independent_evidence(self):
        pubs = [publication()]
        incoming = [{**old_article(), "checkedAt": DAY_ONE}]
        evidence = {"listUrl": pubs[0]["feedUrl"], "articles": deepcopy(incoming), "details": []}
        with patch.object(refresh_module, "collect", return_value=(incoming, evidence)):
            updated, articles, first = refresh_module.refresh(pubs, [], DAY_ONE, 1)
        with patch.object(refresh_module, "collect", side_effect=TimeoutError("Offline")):
            updated, retained, second = refresh_module.refresh(updated, articles, DAY_TWO, 1, prior_report=first)
            _, again, third = refresh_module.refresh(updated, retained, DAY_THREE, 1, prior_report=second)
        self.assertEqual(again, articles)
        for report in (second, third):
            source = report["sources"][0]
            self.assertEqual(source["status"], "unavailable")
            self.assertEqual(source["articles"], [])
            self.assertEqual(len(source["retainedArticles"]), 1)
            saved = source["retainedArticles"][0]
            self.assertEqual(saved["checkedAt"], DAY_ONE)
            self.assertEqual(saved["publishedAt"], incoming[0]["publishedAt"])

    def test_changed_data_identity_cannot_self_certify_from_old_report(self):
        pub = publication()
        verified = old_article()
        prior = {"sources": [{"publication": pub["id"], "status": "ok",
                              "articles": [verified], "retainedArticles": []}]}
        mutations = (
            {"publishedAt": "2026-10-19"},
            {"title": "未经来源核实的替换标题"},
            {"url": "https://www.lifeweek.com.cn/article/999999"},
        )
        for changed in mutations:
            altered = {**verified, **changed}
            with self.subTest(changed=changed), patch.object(refresh_module, "collect", side_effect=TimeoutError("Offline")):
                _, retained, report = refresh_module.refresh([pub], [altered], DAY_TWO, 1, prior_report=prior)
            self.assertEqual(retained, [altered], "A failed fetch must not silently edit the data file")
            self.assertEqual(report["sources"][0]["retainedArticles"], [],
                             "Changed title/URL/date has no matching independent source evidence")

    def test_data_without_prior_source_report_is_not_evidence(self):
        pub = publication()
        old = old_article()
        with patch.object(refresh_module, "collect", side_effect=TimeoutError("Offline")):
            _, retained, report = refresh_module.refresh([pub], [old], DAY_TWO, 1)
        self.assertEqual(retained, [old])
        self.assertEqual(report["sources"][0]["retainedArticles"], [])

    def test_editorial_access_note_survives_failure_and_recovery(self):
        pub = publication()
        previous = [old_article()]
        with patch.object(refresh_module, "collect", side_effect=TimeoutError("Offline")):
            failed, _, _ = refresh_module.refresh([pub], previous, DAY_TWO, 1)
        incoming = [{**old_article(), "checkedAt": DAY_THREE}]
        with patch.object(refresh_module, "collect", return_value=(incoming, {"articles": incoming, "details": []})):
            recovered, _, _ = refresh_module.refresh(failed, previous, DAY_THREE, 1)
        self.assertEqual(recovered[0]["note"], pub["note"])
        self.assertEqual(recovered[0]["sourceNote"], pub["note"])

    def test_dry_run_keeps_data_and_report_bytes_and_mtimes(self):
        pub = publication()
        previous = [old_article()]
        prior = {"sources": [{"publication": pub["id"], "status": "ok",
                              "articles": previous, "retainedArticles": []}]}
        with tempfile.TemporaryDirectory(prefix="magazines-offline-regression-") as folder:
            data_path = Path(folder) / "magazines.js"
            report_path = Path(folder) / "report.json"
            data_path.write_text(source_file([pub], previous), encoding="utf-8")
            report_path.write_text(json.dumps(prior, ensure_ascii=False), encoding="utf-8")
            before = {path.name: (path.read_bytes(), path.stat().st_mtime_ns)
                      for path in (data_path, report_path)}
            output = io.StringIO()
            argv = ["_refresh_magazines.py", "--dry-run", "--today", DAY_TWO,
                    "--data", str(data_path), "--report", str(report_path), "--timeout", "1"]
            with patch.object(sys, "argv", argv), patch.object(refresh_module, "collect", side_effect=TimeoutError("Offline")), \
                    patch.object(refresh_module, "atomic_write") as write, contextlib.redirect_stdout(output):
                status = refresh_module.main()
            self.assertEqual(status, 1)
            write.assert_not_called()
            report = json.loads(output.getvalue())
            self.assertEqual(report["sources"][0]["status"], "unavailable")
            self.assertEqual(report["sources"][0]["retainedArticles"][0]["checkedAt"], previous[0]["checkedAt"])
            after = {path.name: (path.read_bytes(), path.stat().st_mtime_ns)
                     for path in (data_path, report_path)}
            self.assertEqual(after, before)
            self.assertEqual({path.name for path in Path(folder).iterdir()}, set(before))


if __name__ == "__main__":
    unittest.main(verbosity=2)
