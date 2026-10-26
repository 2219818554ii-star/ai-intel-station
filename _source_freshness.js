'use strict';

// User authorization on 2026-10-26, choice 1: CQUT may retain verified content
// when its official sources are blocked. The original two-day content rule is
// still the default; this evidence-bound exception applies to CQUT only.
const DAY=86400000;
function dayNumber(value){
  if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(value))return NaN;
  const time=Date.parse(value+'T00:00:00Z');
  return Number.isFinite(time)&&new Date(time).toISOString().slice(0,10)===value?time/DAY:NaN;
}
function beijingDay(value){
  const time=value instanceof Date?value.getTime():typeof value==='string'?Date.parse(value):NaN;
  return Number.isFinite(time)?new Date(time+8*3600000).toISOString().slice(0,10):'';
}
function timestamp(value){return typeof value==='string'&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value)?Date.parse(value):NaN;}
function canonical(value){
  if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
  if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
  return JSON.stringify(value);
}
function same(a,b){return canonical(a)===canonical(b);}
function sourceURLs(groups){
  if(!groups||typeof groups!=='object'||Array.isArray(groups))return null;
  const urls=[];
  for(const group of Object.values(groups)){
    if(!Array.isArray(group))return null;
    for(const item of group){if(!item||typeof item.u!=='string'||!/^https?:\/\//.test(item.u))return null;urls.push(item.u);}
  }
  return urls;
}
function blockedAttempt(row,checked,start,end,now){
  const diagnostic=[row.error,row.limitation].filter(s=>typeof s==='string').join(' ');
  const failure=/error|fail|timeout|timed out|denied|block|protect|challenge|empty|short|javascript|connection|remote|ssl|tls|refused|reset|unavailable|超时|受阻|保护|验证|失败|不可用|拒绝|空响应/i.test(diagnostic);
  const time=timestamp(row.checkedAtTime);
  return row.checkedAt===checked&&Number.isFinite(time)&&time>=start&&time<=end&&time<=now&&beijingDay(row.checkedAtTime)===checked&&row.usableContent===false&&failure;
}
function validateCQUTFreshness(input){
  const no=reason=>({ok:false,mode:'rejected',reason});
  if(!input||input.key!=='CQUT_UPDATED')return no('受阻保留例外仅适用于CQUT_UPDATED');
  const {today,data,report,baseline,disclosure}=input;
  if(!data)return no('学校数据缺失');
  const now=input.now instanceof Date?input.now.getTime():timestamp(input.now);
  if(!Number.isFinite(now)||beijingDay(new Date(now))!==today)return no('当前北京时间与日期不一致');
  const todayN=dayNumber(today),contentN=dayNumber(data.updated);
  if(!Number.isFinite(todayN)||!Number.isFinite(contentN)||contentN>todayN)return no('学校内容日期无效或在未来');
  const contentAge=todayN-contentN;
  const retentionMetadata=data.status==='blocked'||data.state!=null;
  if(contentAge<=2&&!retentionMetadata)return {ok:true,mode:'fresh-content',contentAge,reason:'原内容新鲜度不超过2天'};
  if(data.status!=='blocked')return no('旧学校内容没有明确受阻状态');
  const checkN=dayNumber(data.checked);
  if(!Number.isFinite(checkN)||checkN>todayN||todayN-checkN>2)return no('学校核查日期无效、在未来或超过2天');
  const state=data.state;
  if(!state||typeof state!=='object'||state.contentDate!==data.updated||state.checkDate!==data.checked||state.evidence!=='_content_review_'+data.checked+'.json')return no('保留状态的内容日、核查日或证据文件不一致');
  if(!report||report.reviewedAt!==data.checked||report.cqutContentUpdatedBefore!==data.updated)return no('独立核查报告缺失、错日或改变了原内容日期');
  if(!Number.isFinite(timestamp(report.attemptedAt))||!Number.isFinite(timestamp(report.completedAt))||beijingDay(report.attemptedAt)!==data.checked||beijingDay(report.completedAt)!==data.checked||timestamp(report.completedAt)<timestamp(report.attemptedAt)||timestamp(report.completedAt)>now)return no('独立报告的真实请求时刻与核查日不一致或在未来');
  if(!baseline||!/^[a-f0-9]{40}$/.test(baseline.commit||'')||!Number.isFinite(timestamp(baseline.committedAt))||timestamp(baseline.committedAt)>=Date.parse(data.checked+'T00:00:00+08:00'))return no('缺少核查日前独立已提交的学校内容基线');
  if(baseline.updated!==data.updated||!same(data.notices,baseline.notices)||!same(data.sources,baseline.sources))return no('当前通知、配置入口或原内容日期偏离独立已提交基线');
  if(!Array.isArray(data.notices)||!data.notices.length||!same(data.notices,report.cqutSnapshotsBefore))return no('当前通知与当次抓取前完整快照不一致');
  if(data.notices.some(n=>!n||typeof n.url!=='string'||!/^https?:\/\//.test(n.url)))return no('通知原文入口无效');
  const portals=sourceURLs(data.sources);
  if(!portals||!portals.length)return no('学校配置入口缺失或无效');
  if(!Array.isArray(report.sources))return no('独立请求记录缺失');
  const required=new Set(data.notices.map(n=>n.url).concat(portals));
  for(const url of required){
    const attempts=report.sources.filter(row=>row&&row.url===url);
    if(!attempts.length)return no('独立记录未覆盖全部通知及配置入口：'+url);
    // Do not cherry-pick a failed retry while hiding a readable response. A
    // usable response requires a normal content review rather than this exception.
    if(!attempts.every(row=>blockedAttempt(row,data.checked,timestamp(report.attemptedAt),timestamp(report.completedAt),now)))return no('所需入口没有明确、同日的失败/保护证据：'+url);
  }
  const text=disclosure&&disclosure.text;
  if(!disclosure||disclosure.visible!==true||typeof text!=='string'||!text.includes('受阻')||!text.includes('保留旧内容')||!text.includes(data.updated)||!text.includes(data.checked))return no('页面未显式披露受阻、保留旧内容及两个真实日期');
  return {ok:true,mode:'blocked-retained',contentAge,checkAge:todayN-checkN,requiredURLs:required.size,
    reason:'官网受阻，全部来源有同日失败记录；原内容和独立基线一致，页面明确保留旧内容'};
}
module.exports={dayNumber,beijingDay,validateCQUTFreshness};
