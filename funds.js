/* 基金看板数据（持仓 4 只 · 支付宝） */
window.FUNDS_UPDATED = "2026-09-25";

/* 首次填充数据来源：罗浩本人支付宝 App 持仓截图，时点 2026-09-25。
   之后每日 15:30 自动化抓取覆盖。抓不到的字段一律留 null，页面显示「—」，绝不编造。 */
window.FUNDS_META = {
  src: "支付宝 App 持仓截图（首次填充）",
  date: "2026-09-25",
  note: "场外基金净值为 T+1，QDII 更晚，页面显示的是最近一个已公布净值日的数据，不是实时价。"
};

/* 持仓：amt=持有金额(元)｜dayPL=昨日收益｜holdPL=持有收益｜holdPct=持有收益率(小数) */
window.FUNDS_HOLD = [
  { n: "易方达全球成长精选混合(QDII)A", code: "012920", type: "QDII-混合", style: "海外",
    amt: 216.31, dayPL: -1.33, holdPL: -53.69, holdPct: -0.1989, auto: "定投",
    url: "https://fund.eastmoney.com/012920.html" },
  { n: "财通品质甄选混合A", code: "024480", type: "混合型-偏股", style: "A股",
    amt: 1411.79, dayPL: -55.83, holdPL: -284.24, holdPct: -0.1676, auto: "",
    url: "https://fund.eastmoney.com/024480.html" },
  { n: "中欧中证A500指数发起A", code: "022432", type: "指数型-股票", style: "A股",
    amt: 1.57, dayPL: -0.03, holdPL: -0.07, holdPct: -0.0428, auto: "",
    url: "https://fund.eastmoney.com/022432.html" },
  { n: "南方纳斯达克100指数发起(QDII)A", code: "016452", type: "QDII-股票", style: "海外",
    amt: 862.65, dayPL: -6.87, holdPL: 22.65, holdPct: 0.0276, auto: "定投",
    url: "https://fund.eastmoney.com/016452.html" }
];

/* 基准：沪深300 = 010300，中证A500 无直连代码，用 512500（中证A500ETF，场内）仅作参考链接 */
window.FUNDS_BENCH = [
  { n: "沪深300", code: "000300", url: "https://fund.eastmoney.com/000300.html" }
];

/* 风格暴露：按持仓真实投向归类，金额来自上面持仓 */
window.FUNDS_EXPOSURE = [
  { k: "A股", v: 1413.36 },
  { k: "海外", v: 1078.96 }
];
