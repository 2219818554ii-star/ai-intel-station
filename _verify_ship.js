// 上线前对着线上页面做一次内容级核对
const fs = require('fs'); const vm = require('vm');
const B = 'C:\\Users\\22198\\WorkBuddy\\2026-08-11-19-02-45\\ai_daily_site\\';
const html = fs.readFileSync(B + 'index.html', 'utf8');
const g = {}; g.window = {};
vm.runInContext(fs.readFileSync(B + 'competitions.js', 'utf8'),
                vm.createContext({ window: g.window, console }), { filename: 'c.js' });
const CP = g.window.COMP;

console.log('页面出现「官网状态」次数: ' + (html.match(/官网状态/g) || []).length);
console.log('warn-row 样式: ' + (html.includes('.warn-row .d-v') ? '已内联' : '缺失'));
const mk = CP.filter(c => c.n.indexOf('市场调查') >= 0)[0];
console.log('\n市调大赛  st=' + mk.st + ' | reg=' + mk.reg.slice(0, 46));
console.log('金相技能  url=' + CP.filter(c => c.n.indexOf('金相') >= 0)[0].url);
console.log('统计建模  url=' + mk.url);
const warnN = CP.filter(c => c.warn).length;
console.log('带官网状态标注: ' + warnN + ' 条');
const longWarn = CP.filter(c => (c.warn || '').indexOf('**') >= 0);
console.log('残留 markdown 星号: ' + longWarn.length);
