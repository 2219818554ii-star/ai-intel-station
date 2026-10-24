// Retire date-only events after the Beijing end of day. An earlier clock time
// requires the same explicit time in both the preserved identity and evidence.
module.exports = function evidenceDeadline(item, review) {
  const day = item.deadline;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day || '')) return NaN;
  const midnight = Date.parse(day + 'T00:00:00+08:00');
  if (!Number.isFinite(midnight) || new Date(midnight + 8*3600000).toISOString().slice(0,10) !== day) return NaN;
  if (item.deadlineTime == null) return midnight + 24*3600000 - 1000;
  const time = item.deadlineTime;
  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(time)) return NaN;
  if (!review || review.deadline !== day || review.deadlineTime !== time || review.snapshot?.deadlineTime !== time) return NaN;
  const excerpt = String(review.evidenceExcerpt || '').replace(/：/g, ':').replace(/\s+/g, ' ');
  const clock = new RegExp('(?:^|[^0-9:])' + time + '(?![0-9:])');
  if (!clock.test(excerpt)) return NaN;
  return Date.parse(day + 'T' + time + ':00+08:00');
};
