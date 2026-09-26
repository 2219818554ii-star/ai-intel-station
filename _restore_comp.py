# -*- coding: utf-8 -*-
"""恢复被误删的 view-comp 区块（取自 git HEAD），插回 view-ted 之前。"""
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding="cp936", errors="replace")

GIT = r"D:/Git/cmd/git.EXE"
old_src = subprocess.run([GIT, "show", "HEAD:index.src.html"],
                         capture_output=True).stdout.decode("utf-8", "replace")

i0 = old_src.index('<div id="view-comp"')
i1 = old_src.index('<div id="view-ted"')
comp_block = old_src[i0:i1]
print("取回 view-comp 区块 %d 字符" % len(comp_block))

P = "index.src.html"
s = io.open(P, encoding="utf-8").read()
assert 'id="view-comp"' not in s, "已存在，勿重复插入"
assert 'id="view-ted"' in s
s = s.replace('<div id="view-ted"', comp_block + '<div id="view-ted"', 1)
io.open(P, "w", encoding="utf-8").write(s)
print("已插回")
