# 构建脚本：把模块化源(index.src.html + competitions.js) 重新生成自包含部署版
# 用法：python _build.py
import os

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, "index.src.html")      # 模块化源（可编辑）
js  = os.path.join(base, "competitions.js")      # 比赛数据
out_deploy = os.path.join(base, "index.html")    # 部署版（GitHub Pages 服务它）
out_gh     = os.path.join(base, "gh-pages", "index.html")
out_local  = os.path.join(base, "ai_intel_station_standalone.html")

html = open(src, encoding="utf-8").read()
data = open(js, encoding="utf-8").read()

marker = '<script src="competitions.js"></script>'
assert marker in html, "marker not found in index.src.html!"
standalone = html.replace(marker, "<script>\n" + data + "\n</script>", 1)

for p in (out_deploy, out_gh, out_local):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(standalone)

print("OK  bytes=%d  资源库=%s  比赛条目scope:%d  JS内联=%s" % (
    len(standalone),
    "全网优质 AI 教学资源库" in standalone,
    standalone.count('"scope":') ,  # 兼容性占位，实际用 scope:
    marker not in standalone,
))
print("deploy ->", out_deploy)
print("gh     ->", out_gh)
print("local  ->", out_local)
