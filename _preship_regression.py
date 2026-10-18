"""Offline checks for deployment verification; no live network or data edits."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import runpy
import subprocess
import sys
import unittest
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parent
PRODUCT = (ROOT / "index.html").read_bytes()


class Response:
    def __init__(self, data=PRODUCT):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        return self.data

    def getcode(self):
        return 200


class DeploymentChecks(unittest.TestCase):
    def run_check(self, *, skip=False, changed=False, behind=False, optional_dns=False, gh_timeout=False):
        requests = []

        def command(args, **kwargs):
            if gh_timeout and str(args[0]).endswith("gh.exe"):
                self.assertEqual(kwargs.get("timeout"), 25)
                raise subprocess.TimeoutExpired(args, kwargs["timeout"])
            if "rev-list" in args:
                output = b"0\t2" if behind else b"0\t0"
            elif "status" in args:
                output = b""
            else:
                output = PRODUCT
            return subprocess.CompletedProcess(args, 0, stdout=output, stderr=b"")

        def urlopen(req, **kwargs):
            url = req.full_url
            requests.append(url)
            if optional_dns and url == "https://arxiv.org":
                raise urllib.error.URLError("fixture DNS failure")
            if ".github.io/" in url and changed:
                return Response(PRODUCT.replace(b"AI_SESSION", b"AI_STALE_SESSION", 1))
            return Response()

        output = StringIO()
        args = [str(ROOT / "_preship.py")] + (["--skip-remote"] if skip else [])
        # Keep the script's Windows terminal configuration from changing this test's streams.
        with patch.object(sys, "argv", args), patch.object(subprocess, "run", command), \
                patch("urllib.request.urlopen", urlopen), redirect_stdout(output):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(ROOT / "_preship.py"), run_name="__main__")
        return result.exception.code, requests, output.getvalue()

    def test_skip_remote_does_not_access_network_or_claim_deployment(self):
        code, requests, output = self.run_check(skip=True)
        self.assertEqual(code, 0)
        self.assertEqual(requests, [])
        self.assertIn("尚不能据此确认上线", output)

    def test_matching_container_names_do_not_hide_changed_html(self):
        code, _, output = self.run_check(changed=True)
        self.assertEqual(code, 1)
        self.assertIn("线上页面与本地产物不同", output)

    def test_unused_optional_link_dns_failure_does_not_crash(self):
        code, _, output = self.run_check(optional_dns=True)
        self.assertEqual(code, 0)
        self.assertIn("未使用，跳过", output)

    def test_behind_remote_is_not_reported_as_synchronized(self):
        code, _, output = self.run_check(skip=True, behind=True)
        self.assertEqual(code, 1)
        self.assertIn("本地落后 origin/main 2 个提交", output)

    def test_github_command_timeout_reports_warning_and_checks_public_page(self):
        code, requests, output = self.run_check(gh_timeout=True)
        self.assertEqual(code, 0)
        self.assertIn("尝试 3/3", output)
        self.assertIn("取不到仓库里的 index.html", output)
        self.assertTrue(any(".github.io/" in url for url in requests))
        self.assertIn("线上站点页面 = 本地产物", output)


if __name__ == "__main__":
    unittest.main()
