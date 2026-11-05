'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');

// Exercise the actual hollow-update guard with controlled Git/filesystem
// responses. No dates, school data or real Git history are changed by fixtures.
module.exports=function({ok}){
  const source=fs.readFileSync(path.join(__dirname,'_selfcheck.js'),'utf8');
  const marker=source.indexOf('/* 反空洞更新：');
  const start=source.indexOf('(function(){',marker);
  const end=source.indexOf('\n})();',start);
  if(marker<0||start<0||end<0)throw Error('CQUT hollow-update guard not found');
  const guard=source.slice(start,end+'\n})();'.length);
  const original=[{date:'2026-10-30',url:'https://official.example/original'}];
  const backfill={date:'2026-10-28',url:'https://official.example/backfill'};
  const file=(day,notices)=>'window.CQUT_UPDATED = "'+day+'";\nwindow.CQUT_NOTICES = '+JSON.stringify(notices,null,2)+';\n';
  const windows=text=>text.replace(/\n/g,'\r\n');
  function check(label,{before,current,noGit=false,retention={ok:false,mode:'rejected'}},expected,reason){
    const data={window:{}};vm.runInNewContext(current,data);
    const results=[];
    vm.runInNewContext(guard,{
      sandbox:data,cqNotices:data.window.CQUT_NOTICES,cqSourceFreshness:retention,__dirname,
      process:{env:{}},ok:(pass,text)=>results.push({pass,text}),
      require(name){
        if(name==='child_process')return {execFileSync(){if(noGit)throw Error('Git unavailable');return before;}};
        if(name==='fs')return {readFileSync(){return current;}};
        if(name==='path')return path;
        throw Error('Unexpected guard dependency: '+name);
      }
    });
    const result=results[0];
    ok(results.length===1&&result.pass===expected&&reason.test(result.text),label+(result?'：'+result.text:''));
  }
  const same=file('2026-11-03',original);
  check('Git LF与工作区CRLF内容相同不误判为本轮刷新',{before:same,current:windows(same)},true,/本轮未改动/);
  check('反向换行表示差异也不改变内容作用域',{before:windows(same),current:same},true,/本轮未改动/);
  check('CRLF归一化不能掩盖真实日期空滚',{before:file('2026-11-02',original),current:windows(same)},false,/新增 0 条/);
  check('原文日期不变的真实补收仍通过增量校验',{before:file('2026-10-30',original),current:windows(file('2026-11-03',original.concat(backfill)))},true,/新增 1 条.*补漏抓/);
  check('缺少Git基线不能推定未改动并绕过严格日期门',{before:same,current:same,noGit:true},false,/新增 -1 条/);
  check('缺少Git时仍允许满足严格日期条件的正常内容',{before:'',current:file('2026-11-03',[{date:'2026-11-02',url:'https://official.example/recent'}]),noGit:true},true,/<= 3 天/);
  const disclosed=same+'window.CQUT_CHECK_NOTE="Official sources blocked; original content retained";\n';
  check('完整证据验证通过后只增受阻说明不冒称内容更新',{before:same,current:disclosed,retention:{ok:true,mode:'blocked-retained'}},true,/受阻保留已独立完整核验.*不声称新增/);
  check('受阻验证失败仍必须通过原日期与增量判据',{before:same,current:disclosed,retention:{ok:false,mode:'blocked-retained'}},false,/新增 0 条/);
  check('普通新鲜内容结论不能借受阻路径跳过空滚检查',{before:file('2026-11-02',original),current:same,retention:{ok:true,mode:'fresh-content'}},false,/新增 0 条/);
};

if(require.main===module){
  let pass=0,fail=0;
  module.exports({ok(value,message){value?pass++:fail++;console.log((value?'[PASS] ':'[FAIL] ')+message);}});
  console.log('CQUT scope: '+pass+' passed / '+fail+' failed');
  process.exitCode=fail?1:0;
}
