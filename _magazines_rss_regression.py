"""Offline checks for official feed dates, URL policy and named popularity lists.

Fixtures retain structures observed in the publishers' actual RSS/Atom and
homepage responses. No network access, credentials or cached article text is
required. Run: python _magazines_rss_regression.py
"""
from __future__ import annotations

import unittest

import _magazines_rss as rss
from _refresh_magazines import article, official_url, parse_html


TODAY = "2026-10-19"
BASE = "https://example.test"


def publication(host="example.test", identifier="fixture"):
    return {"id": identifier, "hosts": [host], "feedUrl": "https://" + host + "/feed"}


def feed(items, base=BASE):
    return "<rss><channel>" + "".join(
        "<item><title>%s</title><link>%s%s</link>%s</item>" %
        (title, base, path, "<pubDate>%s</pubDate>" % stamp if stamp else "")
        for title, path, stamp in items) + "</channel></rss>"


def quanta_hot(title="A verified popular article", path="/actual-story-20260101/"):
    return ("<a class='card-list__title' href='https://evil.test/outside'>Outside</a>"
            "<aside><div class='popular '><p>Past Week</p><h3>Most Read Articles</h3>"
            "<a class='card-list__image' href='https://www.quantamagazine.org/image-only/'>"
            "Image only</a><a class='card-list__title extra' "
            "href='https://www.quantamagazine.org" + path + "'><h4>" + title +
            "</h4></a></div></aside><a class='card-list__title' "
            "href='https://www.quantamagazine.org/outside-after/'>Outside after</a>")


class FeedRegressions(unittest.TestCase):
    def collect(self, pub, responses, limit=60):
        calls = []

        def fetch(url, hosts, timeout):
            calls.append(url)
            value = responses[url]
            if isinstance(value, Exception):
                raise value
            return value, url

        rows, evidence = rss.collect(pub, TODAY, 1, fetch, official_url, article,
                                     parse_html, limit=limit)
        return rows, evidence, calls

    def test_rss2_rfc2822_keeps_source_calendar_day_and_title(self):
        pub = publication()
        rows, _, _ = self.collect(pub, {pub["feedUrl"]: feed([
            ("Science &amp; society", "/article", "Sun, 18 Oct 2026 23:50:00 -0400")])})
        self.assertEqual(rows[0]["title"], "Science & society")
        self.assertEqual(rows[0]["publishedAt"], "2026-10-18")

    def test_atom_published_is_used_and_tracking_removed(self):
        pub = publication()
        xml = '''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <title type="html">An &lt;em&gt;Atom&lt;/em&gt; article</title>
        <link rel="self" href="https://evil.test/self"/>
        <link rel="alternate" href="https://example.test/story?id=3&amp;utm_source=feed"/>
        <published>2026-10-18T23:55:00-04:00</published>
        <updated>2026-10-19T10:00:00Z</updated></entry></feed>'''
        rows, _, _ = self.collect(pub, {pub["feedUrl"]: xml})
        self.assertEqual(rows[0]["title"], "An Atom article")
        self.assertEqual(rows[0]["publishedAt"], "2026-10-18")
        self.assertEqual(rows[0]["url"], BASE + "/story?id=3")

    def test_rdf_rss1_reads_namespaced_title_link_and_dc_date(self):
        pub = publication()
        xml = '''<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/">
        <item rdf:about="https://example.test/nature"><title>A Nature-style item</title>
        <link>https://example.test/nature</link><dc:date>2026-10-16</dc:date>
        </item></rdf:RDF>'''
        rows, evidence, _ = self.collect(pub, {pub["feedUrl"]: xml})
        self.assertEqual(rows[0]["publishedAt"], "2026-10-16")
        self.assertEqual(evidence["details"][0]["format"], "RSS1/RDF")

    def test_atom_updated_and_date_in_url_are_not_publication_dates(self):
        pub = publication()
        xml = '''<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <title>Publication date is unknown</title>
        <link href="https://example.test/article-20261018/"/>
        <updated>2026-10-19T09:00:00Z</updated></entry></feed>'''
        rows, _, _ = self.collect(pub, {pub["feedUrl"]: xml})
        self.assertIsNone(rows[0]["publishedAt"])

    def test_future_article_and_foreign_host_are_excluded(self):
        pub = publication()
        xml = feed([("A future article", "/future", "2026-10-20"),
                    ("A valid article", "/valid", "2026-10-18")])
        xml = xml.replace("</channel>", "<item><title>A foreign article</title>"
                          "<link>https://evil.test/escape</link></item></channel>")
        rows, _, _ = self.collect(pub, {pub["feedUrl"]: xml})
        self.assertEqual([row["url"] for row in rows], [BASE + "/valid"])

    def test_multiple_feeds_partial_failure_and_tracking_deduplication(self):
        pub = publication()
        pub["feedUrls"] = [BASE + "/feed2", BASE + "/failure", pub["feedUrl"]]
        rows, evidence, calls = self.collect(pub, {
            pub["feedUrl"]: feed([("One real article", "/same?utm_source=one", None)]),
            BASE + "/feed2": feed([("One real article", "/same?utm_source=two", "2026-10-16")]),
            BASE + "/failure": TimeoutError("source timed out")})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["publishedAt"], "2026-10-16")
        self.assertEqual(len(calls), 3)
        self.assertTrue(any(item["status"] == "unavailable" for item in evidence["details"]))

    def test_all_sources_failed_raises_so_caller_can_keep_old_articles(self):
        pub = publication()
        with self.assertRaisesRegex(ValueError, "No verified RSS"):
            self.collect(pub, {pub["feedUrl"]: TimeoutError("offline")})

    def test_dtd_or_entity_is_rejected(self):
        pub = publication()
        xml = '<!DOCTYPE rss [<!ENTITY fake "fake title">]><rss><channel/></rss>'
        with self.assertRaisesRegex(ValueError, "unsupported DTD"):
            self.collect(pub, {pub["feedUrl"]: xml})

    def test_unconfigured_feed_host_is_never_fetched(self):
        pub = publication()
        pub["feedUrl"] = "https://evil.test/feed"
        with self.assertRaisesRegex(ValueError, "configured HTTPS hosts"):
            self.collect(pub, {})

    def test_quanta_official_sidebar_only_and_no_slug_date_guess(self):
        pub = publication("www.quantamagazine.org", "quanta")
        pub.pop("feedUrl")
        pub["hotFeedUrl"] = "https://www.quantamagazine.org/"
        rows, evidence, _ = self.collect(pub, {pub["hotFeedUrl"]: quanta_hot()})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["hotRank"], 1)
        self.assertEqual(rows[0]["hotCheckedAt"], TODAY)
        self.assertIsNone(rows[0]["publishedAt"])
        self.assertEqual(evidence["hotStatus"], "ok")
        self.assertEqual(evidence["hotLists"][0]["window"], "Past Week")

    def test_successful_feed_survives_failed_hot_list_without_false_hot_stamp(self):
        pub = publication("www.quantamagazine.org", "quanta")
        pub["hotFeedUrl"] = "https://www.quantamagazine.org/"
        rows, evidence, _ = self.collect(pub, {
            pub["feedUrl"]: feed([("Actual feed story", "/story", "2026-10-18")],
                                 base=pub["hotFeedUrl"].rstrip("/")),
            pub["hotFeedUrl"]: "<main>No verified official ranking labels</main>"})
        self.assertEqual(evidence["hotStatus"], "unavailable")
        self.assertEqual(evidence["hotLists"], [])
        self.assertNotIn("hotCheckedAt", rows[0])

    def test_missing_quanta_time_window_is_not_accepted_as_verified_list(self):
        pub = publication("www.quantamagazine.org", "quanta")
        pub.pop("feedUrl")
        pub["hotFeedUrl"] = "https://www.quantamagazine.org/"
        with self.assertRaisesRegex(ValueError, "Past Week"):
            self.collect(pub, {pub["hotFeedUrl"]: quanta_hot().replace("Past Week", "Elsewhere")})

    def test_hot_entry_keeps_known_rss_date_and_has_explicit_source(self):
        pub = publication("www.quantamagazine.org", "quanta")
        pub["hotFeedUrl"] = "https://www.quantamagazine.org/"
        rows, evidence, _ = self.collect(pub, {
            pub["feedUrl"]: feed([("Original official title", "/actual-story-20260101/", "2026-10-16")],
                                 base=pub["hotFeedUrl"].rstrip("/")),
            pub["hotFeedUrl"]: quanta_hot()})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["publishedAt"], "2026-10-16")
        self.assertEqual(rows[0]["hotSource"], pub["hotFeedUrl"])
        self.assertEqual(evidence["hotLists"][0]["items"][0]["publishedAt"], "2026-10-16")

    def test_sciencenews_trending_uses_displayed_article_time(self):
        pub = publication("www.sciencenews.org", "sciencenews")
        pub.pop("feedUrl")
        pub["hotFeedUrl"] = "https://www.sciencenews.org/"
        text = '''<section class="trending-stories__wrapper___-7tOu">
        <h2>Trending Stories<span aria-hidden="true"></span></h2><ol>
        <li><h3 class="carousel__title"><a href="https://www.sciencenews.org/article/old-story">
        An old but still trending article</a></h3><time datetime="2025-04-11T10:00:00-04:00">
        April 11, 2025</time></li></ol></section>'''
        rows, evidence, _ = self.collect(pub, {pub["hotFeedUrl"]: text})
        self.assertEqual(rows[0]["publishedAt"], "2025-04-11")
        self.assertEqual(rows[0]["hotLabel"], "Trending Stories")
        self.assertIsNone(evidence["hotLists"][0]["window"])

    def test_limit_preserves_hot_entry_over_unranked_recent_items(self):
        pub = publication("www.quantamagazine.org", "quanta")
        pub["hotFeedUrl"] = "https://www.quantamagazine.org/"
        rows, evidence, _ = self.collect(pub, {
            pub["feedUrl"]: feed([("A recent unranked article", "/recent", "2026-10-18")],
                                 base=pub["hotFeedUrl"].rstrip("/")),
            pub["hotFeedUrl"]: quanta_hot()}, limit=1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["hotRank"], 1)
        self.assertEqual(len(evidence["hotLists"][0]["items"]), 1)

    def test_invalid_explicit_date_is_unknown_not_replaced_with_check_date(self):
        pub = publication()
        rows, _, _ = self.collect(pub, {pub["feedUrl"]: feed([
            ("Unknown publication date", "/date-20261018", "2026-02-30")])})
        self.assertIsNone(rows[0]["publishedAt"])
        self.assertEqual(rows[0]["checkedAt"], TODAY)


if __name__ == "__main__":
    unittest.main(verbosity=2)
