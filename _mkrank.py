# -*- coding: utf-8 -*-
# 把内联的 RANK 数据抽取为独立 rank.js，并在 index.src.html 改为 window.RANK 引用
import re, os
base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, "index.src.html")
s = open(src, encoding="utf-8").read()

# 1) 抽取 RANK 块（从 "var RANK = {" 到首个独立成行的 "  };")
m = re.search(r'var RANK = \{[\s\S]*?\n  \};', s)
assert m, "RANK block not found"
block = m.group(0)

# 2) 生成 rank.js（带更新日期，并把内部复核日期一并刷新）
rank_js = '/* AI 情报站 - 实力排行榜数据（每日自动更新） */\n'
rank_js += 'window.RANK_UPDATED = "2026-09-24";\n'
block_fixed = block.replace('var RANK =', 'window.RANK =', 1)
block_fixed = block_fixed.replace('2026-09-22 复核', '2026-09-24 复核')
rank_js += block_fixed + '\n'
open(os.path.join(base, "rank.js"), "w", encoding="utf-8").write(rank_js)
print("rank.js 写出, 长度", len(rank_js))

# 3) index.src.html：内联块替换为 window.RANK 引用
s2 = s.replace(block, 'var RANK = window.RANK || {};')
assert s2 != s, "替换内联 RANK 失败"

# 4) 加 rank.js 脚本标签（forum.js 之后）
assert '<script src="forum.js"></script>' in s2
s2 = s2.replace('<script src="forum.js"></script>',
                '<script src="forum.js"></script>\n  <script src="rank.js"></script>', 1)

# 5) 快照日期 -> 今天，并加"每日自动更新"徽章
s2 = s2.replace('数据截至 <b>2026-09-22</b>。',
                '数据截至 <b>2026-09-24</b>。<span style="display:inline-block;margin-left:8px;padding:2px 9px;border-radius:999px;background:#ecfdf5;color:#15803d;font-size:12px;font-weight:700;border:1px solid #bbf7d0">🔄 每日自动更新</span>')
s2 = s2.replace('人工核对快照（2026-09-22）', '每日自动更新快照（2026-09-24）')

open(src, "w", encoding="utf-8").write(s2)
print("index.src.html 已更新")
