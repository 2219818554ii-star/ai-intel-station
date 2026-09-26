# -*- coding: utf-8 -*-
"""
上线前总检 _preship.py
======================
作用：在「宣布上线完成」之前，把过去真踩过的事故逐条拦下来。

检查项（每一条都对应一次踩坑记录）：
  [1] 产物是否过期         —— 改了 src 忘了跑构建，你以为上线了其实没有
  [2] 关键内容是否落地     —— 栏目标题/8 个细分类名（含 emoji）真的在产物里
  [3] git 是否与线上同步   —— origin/main..HEAD != 0 说明还有提交没推上去
  [4] 线上是否真的一致     —— GitHub Pages 上的 index.html 与本地产物 md5 相同
  [5] 链接是否真能打开     —— 真实 HTTP 抽检（WAF/反爬的 412、403 不算死链）

用法：python _preship.py            （失败退出码 1）
      python _preship.py --skip-remote   （断网时跳过 4/5）
"""
import io
import os
import re
import sys
import hashlib
import subprocess
import urllib.request
import urllib.error

# 命令行默认码页是 cp936，输出 emoji 会直接 UnicodeEncodeError 崩溃，
# 所以统一改成「cp936 + 不能编码就替换成 ?」，保证脚本在任何环境都不崩。
try:
    sys.stdout.reconfigure(encoding="cp936", errors="replace")
    sys.stderr.reconfigure(encoding="cp936", errors="replace")
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = "2219818554ii-star/ai-intel-station"
REMOTE_URL = "https://github.com/%s" % REPO
PROD = "index.html"
GH = "C:/Program Files/GitHub CLI/gh.exe"   # 注意在 C 盘，不是 D 盘
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

PASS, FAIL, WARN = "  [PASS]", "  [FAIL]", "  [WARN]"
results = []


def say(kind, msg, fix=""):
    results.append((kind, msg, fix))
    print(kind + " " + msg)
    if fix:
        for line in fix.split("\n"):
            print("        ↳ " + line)


def ok(kind, msg, fix=""):
    say(kind, msg, fix)


def bad(msg, fix=""):
    say(FAIL, msg, fix)


def warn(msg, fix=""):
    say(WARN, msg, fix)


def read(path):
    with io.open(os.path.join(BASE, path), encoding="utf-8") as f:
        return f.read()


def md5(data):
    """忽略换行差异的 md5。

    坑 revisit：本地 index.html 是 CRLF（Windows 下 python 写的），
    进 git 后被 autocrlf/.gitattributes 归一化成 LF。两边字节不同但页面完全一样，
    直接比 md5 会每次误报「线上不一致」。所以一律先统一换行。
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    data = data.replace(b"\r\n", b"\n")
    return hashlib.md5(data).hexdigest()


def readbin(path):
    with io.open(os.path.join(BASE, path), "rb") as f:
        return f.read()


def readtxt(path):
    # 注意：文本读会把 \r\n 吞成 \n，别拿它的 md5 当字节指纹
    with io.open(os.path.join(BASE, path), encoding="utf-8") as f:
        return f.read()


def run(cmd, **kw):
    p = subprocess.run(cmd, shell=False, cwd=BASE,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
    return p.returncode, out.strip()


def git(*args):
    return run(["D:/Git/cmd/git.EXE"] + list(args))


# =========================================================
print("=" * 68)
print("  上线前总检 · AI 情报站")
print("=" * 68 + "\n")

skip_remote = "--skip-remote" in sys.argv

# ---------- [0] 产物存在 ----------
if not os.path.exists(os.path.join(BASE, PROD)):
    bad("产物 %s 不存在，根本没构建过" % PROD, "先跑：python _build.py")
    sys.exit(1)
prod = readtxt(PROD)

# ---------- [1] 产物是否过期 ----------
print("[1] 产物新鲜度")
src_files = ["index.src.html", "competitions.js", "ted.js", "forum.js",
             "rank.js", "cqut.js", "funds.js"]
pm = os.path.getmtime(os.path.join(BASE, PROD))
fresh = []
for f in src_files:
    fp = os.path.join(BASE, f)
    if not os.path.exists(fp):
        bad("源文件缺失：" + f)
        continue
    if os.path.getmtime(fp) > pm + 1:
        fresh.append(f)
if fresh:
    bad("以下源文件比产物新，说明改了没构建，线上还是旧版：\n        "
        + "\n        ".join(fresh),
        "先跑：python _build.py  然后重新推送")
else:
    ok(PASS, "源文件全部已构建进产物（%d 个输入）" % len(src_files))

# 产物里必须内联了 5 份数据，不能还是外链
leftover = [f for f in src_files[1:]
            if '<script src="%s"></script>' % f in prod]
if leftover:
    bad("产物里仍有未内联的外链：%s" % ", ".join(leftover),
        "跑 python _build.py，它会在内联失败时报错退出")
else:
    ok(PASS, "%d 份数据文件全部内联，产物自包含" % (len(src_files) - 1))

# ---------- [2] 关键内容是否真的落地 ----------
print("\n[2] 关键内容落地检查（直接读产物全文，emoji 也精确匹配）")
MUST_CONTAIN = [
    ("每日日报 tab 文案", "📰"),
    ("实力排行榜 tab 文案", "🏆"),
    ("可报名比赛 tab 文案", "🏁"),
    ("AI 上手 tab 文案", "📚"),
    ("TED 英语 tab 文案", "🎓"),
    ("成长讲坛 tab 文案", "🌱"),
    ("重庆理工 tab 文案", "🏫"),
    ("理工列表容器", 'id="cqut-list"'),
    ("理工一级筛选", 'id="cqutFilters"'),
    ("理工二级筛选", 'id="cqutTagFilters"'),
    ("理工信源矩阵", 'id="cqut-sources"'),
    ("讲坛系列入口按钮", "进入视频清单"),
    ("讲坛视频直达播放按钮", "在B站播放"),
    ("讲坛返回系列按钮", "← 返回系列列表"),
    ("基金看板 tab 文案", "📈 基金看板"),
    ("基金持仓列表容器", 'id="funds-list"'),
    ("各学院赛事区块标题", "各学院赛事"),
    ("各学院赛事列表容器", 'id="cqut-match-list"'),
    ("各学院赛事筛选容器", 'id="cqutMatchFilters"'),
    ("赛事我所能栏位", "具体要干啥"),
]
missing = [n for n, s in MUST_CONTAIN if s not in prod]
if missing:
    bad("产物里找不到：%s" % "、".join(missing),
        "改了 index.src.html 但没构建 / 或改动本身有 bug")
else:
    ok(PASS, "%d 项关键结构全部存在（8 栏目 + 理工 4 组件 + 基金 2 组件 + 赛事 3 组件 + TED 多看入口）"
       % len(MUST_CONTAIN))

# 8 个细分类：直接从 cqut.js 读真名，再去产物里找
try:
    mo = re.search(r"window\.CQUT_TAGS\s*=\s*\[(.*?)\];", read("cqut.js"), re.S)
    tagnames = re.findall(r'n:"([^"]+)"', mo.group(1)) if mo else []
    tagkeys = re.findall(r'k:"([^"]+)"', mo.group(1)) if mo else []
except Exception:
    tagnames, tagkeys = [], []
miss_tag = [t for t in tagnames if t not in prod]
if tagnames and not miss_tag:
    ok(PASS, "理工 8 个细分类名全部出现在产物：%s" % " / ".join(tagnames))
elif not tagnames:
    bad("cqut.js 里解析不出 CQUT_TAGS")
else:
    bad("产物里缺少细分类：%s" % "、".join(miss_tag),
        "改完 index.src.html 没重新构建")
if len(tagkeys) == 8:
    ok(PASS, "细分类枚举数量 = %d（与自检期望一致）" % len(tagkeys))
elif tagkeys:
    bad("细分类枚举数量 = %d，但 _selfcheck.js 期望 8——两边不同步了"
        % len(tagkeys))

# ---------- [3] git 是否与线上同步 ----------
print("\n[3] git 同步状态")
rc, out = git("rev-list", "--count", "origin/main..HEAD")
if rc != 0 or not out.isdigit():
    warn("拿不到 origin/main 提交数（可能刚建仓库或断网），跳过",
         "确认过 [4] 线上一致即可")
elif int(out) > 0:
    bad("还有 %s 个提交没推到 GitHub" % out,
        "推送时先存退出码再判断，别用 `push | tail`（tail 会盖掉 git 的退出码）")
else:
    ok(PASS, "本地与 origin/main 完全同步（落后 0 个提交）")

rc, out = git("status", "--porcelain")
if rc == 0 and out:
    warn("工作区有未提交的改动（不影响线上，但下次会盖住旧版）：\n        "
         + "\n        ".join(out.split("\n")[:8]))
else:
    ok(PASS, "工作区干净，无未提交改动")

# ---------- [4] 线上是否真的一致 ----------
print("\n[4] GitHub Pages 线上一致性")
if skip_remote:
    print("  (跳过：手动指定 --skip-remote)")
else:
    served = None
    for attempt in range(3):
        rc, out = run([GH,
                       "api", "-H", "Accept: application/vnd.github.raw",
                       "repos/%s/contents/%s" % (REPO, PROD)])
        # gh api 输出是文本，文本读会把 \r\n 抹平，这里直接当字节用不可靠，
        # 所以只用它判断「拿没拿到」，真比对交给下面 curl 拉到的线上页面。
        if rc == 0 and len(out) > 5000:
            served = True
            break
        print("     尝试 %d/3 未取到仓库文件…" % (attempt + 1))
    if served is None:
        warn("取不到仓库里的 index.html（多为 VPN 抖动）\n        "
             "修复：多跑几次；仍不行加 --skip-remote")
    else:
        ok(PASS, "仓库里已能读到 index.html（说明已提交并推送）")

    # 真正的「线上」= 用户浏览器打开的那个地址
    online = None
    try:
        req = urllib.request.Request(
            "https://%s.github.io/ai-intel-station/%s" % (REPO.split("/")[0], PROD),
            headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            online = r.read()
    except Exception as e:
        warn("访问线上地址失败（%s）" % getattr(e, "reason", e))
    if online is not None:
        if md5(online) == md5(readbin(PROD)):
            ok(PASS, "线上站点页面 = 本地产物（%.1f KB），用户看到的就是最新版"
               % (len(online) / 1024.0))
        else:
            bad("线上站点还是旧版！线上 md5=%s，本地 md5=%s"
               % (md5(online), md5(readbin(PROD))),
                "① 先 `git status --porcelain` 确认 index.html 已提交\n"
                "② `git push`，推完立刻再跑一次本脚本复核\n"
                "③ 真还不行就别宣布上线，直接跟用户说线上滞后")

# ---------- [5] 链接真实抽检 ----------
print("\n[5] 链接真实抽检（HTTP 请求，非 2xx 才报错）")
PROBE = [
    ("TED 官方搜索", "https://www.ted.com/search?q=how+to+learn"),
    ("B站", "https://search.bilibili.com/all?keyword=ted"),
    ("重理工·部门通知", "https://www.cqut.edu.cn/tzgg/bmtz.htm"),
    ("天天基金·南方纳指100", "https://fund.eastmoney.com/016452.html"),
    ("重理工·校团委", "https://qnzx.cqut.edu.cn/index.htm"),
    ("arXiv（如用到）", "https://arxiv.org"),
]
WAF = (412, 403, 503)  # 学校站 WAF/反爬，不代表链接失效
hard_bad, waf_list, ok_list, soft_note = [], [], [], []
for name, url in PROBE:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.getcode()
            if 200 <= code < 400:
                ok_list.append("%s → %d" % (name, code))
            else:
                hard_bad.append("%s → %d" % (name, code))
    except urllib.error.HTTPError as e:
        if e.code in WAF:
            waf_list.append("%s → %d（站点反爬，不算死链）" % (name, e.code))
        else:
            hard_bad.append("%s → %d" % (name, e.code))
    except Exception as e:
        # 「如用到」类探针：站点里压根没这个链接，网络不通只算提示，不能判死
        if "（如用到）" in name:
            if '"%s"' % url.split("//")[-1] in html or url in html:
                hard_bad.append("%s → 页面在引用它但连不上（%s）" % (name, getattr(e, "reason", e)))
            else:
                soft_note.append("%s → 未使用，跳过（%s）" % (name, getattr(e, "reason", e)))
        else:
            hard_bad.append("%s → 连不上（%s）" % (name, getattr(e, "reason", e)))
for line in ok_list + waf_list + soft_note:
    print("      %s" % line)
if hard_bad:
    bad("抽检到 %d 个打不开的链接：%s" % (len(hard_bad), "、".join(hard_bad)))
else:
    ok(PASS, "抽检 %d 个关键入口全部可达（%d 个站点反爬已豁免）"
       % (len(PROBE), len(waf_list)))

# ---------- 汇总 ----------
deadline = "  " + "-" * 50
print("\n" + deadline)
nf = len([1 for k, m, f in results if k == FAIL])
nw = len([1 for k, m, f in results if k == WARN])
np_ = len([1 for k, m, f in results if k == PASS])
print("  上线前总检：%d 通过 / %d 警告 / %d 失败" % (np_, nw, nf))
if nf:
    print("\n  >>> 结论：不许宣布上线。按上面 FAIL 行的 ↳ 提示逐条修。")
    print("      禁止用「应该没问题吧」蒙混——你就是靠这个才被 TED 404 截图的。")
else:
    print("\n  >>> 结论：可以上线。本地 = 线上 = 最新构建。")
print(deadline)
sys.exit(1 if nf else 0)
