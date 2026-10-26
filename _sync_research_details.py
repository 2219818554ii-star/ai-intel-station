"""Export explicitly reviewed native task text and read-only journal fields.

No source spreadsheet IDs, evidence paths, locations, credentials or raw OCV
datasets are exported. A changed private release or text digest needs review;
the six-field summary and private source are never edited by this command.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path
import re
from _sync_research import validate as validate_summary

ROOT=Path(__file__).resolve().parent
APPROVED_RELEASE_DIGESTS={'86380836c1f21d31b4d1':'30ccba2cb25b7d2c7d7dcc56e97f0f1ebf2ff5dcb37ea495dbfc65e8cde28391'}
TASK_KEYS=('id','title','steps','acceptance','progress','prerequisite','gate')
RECORD_KEYS=('id','date','taskIds','work','issues','conditions','observations','next','replan','status','updatedAt','start','end','activeHours','waitingHours','travelHours','breakMinutes')
ROOT_KEYS=('schemaVersion','summaryRevision','sourceReleaseId','sourceSyncedAt','contentDigest','tasks','records')
STATES={'待核对','已核对','需补充','已更正'}
UNSAFE=re.compile(r'[A-Za-z]:[\\/]|file:|https?://|(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|client[_ -]?secret|password|passwd|private[_ -]?key|authorization|bearer\s)|密码|验证码|(?<!\d)1[3-9]\d{9}(?!\d)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',re.I)

def exact(value,keys):
    return isinstance(value,dict) and set(value)==set(keys)

def day(value):
    try:return isinstance(value,str) and datetime.strptime(value,'%Y-%m-%d').strftime('%Y-%m-%d')==value
    except ValueError:return False

def text(value,limit=2400,required=False):
    if value is None:value=''
    if not isinstance(value,str) or len(value)>limit or (required and not value.strip()) or UNSAFE.search(value):
        raise ValueError('Unreviewed, unsafe or invalid text field')
    return value

def timestamp(value,optional=False):
    if optional and value in ('',None):return None
    if not isinstance(value,str):raise ValueError('Invalid timestamp')
    try:datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:raise ValueError('Invalid timestamp')
    return value

def actual(value,maximum=744):
    if value in ('',None):return None
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not 0<=value<=maximum:raise ValueError('Invalid actual duration')
    return int(value) if value==int(value) else value

def digest(tasks,records):
    ordered_tasks=[{k:t[k] for k in TASK_KEYS} for t in tasks]
    ordered_records=[{k:r[k] for k in RECORD_KEYS} for r in records]
    return hashlib.sha256(json.dumps([ordered_tasks,ordered_records],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def validate_bundle(bundle,summary):
    summary=validate_summary(summary)
    if not exact(bundle,ROOT_KEYS) or bundle['schemaVersion']!=1 or bundle['summaryRevision']!=summary['revision']:raise ValueError('Native text and summary versions do not match')
    release=bundle['sourceReleaseId']
    if release not in APPROVED_RELEASE_DIGESTS:raise ValueError('Private release has not been reviewed for publication')
    timestamp(bundle['sourceSyncedAt'])
    tasks=bundle['tasks'];records=bundle['records']
    if not isinstance(tasks,list) or not isinstance(records,list) or len(records)>2000:raise ValueError('Invalid native task/journal lists')
    ids=set();expected={t['id'] for t in summary['tasks']}
    for t in tasks:
        if not exact(t,TASK_KEYS) or not isinstance(t['id'],str) or t['id'] not in expected or t['id'] in ids:raise ValueError('Missing, duplicate or unknown detailed task')
        ids.add(t['id'])
        for k in TASK_KEYS[1:]:text(t[k],required=k in ('title','steps','acceptance'))
    if ids!=expected:raise ValueError('Detailed task IDs do not exactly cover the approved summary')
    record_ids=set()
    for r in records:
        if not exact(r,RECORD_KEYS) or not isinstance(r['id'],str) or not re.fullmatch(r'LOG-\d{8}-\d{3}',r['id']) or r['id'] in record_ids or not day(r['date']):raise ValueError('Invalid journal identity/date')
        record_ids.add(r['id'])
        if not isinstance(r['taskIds'],list) or len(set(r['taskIds']))!=len(r['taskIds']) or any(x not in ids for x in r['taskIds']) or r['status'] not in STATES:raise ValueError('Invalid journal association/status')
        for k in ('work','issues','conditions','observations','next','replan'):text(r[k],required=k=='work')
        for k in ('updatedAt','start','end'):timestamp(r[k],optional=True)
        if r['start'] and r['end'] and r['end']<r['start']:raise ValueError('Journal ends before it starts')
        for k,maximum in [('activeHours',24),('waitingHours',744),('travelHours',24),('breakMinutes',1440)]:
            if actual(r[k],maximum)!=r[k]:raise ValueError('Invalid journal duration')
    calculated=digest(tasks,records)
    if bundle['contentDigest']!=calculated or calculated!=APPROVED_RELEASE_DIGESTS[release]:raise ValueError('Text/record content differs from the reviewed export')
    return bundle

def make_bundle(private,journal,summary):
    summary=validate_summary(summary)
    if private.get('schemaVersion')!=1 or journal.get('schemaVersion')!=1:raise ValueError('Invalid private export version')
    release=private.get('releaseId')
    if release not in APPROVED_RELEASE_DIGESTS or journal.get('releaseId')!=release:raise ValueError('Task and journal releases differ or are unreviewed')
    rows=private.get('tasks');entries=journal.get('entries')
    if not isinstance(rows,list) or not isinstance(entries,list) or any(not isinstance(r,list) or len(r)!=34 for r in rows):raise ValueError('Expected exactly34 reviewed task columns')
    original=hashlib.sha256(json.dumps([rows,entries],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:20]
    if original!=release:raise ValueError('Private release checksum mismatch')
    public={t['id']:t for t in summary['tasks']};tasks=[]
    for row in rows:
        if row[0] not in public:raise ValueError('Unknown source task')
        p=public[row[0]];status=row[15]
        if status=='未开始':status='待条件' if str(row[13] or '').startswith('HOLD') else '计划中'
        hours=float(row[22]) if row[22] not in ('',None) else None
        if (row[12] or None)!=p['date'] or status!=p['status'] or hours!=p['hours']:raise ValueError('Dates, statuses or estimated hours disagree with approved summary')
        tasks.append({'id':row[0],'title':text(row[6],required=True),'steps':text(row[7],required=True),'acceptance':text(row[8],required=True),'progress':text(row[16]),'prerequisite':text(row[9]),'gate':text(row[13])})
    records=[]
    for e in entries:
        r={k:e.get(k) for k in RECORD_KEYS}
        for k in ('work','issues','conditions','observations','next','replan'):r[k]=text(r[k],required=k=='work')
        for k in ('updatedAt','start','end'):r[k]=timestamp(r[k],optional=True)
        for k,maximum in [('activeHours',24),('waitingHours',744),('travelHours',24),('breakMinutes',1440)]:r[k]=actual(r[k],maximum)
        records.append(r)
    return {'schemaVersion':1,'summaryRevision':summary['revision'],'sourceReleaseId':release,'sourceSyncedAt':timestamp(private['syncedAt']),'contentDigest':digest(tasks,records),'tasks':tasks,'records':records}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tasks',type=Path,required=True);p.add_argument('--journal',type=Path,required=True);p.add_argument('--summary',type=Path,default=ROOT/'research-data.json');p.add_argument('--output',type=Path,default=ROOT/'research-details.json');p.add_argument('--dry-run',action='store_true');args=p.parse_args()
    read=lambda path:json.loads(path.read_text(encoding='utf-8-sig'))
    summary=read(args.summary);result=validate_bundle(make_bundle(read(args.tasks),read(args.journal),summary),summary)
    if not args.dry_run:args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'tasks':len(result['tasks']),'records':len(result['records']),'summaryRevision':result['summaryRevision'],'sourceReleaseId':result['sourceReleaseId'],'contentDigest':result['contentDigest'],'written':not args.dry_run},ensure_ascii=False))
