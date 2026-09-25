# -*- coding: utf-8 -*-
"""重建成长讲坛：系列 -> 具体视频（B站真实 BV 号，绝不编造）。
用户反馈：搜索页入口太广泛，要求 点系列 -> 看视频列表 -> 点视频直达播放页。
数据源：B站官方搜索 API（api.bilibili.com/x/web-interface/search/type）。
先 GET www.bilibili.com 拿 buvid3 cookie，再带 UA+Referer 调搜索 API（实测 200/code=0）。
挑片规则：时长>=300s 的正片，按播放量取前 6；标题清洗 <em> 高亮标签与 HTML 实体。
生成后逐系列抽验第 1 个视频链接（HTTP 200 且页面含该 BV 号）才算成功。"""
import json, re, sys, time, html, urllib.request, urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# ---- 系列定义：cat / who / 搜索关键词 / 系列导语（导语沿用旧版编辑推荐语） ----
SERIES = [
 ("名人与企业家","马云","马云 演讲","从英语老师到阿里创始人。低谷期、迷茫期最该听的一类：今天很残酷，明天更残酷，后天很美好。"),
 ("名人与企业家","雷军","雷军 年度演讲","小米创始人每年一场的「年度演讲」，讲风口上的选择逻辑与长期主义心态。"),
 ("名人与企业家","马斯克","马斯克 演讲 中文字幕","第一性原理思考法：为什么造电动车、上火星、挖隧道。英文原声配中文字幕。"),
 ("名人与企业家","乔布斯","乔布斯 斯坦福大学演讲","2005 斯坦福毕业演讲「Stay hungry, stay foolish」，三个故事讲热爱、失去与死亡。"),
 ("名人与企业家","任正非","任正非 访谈","华为创始人访谈实录：危机意识、基础研究与技术自立。做科研的人听最有共鸣。"),
 ("名人与企业家","曹德旺","曹德旺 演讲","福耀玻璃创始人讲制造业的坚守、成本与诚信，实业家的钝感力。"),
 ("名人与企业家","张一鸣","张一鸣 演讲","字节跳动创始人反复强调「延迟满足感」：把眼光放长的人赢面更大。"),
 ("名人与企业家","俞敏洪","俞敏洪 演讲","新东方创始人成名演讲：在绝望中寻找希望，普通人靠努力对抗出身。"),
 ("名人与企业家","稻盛和夫","稻盛和夫 演讲","日本「经营之圣」：敬天爱人、付出不亚于任何人的努力，与阳明心学一脉相承。"),
 ("名人与企业家","曾毓群","曾毓群 宁德时代","宁德时代创始人讲动力电池技术路线与产业判断，电池方向必听。"),
 ("国学讲坛","易中天","易中天 品三国","百家讲坛最火的一档，用大白话讲三国人物与权谋，历史入门首选。"),
 ("国学讲坛","王立群","王立群 读史记","河南大学教授讲《史记》，人物心理分析极细，历史与人性观察必看。"),
 ("国学讲坛","于丹","于丹 论语心得","把《论语》讲成现代人的生活智慧，语速慢、金句多，零基础国学入口。"),
 ("国学讲坛","蒙曼","蒙曼 武则天","中央民大教授讲武则天，史学功底与讲故事能力俱佳。"),
 ("国学讲坛","鲍鹏山","鲍鹏山 新说水浒","从《水浒》看中国人的处世与人格，观点犀利。"),
 ("国学讲坛","郦波","郦波 五百年来王阳明","南京师大教授讲王阳明一生，心学最好的视频入门。"),
 ("国学讲坛","康震","康震 唐宋八大家","北师大教授讲八大家的文章与人生，提文字表达与文学素养。"),
 ("国学讲坛","阎崇年","阎崇年 清十二帝疑案","百家讲坛开山级节目，讲清朝十二帝疑案，历史科普经典。"),
 ("阳明心学","郦波 · 心学入门","郦波 五百年来王阳明","第 1 步首选：把王阳明一生讲成故事，零基础听懂心学从哪来。"),
 ("阳明心学","董平 · 浙大公开课","董平 王阳明心学","第 2 步：浙大教授系统讲心学哲学结构（心即理、知行合一、致良知）。"),
 ("阳明心学","王德峰 · 复旦讲座","王德峰 阳明心学","第 2 步进阶：复旦王德峰用哲学讲心学与人生，适合想知道「为什么」的人。"),
 ("阳明心学","典籍里的中国","典籍里的中国 传习录","央视用戏剧还原王阳明与《传习录》，画面感强，当入门的调味料。"),
 ("阳明心学","传习录精读","传习录 讲解","第 3 步：心学「圣经」原文，配讲解版一天两三条慢慢品。"),
 ("阳明心学","度阴山 · 通俗解读","度阴山 知行合一王阳明","把心学讲成能用在生活里的方法，适合想「马上能用」的人。"),
 ("阳明心学","心学实践","阳明心学 事上磨练","第 4 步：在科研、组会、人际里练「省察克治」，把心学真正用起来。"),
]

def get_cookie():
    req = urllib.request.Request("https://www.bilibili.com/", headers={"User-Agent": UA})
    with OPENER.open(req, timeout=15) as r:
        setc = r.headers.get_all("Set-Cookie") or []
    pairs = []
    for c in setc:
        m = re.match(r"([^=;\s]+)=([^;]*)", c)
        if m:
            pairs.append(m.group(1) + "=" + m.group(2))
    return "; ".join(pairs)

# B站是国内站：沙箱代理(127.0.0.1:*)对它限流严重，一律禁代理直连（实测 curl 直连 code=0）
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def search(cookie, kw, page=1):
    q = urllib.parse.quote(kw)
    url = ("https://api.bilibili.com/x/web-interface/search/type?search_type=video"
           "&keyword=%s&page=%d&page_size=20" % (q, page))
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Referer": "https://search.bilibili.com/",
        "Cookie": cookie})
    with OPENER.open(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    if data.get("code") != 0:
        raise RuntimeError("API code=%s %s" % (data.get("code"), data.get("message")))
    return (data.get("data") or {}).get("result") or []

def clean_title(t):
    t = re.sub(r"<em[^>]*>|</em>", "", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

def dur_sec(d):
    try:
        parts = [int(x) for x in str(d).split(":")]
        s = 0
        for p in parts:
            s = s * 60 + p
        return s
    except Exception:
        return 0

def pick(kw, cookie):
    rows = search(cookie, kw)
    vids = []
    for r in rows:
        title = clean_title(r.get("title", ""))
        bvid = r.get("bvid", "")
        sec = dur_sec(r.get("duration", "0:00"))
        if not bvid or not title:
            continue
        if sec < 300:      # 过滤 5 分钟内的切片/预告
            continue
        vids.append({"t": title, "bvid": bvid, "up": r.get("author", ""),
                     "dur": r.get("duration", ""), "play": int(r.get("play") or 0)})
    vids.sort(key=lambda v: v["play"], reverse=True)
    return vids[:6]

def verify(bvid, cookie=None):
    """用 B站官方 view API 逐条验证：code=0 且 bvid 匹配 -> 视频真实存在。
    （视频页本身会 301 重定向，不能当失败判据；API 才是权威。）
    ⚠ view API 必须带 buvid3 cookie，否则一律返回拦截码，会把好视频全误判成死链。
    偶发失败重试 2 次，避免限流误删。"""
    hdr = {"User-Agent": UA, "Referer": "https://www.bilibili.com/",
           "Accept": "application/json, text/plain, */*",
           "Accept-Language": "zh-CN,zh;q=0.9"}
    if cookie:
        hdr["Cookie"] = cookie
    url = "https://api.bilibili.com/x/web-interface/view?bvid=" + bvid
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=hdr)
            with OPENER.open(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))
            if d.get("code") == 0:
                return (d.get("data") or {}).get("bvid") == bvid
            time.sleep(1.2 * (attempt + 1))
        except Exception:
            time.sleep(1.2 * (attempt + 1))
    return False

def main():
    cookie = get_cookie()
    print("cookie ok:", bool(cookie))
    out, cache = [], {}
    total_vids = 0
    for cat, who, kw, desc in SERIES:
        try:
            if kw in cache:
                vids = cache[kw]
                print("[cache] %-12s %s -> %d" % (who, kw, len(vids)))
            else:
                vids = pick(kw, cookie)
                cache[kw] = vids
                time.sleep(1.1)
                print("[fetch] %-12s %-22s -> %d 条" % (who, kw, len(vids)))
        except Exception as e:
            print("[FAIL] %s %s: %s" % (who, kw, e))
            continue
        if not vids:
            print("  !! 空结果，跳过该系列（不许编造）")
            continue
        out.append({"cat": cat, "who": who, "kw": kw, "desc": desc, "vids": vids})
        total_vids += len(vids)
        time.sleep(0.3)
    print("\n系列 %d 个，视频共 %d 条" % (len(out), total_vids))

    # 全量验证：逐条过 view API（带 cookie），验证不过的直接剔除，不留死链
    bad, kept = [], []
    check = 0
    for s in out:
        good = []
        for v in s["vids"]:
            check += 1
            if verify(v["bvid"], cookie):
                good.append(v)
            else:
                bad.append((s["who"], v["t"], v["bvid"]))
            time.sleep(0.5)
        print("[verify] %-14s %d/%d 通过" % (s["who"], len(good), len(s["vids"])))
        if len(good) >= 3:
            s["vids"] = good
            kept.append(s)
        else:
            print("  !! 剔除整个系列（验证通过不足 3 条）：", s["who"])
        time.sleep(0.2)
    out = kept
    total_vids = sum(len(s["vids"]) for s in out)
    print("\n全量验证 %d 条，剔除 %d 条，保留 %d 系列 / %d 视频" % (check, len(bad), len(out), total_vids))
    if bad:
        print("被剔除的死链：")
        for w, t, b in bad:
            print("   -", w, "|", t, "|", b)
    if not out:
        print("!! 全部被剔除，中止生成（不许编造）")
        return

    # 生成 forum.js
    def jdump(o):
        return json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    lines = []
    lines.append('/* AI 情报站 - 成长讲坛 v2：系列 -> 具体视频（B站真实 BV 号）')
    lines.append('   2026-09-25 按用户反馈重构：点系列 -> 看视频列表 -> 点视频直达播放页。')
    lines.append('   数据来自 B站官方搜索 API 实抓，含标题/UP主/时长/播放量，生成时已逐条抽验链接 200。 */')
    lines.append('window.FORUM_UPDATED = "2026-09-25";')
    lines.append('window.FORUM_CATS = ["名人与企业家","国学讲坛","阳明心学"];')
    lines.append('window.FORUM_SERIES = [')
    for s in out:
        vids = ",\n    ".join(jdump(v) for v in s["vids"])
        lines.append('  {cat:%s, who:%s, desc:%s, vids:[\n    %s\n  ]},'
                     % (jdump(s["cat"]), jdump(s["who"]), jdump(s["desc"]), vids))
    lines.append('];')
    with open("forum.js", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\nforum.js 已重写：%d 系列 / %d 视频" % (len(out), total_vids))

if __name__ == "__main__":
    main()
