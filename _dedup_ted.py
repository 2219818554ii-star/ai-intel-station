# -*- coding: utf-8 -*-
"""TED 去重：同一 en 标题保留首次出现，删后续重复（+15 扩容批次的 7 条重复）。"""
import re

P = "ted.js"
txt = open(P, encoding="utf-8").read()
start = txt.index("window.TED = [") + len("window.TED = [")
end = txt.index("\n]", start)                 # 数组收尾行 "]" 独立成行
head, body, tail = txt[:start], txt[start:end], txt[end:]

result, buf, cur = [], None, None
seen, dropped = set(), []

def flush():
    global buf, cur
    if buf is not None:
        if cur in seen:
            dropped.append(cur)
        else:
            seen.add(cur)
            result.extend(buf)
    buf, cur = None, None

for ln in body.split("\n"):
    if ln.startswith("  {en:"):
        flush()
        buf = [ln]
        m = re.search(r'en:"([^"]+)"', ln)
        cur = m.group(1) if m else "\x00"
        if ln.rstrip().endswith("},"):       # 单行条目
            flush()
    elif buf is not None:
        buf.append(ln)
        if ln.rstrip().endswith("},"):
            flush()
    else:
        result.append(ln)
flush()

txt2 = head + "\n".join(result) + tail
open(P, "w", encoding="utf-8").write(txt2)
print("删除重复:", len(dropped))
for d in dropped:
    print("  -", d)
print("剩余条目:", len(re.findall(r'^\s*\{en:', txt2, re.M)))
