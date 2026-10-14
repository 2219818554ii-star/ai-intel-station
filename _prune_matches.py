# -*- coding: utf-8 -*-
"""删 matches.js 里 3 条已过期条目 + 移除因此空掉的 miit 分类。
按 n: 锚点定位整个 {...} 块删除，保留同分类其它条目及其注释。"""
import re

P = "matches.js"
txt = open(P, encoding="utf-8").read()
orig = txt

EXPIRED = [
    "第五届大学生标准创新大赛",
    "2026 年度重庆市大学生知识产权普法大赛",
    "第十五届中国创新创业大赛 · 颠覆性技术创新大赛（未来产业方向）",
]

def remove_entry(t, name):
    idx = t.find('n:"%s"' % name)
    if idx < 0:
        raise SystemExit("NOT FOUND: " + name)
    start = t.rfind("\n  {\n", 0, idx)          # 条目起始
    end = t.find("\n  },", idx)                  # 条目结束
    if start < 0 or end < 0:
        raise SystemExit("bounds fail: " + name)
    return t[:start + 1] + t[end + len("\n  },") + 1:]

for name in EXPIRED:
    txt = remove_entry(txt, name)

# miit 唯一条目已删 → 移除孤立的「部委·产业赛」分类注释
txt = txt.replace("\n  /* ===== ⚡ 部委·产业赛 ===== */\n", "\n")
# 从 MATCH_SCHOOLS 移除 miit
before = txt
txt = re.sub(r'\n  \{k:"miit",[^\n]*\},?', '', txt)
if txt == before:
    raise SystemExit("miit school not removed")

open(P, "w", encoding="utf-8").write(txt)
# 校验
left = re.findall(r'st:"报名中"', txt)
import re as _r
n_cnt = len(_r.findall(r'\n    n:"', txt))
print("已删 3 条过期。剩余 n: 条目 =", n_cnt, "| 仍含 miit 分类:", 'k:"miit"' in txt)
print("EXPIRED 残留:", [e for e in EXPIRED if e in txt])
