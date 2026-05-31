const WEEK_DAYS = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];

export function formatSessionDate(isoDate) {
  if (!isoDate) return "";
  const [year, month, day] = isoDate.split("-").map(Number);
  if (!year || !month || !day) return "";
  const value = new Date(year, month - 1, day);
  const dayName = WEEK_DAYS[value.getDay()];
  return `${dayName} ${String(day).padStart(2, "0")}.${String(month).padStart(2, "0")}`;
}

export function formatSessionTime(time, isoDate) {
  if (!time || !isoDate) return "";
  return `${time} · ${formatSessionDate(isoDate)}`;
}
