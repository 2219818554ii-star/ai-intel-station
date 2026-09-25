# 构建脚本：把模块化源(index.src.html + competitions.js + ted.js) 重新生成自包含部署版
# 用法：python _build.py
import os

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, "index.src.html")      # 模块化源（可编辑）
js  = os.path.join(base, "competitions.js")      # 比赛数据
ted = os.path.join(base, "ted.js")               # TED 演讲数据
forum = os.path.join(base, "forum.js")           # 成长讲坛数据（企业家/国学/心学）
rank = os.path.join(base, "rank.js")             # 实力排行榜数据（每日自动更新）
cqut = os.path.join(base, "cqut.js")              # 重庆理工通知数据（学校/学院/部门/学生会）
funds = os.path.join(base, "funds.js")            # 基金看板数据（持仓）
out_deploy = os.path.join(base, "index.html")    # 部署版（GitHub Pages 服务它）
out_gh     = os.path.join(base, "gh-pages", "index.html")
out_local  = os.path.join(base, "ai_intel_station_standalone.html")

html = open(src, encoding="utf-8").read()
data = open(js, encoding="utf-8").read()
ted_data = open(ted, encoding="utf-8").read()

marker = '<script src="competitions.js"></script>'
assert marker in html, "competitions marker not found in index.src.html!"
standalone = html.replace(marker, "<script>\n" + data + "\n</script>", 1)

ted_marker = '<script src="ted.js"></script>'
assert ted_marker in html, "ted marker not found in index.src.html!"
standalone = standalone.replace(ted_marker, "<script>\n" + ted_data + "\n</script>", 1)

forum_marker = '<script src="forum.js"></script>'
assert forum_marker in html, "forum marker not found in index.src.html!"
forum_data = open(forum, encoding="utf-8").read()
standalone = standalone.replace(forum_marker, "<script>\n" + forum_data + "\n</script>", 1)

rank_marker = '<script src="rank.js"></script>'
assert rank_marker in html, "rank marker not found in index.src.html!"
rank_data = open(rank, encoding="utf-8").read()
standalone = standalone.replace(rank_marker, "<script>\n" + rank_data + "\n</script>", 1)

cqut_marker = '<script src="cqut.js"></script>'
assert cqut_marker in html, "cqut marker not found in index.src.html!"
cqut_data = open(cqut, encoding="utf-8").read()
standalone = standalone.replace(cqut_marker, "<script>\n" + cqut_data + "\n</script>", 1)

funds_marker = '<script src="funds.js"></script>'
assert funds_marker in html, "funds marker not found in index.src.html!"
funds_data = open(funds, encoding="utf-8").read()
standalone = standalone.replace(funds_marker, "<script>\n" + funds_data + "\n</script>", 1)

for p in (out_deploy, out_gh, out_local):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(standalone)

print("OK  bytes=%d  资源库=%s  比赛内联=%s  TED内联=%s(%d)  讲坛内联=%s(%d)  排行内联=%s  理工内联=%s(%d)  基金内联=%s(%d)" % (
    len(standalone),
    "全网优质 AI 教学资源库" in standalone,
    marker not in standalone,
    ted_marker not in standalone, standalone.count('sp:"'),
    forum_marker not in standalone, standalone.count('{cat:"'),
    rank_marker not in standalone,
    cqut_marker not in standalone, cqut_data.count('{t:"'),
    funds_marker not in standalone, funds_data.count('{ n: "'),
))
print("deploy ->", out_deploy)
print("gh     ->", out_gh)
print("local  ->", out_local)
