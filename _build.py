# 构建脚本：把模块化源(index.src.html + competitions.js + ted.js) 重新生成自包含部署版
# 用法：python _build.py
import os
import json
from _sync_research import validate as validate_research
from _sync_research_details import validate_bundle as validate_research_details

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, "index.src.html")      # 模块化源（可编辑）
js  = os.path.join(base, "competitions.js")      # 比赛数据
ted = os.path.join(base, "ted.js")               # TED 演讲数据
forum = os.path.join(base, "forum.js")           # 成长讲坛数据（企业家/国学/心学）
rank = os.path.join(base, "rank.js")             # 实力排行榜数据（每日自动更新）
cqut = os.path.join(base, "cqut.js")              # 重庆理工通知数据（学校/学院/部门/学生会）
nation = os.path.join(base, "matches.js")         # 比赛板块（按学校分类，只收还能参加的）
funds = os.path.join(base, "funds.js")            # 基金看板数据（持仓）
magazines = os.path.join(base, "magazines.js")    # 官方期刊与文章元数据
out_deploy = os.path.join(base, "index.html")    # 部署版（GitHub Pages 服务它）
out_gh     = os.path.join(base, "gh-pages", "index.html")
out_local  = os.path.join(base, "ai_intel_station_standalone.html")

html = open(src, encoding="utf-8").read()
workspace_style = '<style id="workspace-style"></style>'
assert workspace_style in html, 'workspace style marker missing'
html = html.replace(workspace_style, '<style id="workspace-style">\n' + open(os.path.join(base, 'workspace.css'), encoding='utf-8').read() + '\n</style>', 1)
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

nation_marker = '<script src="matches.js"></script>'
assert nation_marker in html, "nation marker not found in index.src.html!"
nation_data = open(nation, encoding="utf-8").read()
standalone = standalone.replace(nation_marker, "<script>\n" + nation_data + "\n</script>", 1)

funds_marker = '<script src="funds.js"></script>'
assert funds_marker in html, "funds marker not found in index.src.html!"
funds_data = open(funds, encoding="utf-8").read()
standalone = standalone.replace(funds_marker, "<script>\n" + funds_data + "\n</script>", 1)

magazines_marker = '<script src="magazines.js"></script>'
assert magazines_marker in html, "magazines marker not found in index.src.html!"
magazines_data = open(magazines, encoding="utf-8").read()
standalone = standalone.replace(magazines_marker, "<script>\n" + magazines_data + "\n</script>", 1)

# 只允许已审核的六字段展示摘要；网页含回退副本，在线时另取最新JSON。
research_data = validate_research(json.load(open(os.path.join(base, "research-data.json"), encoding="utf-8")))
research_details = validate_research_details(json.load(open(os.path.join(base, "research-details.json"), encoding="utf-8")), research_data)
research_snapshot = '<script id="research-data-snapshot"></script>'
research_marker = '<script src="research.js"></script>'
assert research_snapshot in standalone and research_marker in standalone, "research markers missing"
research_json = json.dumps(research_data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
details_json = json.dumps(research_details, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
standalone = standalone.replace(research_snapshot, "<script>\nwindow.RESEARCH_SNAPSHOT=" + research_json + ";\nwindow.RESEARCH_DETAILS=" + details_json + ";\n</script>", 1)
standalone = standalone.replace(research_marker, "<script>\n" + open(os.path.join(base,"research.js"), encoding="utf-8").read() + "\n</script>", 1)

workspace_marker = '<script src="workspace.js"></script>'
assert workspace_marker in standalone, 'workspace script marker missing'
standalone = standalone.replace(workspace_marker, '<script>\n' + open(os.path.join(base, 'workspace.js'), encoding='utf-8').read() + '\n</script>', 1)

cloud_marker = '<script src="cloud.js"></script>'
assert cloud_marker in standalone, 'cloud script marker missing'
standalone = standalone.replace(cloud_marker, '<script>\n' + open(os.path.join(base, 'cloud.js'), encoding='utf-8').read() + '\n</script>', 1)

for p in (out_deploy, out_gh, out_local):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(standalone)

print("OK  bytes=%d  资源库=%s  比赛内联=%s  TED内联=%s(%d)  讲坛内联=%s(%d)  排行内联=%s  理工内联=%s(%d)  全国内联=%s(%d)  基金内联=%s(%d)" % (
    len(standalone),
    "全网优质 AI 教学资源库" in standalone,
    marker not in standalone,
    ted_marker not in standalone, standalone.count('sp:"'),
    forum_marker not in standalone, standalone.count('{cat:"'),
    rank_marker not in standalone,
    cqut_marker not in standalone, cqut_data.count('{t:"'),
    nation_marker not in standalone, nation_data.count('n:"'),
    funds_marker not in standalone, funds_data.count('{ n: "'),
))
print("deploy ->", out_deploy)
print("gh     ->", out_gh)
print("local  ->", out_local)
