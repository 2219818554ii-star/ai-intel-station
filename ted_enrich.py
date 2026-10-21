import re, subprocess, time, json

SITE = r"C:/Users/22198/WorkBuddy/2026-08-11-19-02-45/ai_daily_site"
SRC = SITE + "/ted.js"

html = open(SRC, encoding="utf-8").read()
urls = re.findall(r'url:"([^"]+)"\},', html)  # 只抓未富集的(以 }, 结尾、无 cover/views)
uniq = list(dict.fromkeys(urls))
print("total url fields:", len(urls), "| unique:", len(uniq))

def curl(url):
    cmd = ["curl", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "--max-time", "30", "-w", "\n@@HTTP@@%{http_code}", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        return r.stdout
    except Exception as e:
        return ""

data = {}
for u in uniq:
    out = curl(u)
    m = re.search(r'@@HTTP@@(\d{3})', out)
    code = m.group(1) if m else "000"
    body = out.split("@@HTTP@@")[0] if "@@HTTP@@" in out else out
    cover = ""
    views = None
    if code == "200":
        og = re.search(r'og:image"\s+content="([^"]+)"', body)
        if og:
            cover = og.group(1).split("?")[0].replace("&amp;", "&")
        vm = re.search(r'([0-9,]+)(?:<!--\s*-->\s*|\s+)plays\b', body)
        if vm:
            try:
                views = int(vm.group(1).replace(",", ""))
            except Exception:
                views = None
    data[u] = {"http": code, "cover": cover, "views": views}
    print(f"  {code}  views={views}  cover={'Y' if cover else 'N'}  {u[-55:]}")
    time.sleep(0.5)

def fmt(v):
    return "null" if v is None else str(v)

def repl(m):
    u = m.group(1)
    d = data.get(u, {})
    cover = d.get("cover", "")
    views = d.get("views")
    cov = "null" if not cover else '"' + cover.replace('"', '\\"') + '"'
    return 'url:"' + u + '", cover:' + cov + ', views:' + fmt(views) + '},'

new_html = re.sub(r'url:"([^"]+)"\},', repl, html)
open(SRC, "w", encoding="utf-8").write(new_html)

bad = {u: d for u, d in data.items() if d["http"] != "200"}
print("\nNON-200 urls:", len(bad))
for u, d in bad.items():
    print("  ", d["http"], u)
json.dump(data, open(SITE + "/ted_enrich_results.json", "w"), ensure_ascii=False, indent=1)
print("done. rewritten ted.js")
