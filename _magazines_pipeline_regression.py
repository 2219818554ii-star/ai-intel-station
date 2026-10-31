"""Offline regressions for curation, parallel refresh and retained hot evidence.

The real RSS collector and the main refresh/merge functions run together; only
network fetches are replaced by small official-source-shaped fixture responses.
Run: python _magazines_pipeline_regression.py
"""
from __future__ import annotations

from copy import deepcopy
import unittest
from unittest.mock import patch

import _refresh_magazines as refresh_module


DAY_ONE = "2026-10-19"
DAY_TWO = "2026-10-20"
DAY_THREE = "2026-10-21"
HOT_FIELDS = ("hotRank", "hotSource", "hotLabel", "hotCheckedAt")


def publication(identifier="quanta", host="www.quantamagazine.org", *, hot=True):
    base = "https://" + host
    result = {"id": identifier, "name": identifier, "parser": "rss", "hosts": [host],
              "url": base + "/", "feedUrl": base + "/" + identifier + "/feed",
              "note": "Official source; access follows the publisher."}
    if hot:
        result["hotFeedUrl"] = base + "/"
    return result


def feed(host, items):
    return "<rss><channel>" + "".join(
        "<item><title>%s</title><link>https://%s%s</link>%s</item>" %
        (title, host, path, "<pubDate>%s</pubDate>" % stamp if stamp else "")
        for title, path, stamp in items) + "</channel></rss>"


def popular(path, title):
    return ("<aside><div class='popular '><p>Past Week</p><h3>Most Read Articles</h3>"
            "<a class='card-list__title' href='https://www.quantamagazine.org" + path +
            "'><h4>" + title + "</h4></a></div></aside>")


def old_article(identifier, path, title="A previously verified article"):
    return {"publication": identifier, "title": title,
            "url": "https://example.test" + path, "publishedAt": "2026-10-16",
            "checkedAt": "2026-10-18", "summary": "Preserve the independent reading note."}


class PipelineRegressions(unittest.TestCase):
    def test_reading_questions_fill_missing_notes_without_changing_source_facts(self):
        rows = [old_article("one", "/authored"),
                {**old_article("one", "/battery", "A new battery electrode"), "summary": ""},
                {**old_article("one", "/unknown", "An ambiguous headline"), "summary": "", "publishedAt": None}]
        before = deepcopy(rows)
        count = refresh_module.ensure_reading_guides(rows, [{"id": "one", "category": "科学新知"}])
        self.assertEqual(count, 2)
        self.assertEqual(rows[0], before[0])
        for index in (1, 2):
            self.assertEqual({k: v for k, v in rows[index].items() if k not in ("summary", "summaryBasis")},
                             {k: v for k, v in before[index].items() if k != "summary"})
            self.assertTrue(rows[index]["summary"].startswith("据标题的阅读切入点："))
            self.assertEqual(rows[index]["summaryBasis"], "title-and-publication")
        self.assertIn("循环", rows[1]["summary"])
        self.assertIsNone(rows[2]["publishedAt"])
        self.assertEqual(refresh_module.ensure_reading_guides(rows, []), 0)

    def test_changed_verified_title_rebuilds_only_automatic_reading_questions(self):
        old = {**old_article("one", "/known", "An earlier battery headline"), "summary": ""}
        refresh_module.ensure_reading_guides([old], [{"id": "one", "category": "科学新知"}])
        incoming = {**old, "title": "A new quantum experiment", "publishedAt": DAY_TWO}
        merged = refresh_module.merge_articles([old], [incoming], "one")
        refresh_module.ensure_reading_guides(merged, [{"id": "one", "category": "科学新知"}])
        self.assertIn(incoming["title"], merged[0]["summary"])
        self.assertNotIn(old["title"], merged[0]["summary"])
        self.assertEqual(merged[0]["publishedAt"], DAY_TWO)

    def run_refresh(self, publications, previous, today, responses, prior=None, workers=1):
        def fake_fetch(url, hosts, timeout):
            value = responses[url]
            if isinstance(value, Exception):
                raise value
            return value, url

        with patch.object(refresh_module, "fetch_text", side_effect=fake_fetch) as mocked:
            output = refresh_module.refresh(publications, previous, today, 1,
                                            prior_report=prior, workers=workers)
        self.assertGreater(mocked.call_count, 0)
        return output

    def successful_hot(self):
        pub = publication()
        responses = {
            pub["feedUrl"]: feed("www.quantamagazine.org", [
                ("A formerly popular story", "/formerly/", "2026-10-16"),
                ("A currently popular story", "/currently/", "2026-10-17")]),
            pub["hotFeedUrl"]: popular("/formerly/", "A formerly popular story"),
        }
        return pub, responses, self.run_refresh([pub], [], DAY_ONE, responses)

    def test_editorial_matches_exact_publication_url_and_title_only(self):
        target = old_article("one", "/story", "Exact official title")
        rows = [target, {**target, "publication": "other"},
                {**target, "url": "https://example.test/different"},
                {**target, "title": "Changed official title"}]
        config = {"articles": [{"publication": "one", "url": target["url"],
                                "title": target["title"], "reason": "A specific reading angle.",
                                "priority": 3, "summary": "Must not overwrite the article.",
                                "publishedAt": DAY_ONE, "hotRank": 1}]}
        before = deepcopy(rows)
        actual = refresh_module.apply_editorial(rows, config)
        self.assertEqual(actual[0]["featuredReason"], "A specific reading angle.")
        self.assertEqual(actual[0]["featuredPriority"], 3)
        for index, row in enumerate(actual):
            self.assertEqual({key: value for key, value in row.items()
                              if key not in ("featuredReason", "featuredPriority")}, before[index])
        self.assertTrue(all("featuredReason" not in row for row in actual[1:]))

    def test_changed_title_does_not_inherit_earlier_editorial_reason(self):
        row = old_article("one", "/story", "Updated source headline")
        row.update(featuredReason="An earlier reading angle.", featuredPriority=1)
        actual = refresh_module.apply_editorial([row], {"articles": [{
            "publication": "one", "url": row["url"], "title": "Original source headline",
            "reason": "The old reason must not carry over.", "priority": 2}]})
        self.assertNotIn("featuredReason", actual[0])
        self.assertNotIn("featuredPriority", actual[0])
        self.assertEqual(actual[0]["title"], "Updated source headline")

    def test_removed_editorial_selection_clears_old_curation_fields(self):
        row = old_article("one", "/story")
        row.update(featuredReason="Previously selected.", featuredPriority=1)
        result = refresh_module.apply_editorial([row], {"articles": []})
        self.assertNotIn("featuredReason", result[0])
        self.assertNotIn("featuredPriority", result[0])
        self.assertEqual(result[0]["summary"], "Preserve the independent reading note.")

    def test_parallel_and_sequential_refresh_keep_same_order_rows_and_evidence(self):
        pubs = [publication(identifier, "example.test", hot=False)
                for identifier in ("alpha", "beta", "gamma")]
        previous = [old_article("alpha", "/alpha/retained"),
                    old_article("beta", "/beta/existing"),
                    old_article("gamma", "/gamma/retained")]
        prior = {"sources": [{"publication": pub["id"], "status": "ok",
                              "articles": deepcopy([row for row in previous
                                                    if row["publication"] == pub["id"]])}
                             for pub in pubs]}
        responses = {
            pubs[0]["feedUrl"]: feed("example.test", [
                ("A new alpha story", "/alpha/new", "2026-10-18")]),
            pubs[1]["feedUrl"]: feed("example.test", [
                ("A previously verified article", "/beta/existing", None)]),
            pubs[2]["feedUrl"]: TimeoutError("Official source is unavailable"),
        }
        serial = self.run_refresh(deepcopy(pubs), deepcopy(previous), DAY_ONE,
                                  responses, deepcopy(prior), workers=1)
        parallel = self.run_refresh(deepcopy(pubs), deepcopy(previous), DAY_ONE,
                                    responses, deepcopy(prior), workers=3)
        serial[2].pop("attemptedAt")
        parallel[2].pop("attemptedAt")
        self.assertEqual(serial, parallel)
        self.assertEqual([pub["id"] for pub in parallel[0]], ["alpha", "beta", "gamma"])
        old_ids = {(row["publication"], row["url"]) for row in previous}
        new_ids = {(row["publication"], row["url"]) for row in parallel[1]}
        self.assertTrue(old_ids.issubset(new_ids))
        beta = next(row for row in parallel[1] if row["publication"] == "beta")
        self.assertEqual(beta["publishedAt"], "2026-10-16")
        self.assertEqual(beta["summary"], previous[1]["summary"])

    def test_success_then_total_failure_keeps_original_hot_check_and_independent_proof(self):
        pub, _, (_, previous, report) = self.successful_hot()
        original = deepcopy(previous)
        _, current, next_report = self.run_refresh([pub], previous, DAY_TWO, {
            pub["feedUrl"]: TimeoutError("Feed unavailable"),
            pub["hotFeedUrl"]: TimeoutError("Popularity page unavailable")}, prior=report)
        self.assertEqual(current, original)
        hot = next(row for row in current if row.get("hotRank"))
        self.assertEqual(hot["hotCheckedAt"], DAY_ONE)
        self.assertEqual(next_report["sources"][0]["status"], "unavailable")
        retained = next(row for row in next_report["sources"][0]["retainedArticles"]
                        if row["url"] == hot["url"])
        self.assertEqual(retained["hotCheckedAt"], DAY_ONE)
        self.assertEqual(retained["hotSource"], pub["hotFeedUrl"])

    def test_feed_success_hot_failure_keeps_old_rank_and_original_hot_date(self):
        pub, responses, (_, previous, report) = self.successful_hot()
        responses[pub["hotFeedUrl"]] = TimeoutError("Popularity page unavailable")
        _, current, next_report = self.run_refresh([pub], previous, DAY_TWO, responses, prior=report)
        hot = next(row for row in current if row.get("hotRank"))
        self.assertEqual(hot["hotCheckedAt"], DAY_ONE)
        self.assertEqual(next_report["sources"][0]["hotStatus"], "unavailable")
        retained = next(row for row in next_report["sources"][0]["retainedArticles"]
                        if row["url"] == hot["url"])
        self.assertEqual(retained["hotCheckedAt"], DAY_ONE)

    def test_retained_hot_proof_survives_a_second_failed_day(self):
        pub, _, (_, previous, report) = self.successful_hot()
        failure = {pub["feedUrl"]: TimeoutError("Feed unavailable"),
                   pub["hotFeedUrl"]: TimeoutError("Popularity page unavailable")}
        _, rows_two, report_two = self.run_refresh([pub], previous, DAY_TWO, failure, prior=report)
        _, rows_three, report_three = self.run_refresh([pub], rows_two, DAY_THREE,
                                                       failure, prior=report_two)
        self.assertEqual(rows_three, previous)
        retained = next(row for row in report_three["sources"][0]["retainedArticles"]
                        if row.get("hotRank"))
        self.assertEqual(retained["hotCheckedAt"], DAY_ONE)
        self.assertEqual(retained["checkedAt"], DAY_ONE)

    def test_tampered_hot_rank_source_label_or_date_cannot_self_certify(self):
        pub, _, (_, previous, report) = self.successful_hot()
        original = next(row for row in previous if row.get("hotRank"))
        edits = {"hotRank": 99, "hotSource": "https://evil.test/fake-ranking",
                 "hotLabel": "Fabricated all-web popularity", "hotCheckedAt": DAY_TWO}
        for field, value in edits.items():
            with self.subTest(field=field):
                candidate = deepcopy(original)
                candidate[field] = value
                proof = refresh_module.retained_evidence([candidate], pub["id"], report)
                self.assertEqual(len(proof), 1)  # The independently known article still exists.
                self.assertFalse(any(key in proof[0] for key in HOT_FIELDS))

    def test_tampered_publication_date_or_title_has_no_retained_article_proof(self):
        pub, _, (_, previous, report) = self.successful_hot()
        original = next(row for row in previous if row.get("hotRank"))
        for field, value in (("publishedAt", DAY_TWO), ("title", "An invented source title")):
            with self.subTest(field=field):
                candidate = deepcopy(original)
                candidate[field] = value
                self.assertEqual(refresh_module.retained_evidence([candidate], pub["id"], report), [])

    def test_data_without_prior_successful_report_cannot_certify_itself(self):
        pub, _, (_, previous, _) = self.successful_hot()
        self.assertEqual(refresh_module.retained_evidence(previous, pub["id"], None), [])
        fake = {"sources": [{"publication": pub["id"], "status": "unavailable",
                             "articles": deepcopy(previous)}]}
        self.assertEqual(refresh_module.retained_evidence(previous, pub["id"], fake), [])

    def test_new_ranking_keeps_dropped_article_but_removes_old_hot_fields(self):
        pub, responses, (_, previous, report) = self.successful_hot()
        responses[pub["hotFeedUrl"]] = popular("/currently/", "A currently popular story")
        _, current, next_report = self.run_refresh([pub], previous, DAY_TWO, responses, prior=report)
        dropped = next(row for row in current if row["url"].endswith("/formerly/"))
        ranked = next(row for row in current if row["url"].endswith("/currently/"))
        self.assertFalse(any(field in dropped for field in HOT_FIELDS))
        self.assertEqual(dropped["publishedAt"], "2026-10-16")
        self.assertEqual(ranked["hotRank"], 1)
        self.assertEqual(ranked["hotCheckedAt"], DAY_TWO)
        self.assertEqual(next_report["sources"][0]["hotStatus"], "ok")

    def test_dropped_article_outside_current_feed_does_not_mutate_previous_input(self):
        pub, responses, (_, previous, report) = self.successful_hot()
        before_rows, before_report = deepcopy(previous), deepcopy(report)
        responses[pub["feedUrl"]] = feed("www.quantamagazine.org", [
            ("A currently popular story", "/currently/", "2026-10-17")])
        responses[pub["hotFeedUrl"]] = popular("/currently/", "A currently popular story")
        _, current, _ = self.run_refresh([pub], previous, DAY_TWO, responses, prior=report)
        self.assertEqual(previous, before_rows)
        self.assertEqual(report, before_report)
        dropped = next(row for row in current if row["url"].endswith("/formerly/"))
        self.assertFalse(any(field in dropped for field in HOT_FIELDS))
        self.assertEqual(dropped["publishedAt"], "2026-10-16")

    def test_rolling_feed_cap_preserves_exact_editorial_selection(self):
        old = old_article("one", "/important-research")
        old.update(featuredReason="Read the research methods critically.", featuredPriority=1)
        incoming = [old_article("one", "/new-" + str(i))
                    for i in range(refresh_module.PER_PUBLICATION)]
        before = deepcopy(old)
        merged = refresh_module.merge_articles([old], incoming, "one")
        self.assertEqual(len(merged), refresh_module.PER_PUBLICATION + 1)
        self.assertEqual(merged[-1], old)
        self.assertEqual(old, before)
        cleared = refresh_module.apply_editorial(merged, {"articles": []})
        next_run = refresh_module.merge_articles(cleared, incoming, "one")
        self.assertEqual(len(next_run), refresh_module.PER_PUBLICATION)
        self.assertFalse(any(row["url"] == old["url"] for row in next_run))

    def test_partial_list_headline_cannot_borrow_an_earlier_article_date(self):
        old = old_article("one", "/known-story", "Exact verified headline")
        incoming = {**old, "title": old["title"] + " Category", "publishedAt": None,
                    "checkedAt": DAY_TWO}
        merged = refresh_module.merge_articles([old], [incoming], "one")
        self.assertEqual(merged[0]["title"], old["title"])
        self.assertEqual(merged[0]["publishedAt"], old["publishedAt"])
        self.assertEqual(merged[0]["checkedAt"], old["checkedAt"])
        prior = {"sources": [{"publication": "one", "status": "ok", "articles": [old]}]}
        self.assertEqual(len(refresh_module.retained_evidence(merged, "one", prior)), 1)

    def test_partial_feed_cannot_evict_newer_verified_articles_at_capacity(self):
        pub = publication("one", "example.test", hot=False)
        pub["feedUrls"] = [pub["feedUrl"], "https://example.test/science/feed"]
        previous = [{**old_article("one", "/business-" + str(day)),
                     "publishedAt": "2026-10-%02d" % day} for day in (19, 18, 17)]
        before = deepcopy(previous)
        prior = {"sources": [{"publication": "one", "status": "ok",
                              "articles": deepcopy(previous)}]}
        responses = {pub["feedUrl"]: TimeoutError("Business feed temporarily unavailable"),
                     pub["feedUrls"][1]: feed("example.test", [
                         ("An older science story", "/science-" + str(day),
                          "2026-09-%02d" % day) for day in (3, 2, 1)])}
        with patch.object(refresh_module, "PER_PUBLICATION", 3):
            _, rows, report = self.run_refresh([pub], previous, DAY_TWO, responses, prior)
        self.assertEqual({row["url"] for row in rows}, {row["url"] for row in previous})
        self.assertEqual(len(report["sources"][0]["retainedArticles"]), 3)
        self.assertTrue(any(item["status"] == "unavailable"
                            for item in report["sources"][0]["details"]))
        self.assertEqual(previous, before)

    def test_rolling_cap_keeps_current_hot_even_when_older_than_regular_articles(self):
        previous = [{**old_article("one", "/recent-" + str(day)),
                     "publishedAt": "2026-10-%02d" % day} for day in (19, 18, 17)]
        ranked = {**old_article("one", "/older-but-currently-ranked"),
                  "publishedAt": "2026-09-01", "summary": "", "hotRank": 1,
                  "hotSource": "https://example.test/most-read", "hotLabel": "Most Read",
                  "hotCheckedAt": DAY_TWO}
        original = deepcopy(ranked)
        with patch.object(refresh_module, "PER_PUBLICATION", 3):
            merged = refresh_module.merge_articles(previous, [ranked], "one")
            self.assertEqual(len(merged), 4)
            self.assertEqual(merged[-1], ranked)
            for field in HOT_FIELDS:
                merged[-1].pop(field, None)
            next_run = refresh_module.merge_articles(merged, previous, "one")
        self.assertEqual(len(next_run), 3)
        self.assertFalse(any(row["url"] == ranked["url"] for row in next_run))
        self.assertEqual(ranked, original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
