# -*- coding: utf-8 -*-
"""T49: 重写 view-learn——删掉前置的指令卡/公式/分工/避坑，只留 AI 教学资源库，
分类扩到 8 类、条目扩到 ~46 条；视频类 B站优先（永不 404），海外源配国内备份。"""
import io
import re
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding="cp936", errors="replace")

P = "index.src.html"
s = io.open(P, encoding="utf-8").read()


def bs(kw):
    return "https://search.bilibili.com/all?keyword=" + quote(kw)


def item(title, url, plat, desc, tags):
    t = "".join('<span class="tag">%s</span>' % x for x in tags)
    return ('        <div class="rsrc-item">\n'
            '          <a class="rsrc" href="%s" target="_blank" rel="noopener noreferrer">%s'
            '<span class="plat">%s</span></a>\n'
            '          <p>%s</p>\n'
            '          %s\n'
            '        </div>\n' % (url, title, plat, desc, t))


def grid(items):
    return '      <div class="rsrc-grid">\n' + "".join(items) + '      </div>\n'


def sec(title, items):
    return '\n    <h4 class="cat-h">%s</h4>\n' % title + grid(items)


IT = []

# ---------- 一、零基础看懂 AI ----------
IT.append(sec('🎬 一、零基础看懂 AI（科普视频，中文优先）', [
    item("李宏毅《生成式AI导论 2025》", "https://www.bilibili.com/video/BV1KUNjzpEpM/", "B站",
         "台大教授，中文授课，明确写“不需任何先验知识”。从 Transformer 一路讲到 DeepSeek、RLHF，是最顺的中文入门。",
         ["零基础", "中文", "视频"]),
    item("李宏毅《机器学习 2025》", "https://www.bilibili.com/video/BV1aiADewEBC/", "B站",
         "已授权完整版，今年内容偏实际应用、紧跟大模型趋势。想系统打底就看这一套。",
         ["进阶", "中文", "视频"]),
    item("3Blue1Brown 官方账号（中文字幕）", "https://space.bilibili.com/88461692", "B站",
         "用动画把神经网络、梯度下降、Transformer、扩散模型讲透，公认最直观。B站官方号带中文字幕，不用翻墙。",
         ["零基础", "视频", "动画"]),
    item("Karpathy：How I use LLMs / Intro to LLMs", "https://www.youtube.com/@AndrejKarpathy", "YouTube（需梯子）",
         "前 OpenAI/Tesla AI 总监。一场讲清 LLM 原理，一场讲日常怎么用。B站搜“Karpathy”有大量带字幕搬运。",
         ["零基础", "视频", "英文"]),
    item("B站搜：大模型 原理 入门", bs("大模型 原理 入门"), "B站",
         "中文圈讲 Transformer/大模型原理的精选合集，挑播放量高、时间近的看。",
         ["零基础", "中文", "视频"]),
    item("B站搜：AI 科普 通俗", bs("AI 科普 通俗"), "B站",
         "10 分钟级短视频，通勤/吃饭时刷两条，攒常识比刷段子划算。",
         ["零基础", "中文", "短视频"]),
]))

# ---------- 二、科研人用 AI 干活 ----------
IT.append(sec('🛠 二、科研人用 AI 干活（实操视频，对你最实用）', [
    item("做科研的大师兄", bs("做科研的大师兄"), "B站",
         "博士博主，专讲 AI 辅助科研的完整工作流：查文献、读文献、写论文、画图，贴合研究生日常。",
         ["科研", "中文", "视频"]),
    item("同济子豪兄", bs("同济子豪兄"), "B站",
         "同济大学讲师，精讲论文系列（LeNet/AlexNet/Transformer…）和 AI 工具实操，讲得细、不跳步。",
         ["科研", "中文", "视频"]),
    item("天Jiang 学长", bs("天JIANG"), "B站",
         "研究生视角的 AI 工具教程：文献管理、论文写作、数据分析实操，节奏适合跟练。",
         ["科研", "中文", "视频"]),
    item("B站搜：AI 写论文 教程", bs("AI 写论文 教程"), "B站",
         "从选题、文献综述到初稿润色的 AI 实操合集。⚠️ 看完记住底线：AI 出初稿，数值和引用你必须亲自核对。",
         ["科研", "中文", "实操"]),
    item("B站搜：ChatGPT 科研 使用", bs("ChatGPT 科研 使用"), "B站",
         "科研场景下怎么问出好答案：喂文献、定格式、要表格。核心是“给背景+给约束”。",
         ["科研", "中文", "实操"]),
    item("B站搜：AI 文献综述", bs("AI 文献综述"), "B站",
         "用 AI 快速过 50 篇文献的方法：先摘要后精读、建对比表。配合你改第三章 SCI 正好用得上。",
         ["科研", "中文", "实操"]),
    item("B站搜：AI 润色 论文", bs("AI 润色 论文"), "B站",
         "英译/润色的指令写法与演示，重点看“保留数值、不改术语”的约束怎么下。",
         ["科研", "中文", "实操"]),
]))

# ---------- 三、AI 工具上手 ----------
IT.append(sec('🤖 三、AI 工具上手（一个一个学会用）', [
    item("B站搜：ChatGPT 教程", bs("ChatGPT 教程"), "B站",
         "从注册到高级用法（自定义指令、数据分析、联网）的中文合集，你有 GPT 会员，直接能跟练。",
         ["工具", "中文", "视频"]),
    item("B站搜：DeepSeek 教程", bs("DeepSeek 教程"), "B站",
         "国产模型代表，中文理解好、免费额度足。推理模式（R1）做数学/逻辑题很强，数模比赛能派上用场。",
         ["工具", "中文", "免费"]),
    item("B站搜：Kimi 教程", bs("Kimi 教程"), "B站",
         "长文本之王：整本论文、几十篇 PDF 一次丢进去总结。改第三章时“整篇通读”就靠这类。",
         ["工具", "中文", "长文本"]),
    item("B站搜：AI 做 PPT 教程", bs("AI 做 PPT 教程"), "B站",
         "组会汇报、竞赛答辩的 PPT 提效流：大纲→内容→排版一键生成，再手动调细节。",
         ["工具", "中文", "实操"]),
    item("B站搜：AI 绘图 教程", bs("AI 绘图 教程"), "B站",
         "Midjourney / Stable Diffusion 入门，做海报、示意图、竞赛展板用得上。",
         ["工具", "中文", "实操"]),
    item("B站搜：NotebookLM 教程", bs("NotebookLM 教程"), "B站",
         "Google 出品：把你的文献喂进去，它只基于你给的材料回答，幻觉少，还能生成播客式讲解。",
         ["工具", "视频", "英文"]),
    item("B站搜：豆包 AI 教程", bs("豆包 AI 教程"), "B站",
         "字节全家桶，手机端好用，语音对话+图片识别适合随手问。",
         ["工具", "中文", "免费"]),
    item("B站搜：Claude 教程", bs("Claude 教程"), "B站",
         "长文写作与代码质量口碑最好的一家，你的 Claude Code 就是它——先看别人怎么用。",
         ["工具", "中文", "视频"]),
]))

# ---------- 四、数据处理与编程 ----------
IT.append(sec('📊 四、数据处理与编程（零基础能跟，比赛直接用）', [
    item("李沐《动手学深度学习》", "https://www.bilibili.com/video/BV1daQAYuEYm/", "B站",
         "亚马逊首席科学家带读经典教材，代码+理论并行。数模要用神经网络时再啃，平时收藏。",
         ["进阶", "中文", "视频"]),
    item("B站搜：Python 零基础 入门", bs("Python 零基础 入门"), "B站",
         "数模/数据处理的地基。挑一套播放量最高的跟完前 20 集，能跑通脚本就够用。",
         ["零基础", "中文", "视频"]),
    item("B站搜：Origin 数据处理 教程", bs("Origin 数据处理 教程"), "B站",
         "你画谱图/拟合就用它：峰形处理、拟合报告、批量出图，直接对着自己的数据跟练。",
         ["科研", "中文", "实操"]),
    item("B站搜：Excel 数据分析 教程", bs("Excel 数据分析 教程"), "B站",
         "透视表+基础函数+图表，处理实验记录、值班表足够用，性价比最高的一门“手艺”。",
         ["零基础", "中文", "实操"]),
    item("B站搜：SPSS 教程", bs("SPSS 教程"), "B站",
         "统计建模大赛（市场调查/统计建模）的常用工具，点鼠标就能跑回归、方差分析，不用写代码。",
         ["比赛", "中文", "实操"]),
    item("B站搜：MATLAB 教程", bs("MATLAB 教程"), "B站",
         "数模三大件之一，数值计算/绘图现成模板多。比赛前过一遍基础语法即可。",
         ["比赛", "中文", "视频"]),
]))

# ---------- 五、系统权威课 ----------
IT.append(sec('📚 五、系统权威课（想系统学就上，多数免费）', [
    item("DeepLearning.AI（Andrew Ng）", "https://www.deeplearning.ai/", "官网",
         "吴恩达出品，短课制，ChatGPT Prompt Engineering for Developers 等课免费且质量极高。",
         ["系统课", "免费", "英文"]),
    item("Google 机器学习速成课 MLCC", "https://developers.google.com/machine-learning/crash-course", "官网",
         "谷歌官方免费课，交互式练习+视频，经典 ML 概念一网打尽（国内访问偶慢，可等或挂梯子）。",
         ["系统课", "免费", "英文"]),
    item("Harvard CS50 AI with Python", "https://cs50.harvard.edu/ai/", "官网",
         "哈佛名课的 AI 分支，免费公开全部作业与讲义，英文配字幕。",
         ["系统课", "免费", "英文"]),
    item("fast.ai《Practical Deep Learning》", "https://www.fast.ai/", "官网",
         "自上而下教学法：第一课就训练出能用的模型，适合“先跑通再理解”。",
         ["系统课", "免费", "英文"]),
    item("Elements of AI（赫尔辛基大学）", "https://www.elementsofai.com/", "官网",
         "面向全人类的 AI 入门课，几乎不涉数学，有中文版，适合完全零基础建立框架。",
         ["零基础", "免费", "中文"]),
    item("MIT 6.S191 深度学习导论", "https://introtodeeplearning.com/", "官网",
         "MIT 一年一更新的公开课， slides 和视频全公开，讲前沿讲得清楚。",
         ["系统课", "免费", "英文"]),
    item("Hugging Face Learn", "https://huggingface.co/learn", "官网",
         "NLP/LLM 实战课（免费），想跑通第一个大模型任务从这进。",
         ["进阶", "免费", "英文"]),
    item("Kaggle Learn", "https://www.kaggle.com/learn", "官网",
         "边做边学的微课程，Python/ML/数据可视化，每门几小时，配比赛数据练手最合适。",
         ["免费", "实操", "英文"]),
]))

# ---------- 六、提示词 / 指令工程 ----------
IT.append(sec('✍️ 六、提示词 / 指令工程（专练“下指令”）', [
    item("OpenAI 官方提示工程指南", "https://platform.openai.com/docs/guides/prompt-engineering", "官网",
         "六大策略（写清楚指令、给参考文本、拆任务、给思考时间、外部工具、系统测试），官方出品最权威。",
         ["提示词", "英文", "官方"]),
    item("Anthropic 提示工程文档", "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview", "官网",
         "Claude 视角的提示工程，章节化、示例多，配套 Prompt Library 可直接抄模板。",
         ["提示词", "英文", "官方"]),
    item("Learn Prompting（开源教程）", "https://learnprompting.org/", "官网",
         "最流行的开源提示词课程，从零到高级，有中文翻译版本。",
         ["提示词", "免费", "中文"]),
    item("Prompt Engineering Guide（DAIR.AI）", "https://www.promptingguide.ai/", "官网",
         "社区维护的提示工程大全，技术多、论文链接全，进阶查阅首选（有中文版）。",
         ["提示词", "免费", "中文"]),
    item("B站搜：提示词 技巧", bs("提示词 技巧"), "B站",
         "中文视频版的提示词课，看着别人怎么写、怎么迭代，比自己啃文档快。",
         ["提示词", "中文", "视频"]),
]))

# ---------- 七、图文 / 博客 ----------
IT.append(sec('📝 七、图文 / 博客（随时翻的参考）', [
    item("The Batch（DeepLearning.AI 周报）", "https://www.deeplearning.ai/the-batch/", "官网",
         "吴恩达每周一封的 AI 时事信，英文简单、观点克制，适合练阅读顺便跟进展。",
         ["资讯", "英文", "免费"]),
    item("Lilian Weng Blog", "https://lilianweng.github.io/", "官网",
         "前 OpenAI 安全研究副总裁的长文博客，每篇都是某方向（Agent/扩散模型/RLHF）的综述级整理。",
         ["进阶", "英文", "深度"]),
    item("Google Gemini 提示策略", "https://ai.google.dev/gemini-api/docs/prompting-strategies", "官网",
         "你有 Gemini 会员：这份官方策略讲清系统指令、few-shot、输出格式怎么定。",
         ["提示词", "英文", "官方"]),
]))

# ---------- 八、AI 资讯跟进 ----------
IT.append(sec('📰 八、AI 资讯跟进（中文，天天能看）', [
    item("机器之心", "https://www.jiqizhixin.com/", "官网",
         "国内最专业的 AI 媒体，论文解读和产业动态都全，网页直接看不用装 App。",
         ["资讯", "中文", "免费"]),
    item("量子位", "https://www.qbitai.com/", "官网",
         "更新快、话题面广，新模型新工具第一时间报道，适合每天扫一眼标题。",
         ["资讯", "中文", "免费"]),
    item("B站搜：AI 日报", bs("AI 日报"), "B站",
         "每天几分钟的 AI 新闻合集视频，通勤时听，不掉队。",
         ["资讯", "中文", "短视频"]),
]))

NEW = (
    '<div id="view-learn" class="view" style="display:none" role="tabpanel" aria-labelledby="tab-learn">\n'
    '    <div class="view-head"><h2>📚 AI 上手 · 教学视频与课程库</h2>\n'
    '      <p>这页只放 <b>AI 教学</b>：8 大类 46+ 条，中文优先、B站直链优先（点得开、不用翻墙）。'
    '别囤课——<b>看完一个再看下一个</b>，今天挑一条看 15 分钟就赢。</p></div>\n'
    '\n'
    '    <style>\n'
    '      .rlib-intro{font-size:14px;color:#374151;line-height:1.75;margin:6px 0 14px}\n'
    '      .rlib-intro b{color:var(--ink)}\n'
    '      .cat-h{font-size:15px;margin:18px 0 10px;color:var(--brand);font-weight:700}\n'
    '      .rsrc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px;margin-bottom:4px}\n'
    '      .rsrc-item{border:1px solid var(--line);border-radius:10px;padding:12px 13px;background:#fcfdff;box-shadow:var(--shadow)}\n'
    '      .rsrc-item .rsrc{font-size:14.5px;font-weight:700;color:var(--brand);text-decoration:none;word-break:break-word}\n'
    '      .rsrc-item .rsrc:hover{text-decoration:underline}\n'
    '      .plat{display:inline-block;font-size:11px;font-weight:600;color:#6b7280;background:#eef2f7;border-radius:6px;padding:1px 6px;margin-left:6px;vertical-align:middle}\n'
    '      .rsrc-item>p{font-size:13px;color:#374151;line-height:1.6;margin:7px 0 9px}\n'
    '      .tag{display:inline-block;font-size:11px;color:#0f766e;background:#e6f7f3;border:1px solid #b8e6dd;border-radius:999px;padding:1px 8px;margin:2px 5px 0 0}\n'
    '      .rlib-note{font-size:13px;color:#374151;line-height:1.7;margin-top:14px;padding:10px 12px;background:#fff7ed;border:1px solid #fed7aa;border-radius:10px}\n'
    '    </style>\n'
    + "".join(IT) +
    '    <div class="rlib-note">💡 <b>怎么用这页：</b>① 零基础先看「一」里李宏毅 2 集；② 要干活直接跳「二/三/四」挑对口的一条跟练；'
    '③ 海外标注「需梯子」的，挂着快橙再点，或优先用同条的 B站 备选。</div>\n'
    '</div>\n\n'

)

new_s, k = re.subn(r'<div id="view-learn"[\s\S]*?(?=<div id="view-ted")', NEW, s)
assert k == 1, "替换数 %d" % k
io.open(P, "w", encoding="utf-8").write(new_s)
n_items = len(re.findall(r'class="rsrc-item"', NEW))
print("view-learn 已重写：%d 个条目、%d 个分类" % (n_items, NEW.count('cat-h')))
