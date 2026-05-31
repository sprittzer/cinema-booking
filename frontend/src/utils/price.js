export function getTicketPrice(time) {
  if (!time) {
    return 0;
  }

  const hour = Number(time.split(":")[0]);

  if (hour < 12) {
    return 350;
  }

  if (hour < 18) {
    return 500;
  }

  return 700;
}

export function getPriceLabel(time) {
  if (!time) {
    return "";
  }

  const hour = Number(time.split(":")[0]);

  if (hour < 12) {
    return "Утренний тариф";
  }

  if (hour < 18) {
    return "Дневной тариф";
  }

  return "Вечерний тариф";
}