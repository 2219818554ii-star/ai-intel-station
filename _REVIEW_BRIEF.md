# AI 情报站 · 代码审核交接简报（给 Codex / 外部审查用）

> 生成：2026-10-15 阿禾。目的：让外部 AI（Codex 等）在不了解背景的情况下，也能审出真问题。
> 站点：GitHub Pages 单文件静态站。线上 https://2219818554ii-star.github.io/ai-intel-station/

## 1. 仓库与文件角色
路径：`C:/Users/22198/WorkBuddy/2026-08-11-19-02-45/ai_daily_site`

**唯一源文件（要审的）**
- `index.src.html` — 页面模板 + **全部渲染逻辑**：排行榜 / 基金看板 / 比赛 / 学习 / 讲坛 / 期刊精选 / 每日日报(实时 API)。esc() 转义、事件绑定都在这。
- 数据文件（`window.XXX = [...]`，构建时被内联）：
  - `ted.js`（40 条演讲，含 cover 封面图 / views 官网播放量）
  - `funds.js`（4 只基金持仓 + 深度档案 + 11 A股/4 美股重点个股）
  - `forum.js`（讲坛：25 系列 / 205 B站视频，bvid+play）
  - `matches.js`（活跃可报名比赛 8 条，另 5 条保留完整退役证据，不得丢身份）
  - `competitions.js`（全国比赛资源库 183 条）
  - `cqut.js`（重庆理工通知）
  - `rank.js`（排行榜：models/tools/combos/tables）
  - `magazines.js`（6 本期刊的已核实官方入口、文章元数据、核查状态）

**构建 / 校验 / 抓取脚本**
- `_build.py` — 读 index.src.html + 各 .js，内联生成 `index.html` / `gh-pages/index.html` / `ai_intel_station_standalone.html`
- `_selfcheck.js` — Node 跑 DOM 断言 + 各栏目新鲜度门 + 边界回归（要求 **0 失败**；通过数随新增护栏增加）
- 抓取脚本（"真刷新"用，非站点运行依赖）：`_refresh_funds.py`+`_apply_funds.py`（基金）、`_refresh_forum.py`（讲坛）、`ted_enrich.py`（TED 验活+封面+播放量）、`_prune_matches.py`（删过期比赛）、`_dedup_ted.py`（TED 去重）、`_recalc_funds.py`、`_preship.py`

**生成物（勿手改）**：`index.html`、`gh-pages/`、`ai_intel_station_standalone.html`

## 2. 构建 / 自检 / 推送命令（本机路径）
```powershell
& 'C:/Users/22198/.workbuddy/binaries/python/versions/3.13.12/python.exe' _build.py
& 'C:/Users/22198/.workbuddy/binaries/node/versions/22.22.2-6/node.exe' _selfcheck.js
& 'C:/Users/22198/.workbuddy/binaries/python/versions/3.13.12/python.exe' _magazines_refresh_regression.py
& 'C:/Users/22198/.workbuddy/binaries/python/versions/3.13.12/python.exe' _preship_regression.py
# Git executable: D:/Git/cmd/git.EXE
```
- push 走本机快橙 VPN 本地代理；VPN 掉线会报 502 / schannel 错——不是代码问题。

## 3. 项目铁律（审查时请尊重，别"修"成违规）
1. **每天对所有栏目实际核查，有真实变化才更新内容，绝不只滚 `*_UPDATED` 日期戳**（罗浩 2026-10-14 定）。无变化和访问受限必须如实记录，不能编造“今日新增”。
2. **绝不编造**：抓不到就留 null / 不写，页面显示「—」。
3. **基金账户数据**（amt/dayPL/holdPL/holdPct/cumulativePL/amtDate/navAt 及余额宝）按用户已授权更新的 **2026-10-15 清晰截图**与 `_funds_snapshot_2026-10-15.json`，**脚本/审查都不要改**；只刷新已核实的公开净值等信息。
4. 新鲜度门阈值：基金/重理工/比赛/排行=2 天，TED/讲坛/全国=3 天，超期自检 FAIL 是**故意**的护栏。
5. 涨跌配色遵循中国习惯：涨红 #e02424 / 跌绿 #16a34a。

## 4. 近期改动（review 重点）
- `354c692`（10-14 全改）：比赛删 3 条过期 + 移除空 miit 分类（剩 13）；排行榜 SWE 表按分降序；TED 去重 7 条 + 补 7 条经典（回 40 唯一、全带封面）；排行榜 legend 补 TB2.1/TB4.0 口径说明；自检条目门槛 15→10（诚实反映剪枝，非放水）。
- `fd78081`：排行榜 models/tools/combos 渲染前按分降序、无分沉底；TED 主按钮改「TED官网直达」直链已验活地址。
- 10-15 自动任务已恢复：`d5630f9` 基金刷新、`6974e65` 比赛日更（180→182）。

## 5. 建议 Codex 重点查
- [ ] `index.src.html` 渲染函数有无 JS 错误 / 边界（空数据、null、转义）。
- [ ] 排序是否真的生效（models/tools/combos/aa/tb/swe 全降序、无分沉底）——注意排序在**渲染时**做，数据数组保持原序是正常的。
- [ ] 链接死链：ted 40 / matches 13 / competitions 182 / forum 241（curl 验活）。
- [ ] 基金估算一致性：估算市值=amt×unit/navAt；trend 文字里的价格/昨收是否与 price/chg 一致。
- [ ] TED 去重是否干净（应 40 唯一、0 重复）。
- [ ] selfcheck 是否被"放水"（门槛改动是否有正当理由注释）。
- [ ] esc() 是否覆盖所有用户可见插值（防 XSS/破版）。
- [ ] 移动端 / 窄屏排版（排行榜大表格横滑、TED/比赛卡片）。
- [ ] 构建产物与源是否一致（改 .js 后是否忘了 _build.py）。

## 6. 已知"不是 bug"的坑（省得误报）
- 基金持仓是 06-30 二季报 top10，三季报(截至 9-30)预计 10 月中下旬披露后需复核——现在旧是正常的。
- QDII 基金(012920/016452)净值 T+2 滞后，比 A股基金慢一天——正常。
- `_build.py` 日志里括号数字是文本匹配计数，不是条目数；以运行时自检为准（10月19日理工通知294、全国赛事183）。
- TED 个别条目 views=null（该 TED 页面未暴露播放数）——按"不编造"留空，正常。
- 排行榜 TB 列大量留空：官方 8/29 已把 Terminal-Bench 升级到 4.0，很多模型只有 TB4.0 分、无 TB2.1，故留空——正常（legend 已说明）。

## 7. 2026-10-19 新增「期刊精选」维护约定
- 第9栏 `#magazines`：商界、三联生活周刊、第一财经（原第一财经周刊）、博客天下、人物、环球人物。保留官方出处，提供多词搜索、主题/刊物筛选、独立收藏及已读记录、分批阅读与手机横滑选刊。
- `magazines.js` 中 `MAGAZINES_CHECKED` / 每刊 `checkedAt` 表示实际核查日；`MAGAZINE_ARTICLES[].publishedAt` 只填原文明示的单篇发布日期，未知留 `null`。三联期刊日期不能代替单篇日期。原文可能需要订阅或登录，本站只保存元数据和独立导读。
- 初始逐篇来源与身份核实见 `_magazines_sources_a.json`、`_magazines_sources_b.json`；动态核查报告 `_magazines_refresh.json` 保留每刊尝试结果、当次确切元数据及上次独立证据。不得用数据自己给自己认证或删掉失败时的原文。
- 先运行 `_refresh_magazines.py --dry-run --timeout 8` 可预览而不写文件；正式运行 `_refresh_magazines.py --timeout 8` 更新源数据及报告，然后构建、跑零失败自检与两组 Python 回归，再验证浏览器及上线版本。
- 抓取只允许配置的官方 HTTPS 域名，空页面、超时及访问保护要保留旧内容；商界入口为投资界认证官方账号，明确是往期文章。人物、博客天下使用博雅官方分刊频道，不抓混合首页。环球人物暂无稳定直接解析，需维护任务继续核查官方网页/索引，不能声称脚本六刊全部成功。
- 现有每日09:00任务已扩展到期刊。它负责实际核查、必要优化、生成、检查和上线；内容未变化时不编造新增。阅读记录仅保存在当前浏览器，不随公开内容更新清空。
