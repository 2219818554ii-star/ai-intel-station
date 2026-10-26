'use strict';
// User approved choice 1 on 2026-10-26: retain blocked CQUT content with proof.
// Cases below reject the tempting shortcuts instead of raising date thresholds.
const test=require('node:test'),assert=require('node:assert/strict');
const {validateCQUTFreshness,beijingDay,dayNumber}=require('./_source_freshness.js');
function example(){
  const notices=[{t:'甲通知',url:'https://www.cqut.edu.cn/info/1/1.htm',date:'2026-10-23',sum:'保留原摘要',tag:'grad',cat:'school'},
    {t:'乙通知',url:'https://chem.cqut.edu.cn/info/1/2.htm',date:'2026-10-22',sum:'学院原摘要',tag:'rs',cat:'college'}];
  const sources={teach:[{n:'研究生院',u:'https://yjsy.cqut.edu.cn/'}],college:[{n:'化学化工学院',u:'https://chem.cqut.edu.cn/'}]};
  return {key:'CQUT_UPDATED',today:'2026-10-26',now:'2026-10-26T12:00:00+08:00',
    data:{updated:'2026-10-23',checked:'2026-10-26',status:'blocked',state:{contentDate:'2026-10-23',checkDate:'2026-10-26',evidence:'_content_review_2026-10-26.json'},notices,sources},
    report:{reviewedAt:'2026-10-26',attemptedAt:'2026-10-26T09:00:00+08:00',completedAt:'2026-10-26T09:10:00+08:00',cqutContentUpdatedBefore:'2026-10-23',cqutSnapshotsBefore:structuredClone(notices),
      sources:[...notices.map(x=>x.url),...Object.values(sources).flat().map(x=>x.u)].map(url=>({url,checkedAt:'2026-10-26',checkedAtTime:'2026-10-26T09:05:00+08:00',status:412,usableContent:false,error:'HTTP Error 412: Precondition Failed',limitation:'Access-protected response; retained old content.'}))},
    baseline:{commit:'a'.repeat(40),committedAt:'2026-10-25T20:00:00+08:00',updated:'2026-10-23',notices:structuredClone(notices),sources:structuredClone(sources)},
    disclosure:{visible:true,text:'官网核查受阻 · 保留旧内容；内容更新2026-10-23；最近核查2026-10-26。'}};
}
function rejected(name,change){test(name,()=>{const input=example();change(input);assert.equal(validateCQUTFreshness(input).ok,false);});}
test('原两天内容主路径无需受阻报告',()=>{const x=example();x.data.updated='2026-10-25';delete x.data.status;delete x.data.state;delete x.report;delete x.baseline;delete x.disclosure;assert.equal(validateCQUTFreshness(x).mode,'fresh-content');});
test('真实受阻、全来源覆盖、原快照与原日期完整时允许保留',()=>{const r=validateCQUTFreshness(example());assert.equal(r.ok,true);assert.equal(r.mode,'blocked-retained');assert.equal(r.contentAge,3);assert.equal(r.requiredURLs,4);});
test('真实核查可保留到第二天和第二天后的边界',()=>{const x=example();x.today='2026-10-28';x.now='2026-10-28T12:00:00+08:00';const r=validateCQUTFreshness(x);assert.equal(r.ok,true);assert.equal(r.checkAge,2);});
rejected('不能给其他栏目使用学校受阻例外',x=>{x.key='RANK_UPDATED';});
rejected('旧内容没有blocked状态不能保留',x=>{delete x.data.status;});
rejected('缺少独立dated报告必须失败',x=>{delete x.report;});
rejected('核查超过两天必须再次实际抓取',x=>{x.today='2026-10-29';x.now='2026-10-29T12:00:00+08:00';});
rejected('未来核查日不能当新鲜证据',x=>{x.data.checked='2026-10-27';});
rejected('报告核查日与CHECKED不一致拒绝',x=>{x.report.reviewedAt='2026-10-25';});
rejected('状态contentDate不能滚动',x=>{x.data.state.contentDate='2026-10-26';});
rejected('状态checkDate不能混用另一日',x=>{x.data.state.checkDate='2026-10-25';});
rejected('证据文件名不可错期或路径穿越',x=>{x.data.state.evidence='../_content_review_2026-10-26.json';});
rejected('删通知即使保留总数声明也失败',x=>{x.data.notices.pop();});
rejected('修改摘要而保留URL也不是原内容',x=>{x.data.notices[0].sum='悄悄改过的内容';});
rejected('当前数据与报告一起改不能自证',x=>{x.data.notices[0].sum='伪造内容';x.report.cqutSnapshotsBefore=structuredClone(x.data.notices);});
rejected('内容新日期与报告一起滚不能自证',x=>{x.data.updated='2026-10-26';x.data.state.contentDate='2026-10-26';x.report.cqutContentUpdatedBefore='2026-10-26';});
rejected('缺少独立提交基线不能自证',x=>{delete x.baseline;});
rejected('核查当日新提交不当作核查前基线',x=>{x.baseline.committedAt='2026-10-26T08:30:00+08:00';});
rejected('改变配置入口不能缩减核查范围',x=>{x.data.sources.college=[];});
rejected('只核查配置站点而没核查全部通知拒绝',x=>{x.report.sources.shift();});
rejected('缺一个配置入口的请求记录拒绝',x=>{x.report.sources.pop();});
rejected('不可用成功响应替代失败保护证据',x=>{x.report.sources[0].usableContent=true;});
rejected('不能挑失败重试而隐藏成功响应',x=>{x.report.sources.push({...x.report.sources[0],usableContent:true});});
rejected('缺失失败诊断拒绝',x=>{delete x.report.sources[0].error;delete x.report.sources[0].limitation;});
rejected('没有变化不是访问失败理由',x=>{x.report.sources[0].error='';x.report.sources[0].limitation='No new notices';});
rejected('请求记录日期不能借用旧日',x=>{x.report.sources[0].checkedAt='2026-10-25';});
rejected('缺失实际请求时刻不能借用当前时钟',x=>{delete x.report.sources[0].checkedAtTime;});
rejected('请求时刻不能落在报告完成之后',x=>{x.report.sources[0].checkedAtTime='2026-10-26T10:00:00+08:00';});
rejected('报告不能引用未来完成时刻',x=>{x.report.completedAt='2026-10-26T23:00:00+08:00';});
rejected('报告缺少起止时刻拒绝',x=>{delete x.report.attemptedAt;delete x.report.completedAt;});
rejected('页面隐藏状态提示不能过关',x=>{x.disclosure.visible=false;});
rejected('页面漏掉受阻字样拒绝',x=>{x.disclosure.text='保留旧内容：2026-10-23，核查2026-10-26';});
rejected('页面漏掉保留旧内容字样拒绝',x=>{x.disclosure.text='官网受阻，内容2026-10-23，核查2026-10-26';});
rejected('页面不显示两个完整真实日期拒绝',x=>{x.disclosure.text='官网受阻，保留旧内容，最近已核查';});
rejected('空通知列表不能靠保留空快照通过',x=>{x.data.notices=[];x.report.cqutSnapshotsBefore=[];x.baseline.notices=[];});
rejected('不存在的日历日期拒绝',x=>{x.data.updated='2026-02-30';});
rejected('未来内容日期拒绝',x=>{x.data.updated='2026-10-27';});
test('北京时间跨UTC日正确，缺失时刻不默认当前时间',()=>{assert.equal(beijingDay('2026-10-25T16:30:00Z'),'2026-10-26');assert.equal(beijingDay(undefined),'');assert.ok(Number.isNaN(dayNumber('2026-02-30')));});
