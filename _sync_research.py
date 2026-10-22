"""把指定Google展示表连接器读回的数据，校验后发布为六字段摘要。不可输入完整总表。"""
import argparse, datetime, hashlib, json, math, os, pathlib, re

SOURCE_ID = "1sHUITtFaKh5NV64wvlErZRuR3B3DZq-V9NCQuGb-FMc"
HEADERS = ["任务编号", "建议日期", "展示任务", "公开状态", "预计主动小时", "分类"]
TITLES = {'电池装配记录', '极片工艺小试与质量排查', '科研阅读与论文撰写', '实验样品制备', '合格样品测量验证', '历史测量数据溯源', '电池装配规范复核', '科研记录与数据检查', '电池装配与测试核验', '实验资源协调', '样品编号与质量台账', '计划复盘与科研协调', '设备连接与模式核验', '实验材料盘点', '实验表征与记录', '电化学测试与数据整理', '科研资料整理提交', '安全与接收审批', '极片质量核验', '样品编号与异常记录', '电极质量检查'}
CATEGORIES = {"实验资源", "安全与测试", "科研整理", "样品质量", "项目管理", "写作", "电化学", "实验制备", "实验表征"}
STATUSES = {"计划中", "进行中", "待条件", "待确认", "已完成", "已取消"}
TASK_KEYS = {"id", "date", "title", "status", "hours", "category"}
ROOT_KEYS = {"schemaVersion", "sourceLabel", "sourceUpdatedAt", "syncedAt", "revision", "tasks"}

def iso(value):
    if not isinstance(value, str):
        raise ValueError("日期类型错误")
    return datetime.date.fromisoformat(value).isoformat()

def timestamp(value):
    parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("时间须带时区")
    return parsed.astimezone(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def digest(tasks):
    return hashlib.sha256(json.dumps(tasks, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()[:16]

def validate(data):
    if set(data) != ROOT_KEYS or data["schemaVersion"] != 1 or data["sourceLabel"] != "Google 科研展示表":
        raise ValueError("仅允许展示摘要结构")
    timestamp(data["sourceUpdatedAt"]); timestamp(data["syncedAt"])
    if not isinstance(data["tasks"], list) or len(data["tasks"]) > 999:
        raise ValueError("任务行数异常")
    seen = set()
    for task in data["tasks"]:
        if set(task) != TASK_KEYS or not re.fullmatch(r"T\d{3,5}", task["id"]):
            raise ValueError("任务字段或编号异常")
        if task["id"] in seen:
            raise ValueError("重复任务编号")
        seen.add(task["id"])
        if task["date"] is not None and iso(task["date"]) != task["date"]:
            raise ValueError("日期格式异常")
        if task["title"] not in TITLES or task["category"] not in CATEGORIES or task["status"] not in STATUSES:
            raise ValueError("出现未审核的展示内容，请先核对公开白名单")
        hours = task["hours"]
        if hours is not None and (isinstance(hours, bool) or not isinstance(hours, (int, float)) or not math.isfinite(hours) or not 0 <= hours <= 240):
            raise ValueError("预计工时异常")
    if data["revision"] != digest(data["tasks"]):
        raise ValueError("摘要版本与任务不一致")
    return data

def from_connector(source):
    if source.get("spreadsheetId") != SOURCE_ID or source.get("sheetName") != "网站数据":
        raise ValueError("禁止从完整总表或其他文件导出")
    values = source["values"]
    if not values or values[0] != HEADERS:
        raise ValueError("展示表必须严格只有六列表头")
    tasks = []
    for row in values[1:]:
        if not any(v not in ("", None) for v in row):
            continue
        if len(row) > 6:
            raise ValueError("禁止导出额外字段")
        row = row + [None] * (6-len(row))
        if isinstance(row[4], bool):
            raise ValueError("布尔值不能作为预计工时")
        hours = None if row[4] in ("", None) else float(row[4])
        if hours is not None and hours.is_integer():
            hours = int(hours)
        tasks.append(dict(id=row[0], date=None if row[1] in ("", None) else iso(row[1]), title=row[2], status=row[3] or "待确认", hours=hours, category=row[5]))
    return validate(dict(schemaVersion=1, sourceLabel="Google 科研展示表", sourceUpdatedAt=timestamp(source["sourceUpdatedAt"]), syncedAt=timestamp(source["syncedAt"]), revision=digest(tasks), tasks=tasks))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="连接器指定展示表的六列读回JSON，存放于网站仓库以外")
    args = parser.parse_args()
    data = from_connector(json.loads(pathlib.Path(args.input).read_text(encoding="utf-8-sig")))
    out = pathlib.Path(__file__).with_name("research-data.json")
    temporary = out.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    os.replace(temporary, out)
    print(json.dumps({"tasks":len(data["tasks"]), "revision":data["revision"], "fieldsPerTask":6}))
