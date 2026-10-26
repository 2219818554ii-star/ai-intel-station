# AI 情报站 · 代码审核交接简报（给 Codex / 外部审查用）

> 生成：2026-10-15 阿禾。目的：让外部 AI（Codex 等）在不了解背景的情况下，也能审出真问题。
> 站点：GitHub Pages 单文件静态站。线上 https://2219818554ii-star.github.io/ai-intel-station/

## 1. 仓库与文件角色

### 2026-10-26 当前授权与新版架构（优先于下方旧方案）

- 用户明确授权重设计个人工作台，并公开本人已审核的任务执行文字和记录。科研正文现在原生展示在本主站，不能再依赖国外登录页才能阅读。原私有 Sites 保持本人权限；不改变 Google 表格分享权限。公开内容仍排除凭据、联系方式、具体本机证据路径和未经审核的原始记录。
- `research-data.json` 的136项六字段基线保持；`research-details.json` 是逐项对齐并经固定审核摘要校验的执行正文及5条记录。`_sync_research_details.py` 严格验证双文件版本、来源、字段、审核release与digest，不能用重新计算digest放行未经审核的新材料。源日期仍为10/22，不把迁移日当新实验进展。
- 首页“今天”按北京时间组织任务、未来7天、条件缺口、研究生相关校园通知、实有截止机会和编辑精选。11个唯一栏目路由，桌面侧栏、手机底栏/抽屉、全站搜索；旧日期hash仍通向日报。`workspace.js`/`workspace.css` 由构建内联；离线仅缓存同域发布资料，不缓存外部API、登录页和云写请求。
- `cloud.js` 连接独立个人同步服务，需设备授权。收藏/已读/已看先保留本机，再按字段版本CAS和操作ID同步；旧设备不能默默覆盖云端新选择，冲突显示并允许本人重试。无配置/断网保留本机数据，不伪称跨设备同步已成功。
- 云端科研安排作为经过设备认证的个人覆盖层，与审核静态基线分开。只允许原136编号的状态、建议日期、预计主动工时、用户补充进展；不能修改任务正文、原实验结果和实际工时。模型只生成差异预览，本人应用后才同步并可撤销。静态事实版本变化时不自动套旧覆盖层。
- DeepSeek默认，OpenAI可选；各用本人API密钥。密钥经HTTPS发送到独立服务并加密存储，绝不进入本公开仓库、HTML、URL、日志或自动维护提示。API未实调前不得声称模型连通。服务源码位于公开仓库外 `C:/Users/22198/Documents/ChatGPT/学习/luohao-cloud-20261026`；自动维护不得初始化/清空云数据库或覆盖个人云安排。
- 用户选择“1”授权CQUT仅在官网全受阻时保留旧内容：原两天内容门仍为默认；例外须当日全部通知与全部入口的真实失败证据、核查日前独立Git基线完全一致，并在页面明确“受阻/保留旧内容”和原内容日/核查日。`_source_freshness.js`与38项回归验证此例外；其他日期、来源、基金、身份护栏不变。有真实新通知时走原新鲜内容路径，不套例外。
- 上线除原检查外还需 `_research_details_regression.py`、云服务SQL/认证/CAS/幂等/撤销回归、主站真实窄屏/键盘/离线和双设备交互验证。模型接口测试与合成模型响应测试必须分开报告；国内访问能力不能由单次本机HTTP成功扩大为全国网络保证。

### 2026-10-21 科研原生栏目（当前活动方案）

- 用户只看本网站科研栏目执行，在当前对话反馈；复用现有私有Sites作为按任务编号打开的详情页，不新建站点；日常入口保留在本网站。`#research` 内直接展示安全摘要卡片、工时、未来7天和风险。
- 数据源为 Google `AI Daily｜科研栏目展示数据（仅限公开白名单）`，ID `1sHUITtFaKh5NV64wvlErZRuR3B3DZq-V9NCQuGb-FMc`，`网站数据!A1:F1000`。只允许六列：任务编号、建议日期、展示任务、公开状态、预计主动小时、分类。完整科研总表和实验原始记录不可写入公开仓库。
- 展示表当前仍为私有，网站使用连接器读回并审核后的 `research-data.json`。不修改表格分享权限，不绕过Google授权；“Google表格修改后立刻被匿名网页读取”未启用。每次用户反馈后维护原任务与展示表，再同步发布网站，用户刷新可见。
- 导入格式：仓库外临时JSON包含 spreadsheetId、sheetName、sourceUpdatedAt、syncedAt、values；用 `_sync_research.py --input <绝对路径>` 审核导出。文件ID和表头必须匹配指定展示表；标题/分类/状态须在审核白名单，日期、重复ID和工时均校验，未知内容停止导出，不能静默丢弃。
- 若展示表新增已审核的高层次标题或分类，先检查无原始数据、配方、路径、联系人和具体出行信息，再同步调整 `_sync_research.py` / `research.js` 白名单并测试。不得把审核改成接受任意字段。
- `research.js` 只读取本站 `research-data.json`，打开科研栏目、返回页面或手动刷新时检查发布数据（no-store+时间参数），失败保留有效摘要并明确提示，不伪称同步成功。构建时内联JSON与JS为本地/离线回退；file://不能跨设备访问。
- 2026-10-21完成状态修正：T002收窄为资料整理提交（已完成），原有原机/接线/映射核验保留由T013/T015跟进，变更写入总表CHG-008。任务执行完成退出待办，证据验收仍独立；公开面板显著展示已完成事项，不以建议日期推断实际完成日期。公开标题白名单新增“科研资料整理提交”，仍仅六字段。
- 今日采用北京时间；未来7天不含今天；待条件、未定日期、逾期、缺工时均提醒。工时为预计主动工时，不是实验实测耗时；已标记完成不能等同证据验收通过。
- 构建输入新增 `research.js` / `research-data.json`。更新数据后必须运行 `_build.py`、`_selfcheck.js`、`_research_export_regression.py`、`_preship_regression.py`，确认三份产物和线上JSON；校验原有账户及赛事身份。回归计数随新功能护栏增加，不降低旧护栏。
- 实验记录入口复用同一私有项目 /?view=journal，任务详情可按 task 参数筛选关联记录。原总表的科研日报扩展为22列，记录ID稳定；任务与实际记录通过同版releaseId导出发布。网页表单仅生成反馈，用户在本对话提交后才由助手核对写入，不能宣称自动保存。主动工时、等待、交通、休息与起止跨度分别记录；未知值为空，不根据计划或跨度推算实做。
- 继续保留既有网站备份。私有详情复用既有项目 appgprj_6ad8592214848191bf10b277ad94cbb4：/?task=T001 仅显示指定执行单，详情默认展开；保留本人权限。每次调整任务需同步私有总表详情与公开展示表摘要，分别部署后核对编号、排期、状态、工时一致。公开仓库始终只含六字段摘要及私有详情入口，不含完整内容或凭据。

路径：`C:/Users/22198/WorkBuddy/2026-08-11-19-02-45/ai_daily_site`

**唯一源文件（要审的）**
- `index.src.html` — 页面模板 + **全部渲染逻辑**：排行榜 / 基金看板 / 比赛 / 学习 / 讲坛 / 期刊精选 / 每日日报(实时 API)。esc() 转义、事件绑定都在这。
- 数据文件（`window.XXX = [...]`，构建时被内联）：
  - `ted.js`（40 条演讲，含 cover 封面图 / views 官网播放量）
  - `funds.js`（4 只基金持仓 + 深度档案 + 11 A股/4 美股重点个股）
  - `forum.js`（讲坛：25 系列 / 205 B站视频，bvid+play）
- `matches.js`（当前报名线索 5 条，其中1条校内截止年份待核实，另8条保留完整退役证据；受阻来源不冒充全量报名核验，不得丢身份）
  - `competitions.js`（全国比赛资源库 183 条）
  - `cqut.js`（重庆理工通知）
  - `rank.js`（排行榜：models/tools/combos/tables）
- `magazines.js`（19 本期刊的官方入口、文章元数据、核查状态；当前853篇，48篇编辑精选）

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
& 'C:/Users/22198/.workbuddy/binaries/python/versions/3.13.12/python.exe' _magazines_cn_regression.py
& 'C:/Users/22198/.workbuddy/binaries/python/versions/3.13.12/python.exe' _magazines_rss_regression.py
& 'C:/Users/22198/.workbuddy/binaries/python/versions/3.13.12/python.exe' _magazines_pipeline_regression.py
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
- `_build.py` 日志里括号数字是文本匹配计数，不是条目数；以运行时自检为准（10月20日理工通知308、全国赛事183）。
- TED 个别条目 views=null（该 TED 页面未暴露播放数）——按"不编造"留空，正常。
- 排行榜 TB 列大量留空：官方 8/29 已把 Terminal-Bench 升级到 4.0，很多模型只有 TB4.0 分、无 TB2.1，故留空——正常（legend 已说明）。

## 7. 2026-10-19 新增「期刊精选」维护约定
- 第9栏 `#magazines`：已由6刊扩展19刊，另增中国新闻周刊、新周刊、南方人物周刊、财经、财新周刊、南方周末、Scientific American、Nature、Science News、The Atlantic、The Economist、Smithsonian、Quanta。保留官方出处，支持5类主题、原文语言、刊物与阅读状态组合，折叠书架避免挤压正文。
- `magazines.js` 中 `MAGAZINES_CHECKED` / 每刊 `checkedAt` 表示实际核查日；`MAGAZINE_ARTICLES[].publishedAt` 只填原文明示的单篇发布日期，未知留 `null`。三联期刊日期不能代替单篇日期。原文可能需要订阅或登录，本站只保存元数据和独立导读。
- 初始逐篇来源与身份核实见 `_magazines_sources_a.json`、`_magazines_sources_b.json`；动态核查报告 `_magazines_refresh.json` 保留每刊尝试结果、当次确切元数据及上次独立证据。不得用数据自己给自己认证或删掉失败时的原文。
- 先运行 `_refresh_magazines.py --dry-run --timeout 8` 可预览而不写文件；正式运行 `_refresh_magazines.py --timeout 8` 更新源数据及报告，然后构建、跑零失败自检与两组 Python 回归，再验证浏览器及上线版本。
- 抓取只允许配置的官方 HTTPS 域名，空页面、超时及访问保护要保留旧内容；商界入口为投资界认证官方账号，明确是往期文章。人物、博客天下使用博雅官方分刊频道，不抓混合首页。环球人物暂无稳定直接解析，需维护任务继续核查官方网页/索引，不能声称脚本六刊全部成功。
- 现有每日09:00任务已扩展到期刊。它负责实际核查、必要优化、生成、检查和上线；内容未变化时不编造新增。阅读记录仅保存在当前浏览器，不随公开内容更新清空。
- 2026-10-25阅读记录补强：收藏/已读保存当前文章的标题、刊物、单篇日期及导读快照。滚出当期列表后，仅在收藏/已读中保留原文并注明信息可能变化，不回流最新总量、官方热榜或编辑精选。旧版仅URL记录不猜标题与日期；人物/博客天下等共用域无法辨别刊物时给中性官方入口，提示清除不兼容筛选。长列表标记后焦点接续原位置的邻项，空列表才返回结果标题。
- 三类榜单分开：最新只用单篇明确日期；来源热榜只用南方周末热门、Quanta过去一周Most Read、Science News Trending的真实原站顺序，展示原榜、名次和核查日，各刊分别排名；编辑精选由 `_magazines_editorial.json` 明确选择，逐篇给出阅读切入点，配置标题/URL/刊物精确匹配才生效。
- `_magazines_cn.py` / `_magazines_rss.py` 是官方HTML/SSR/API与RSS1/RDF/RSS2/Atom的独立解析器。刷新可用 `--workers 3 --timeout 6` 并行核查，失败保留旧文章与榜单原核查日；新榜成功时去掉落榜标记但保留原文。报告的独立旧证据会跨失败轮次延续，不能用数据自己认证数据。
- `_magazines_catalog_baseline.json` 保留已核实刊物身份、域名和基础文章量；扩展证据在 `_magazines_expansion_cn.json` / `_magazines_expansion_world.json`。元数据、热榜来源与编辑精选均有额外回归，不能只把下拉控件做出来而不实际排序。
- 其他栏目：TED按精选、真实累计播放量、演讲年份排序，播放采集日 `TED_VIEWS_CAPTURED_AT` 独立于内容更新；讲坛系列按已收录视频累计播放合计、进入系列后按单视频播放，不去重观众且非实时；通知按明确原文日期或研究生/奖助/考试分组优先；比赛推荐为已有适配建议，不能冒称报名热度。新增 `_section_rankings_regression.js` 已接入自检。
- 10月25日新增逐视频 `playCapturedAt`：完整官方view响应核对BV、标题和计数后才能更新该条；无新证据的播放数和默认 `FORUM_PLAY_CAPTURED_AT` 保留。局部成功不能改称全量刷新，混合日期须显示非同期采样及逐卡日期，对应 `_forum_plays_日期.json` 独立证据受自检约束。基金 `FUNDS_CHECKED` 与 `FUNDS_UPDATED` 分开；净值未变时内容日及原应用证据不动，新的核查记录另存并在页面明确显示。
