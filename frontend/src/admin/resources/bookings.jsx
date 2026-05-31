import { Datagrid, List, NumberField, SelectField, TextField } from "react-admin";

const STATUS_CHOICES = [
  { id: "pending", name: "Ожидает оплаты" },
  { id: "confirmed", name: "Подтверждён" },
  { id: "used", name: "Использован" },
  { id: "cancelled", name: "Отменён" },
];

export const BookingList = () => (
  <List>
    <Datagrid>
      <NumberField source="id" label="ID" />
      <NumberField source="user_id" label="Пользователь" />
      <NumberField source="session_id" label="Сеанс" />
      <SelectField source="status" label="Статус" choices={STATUS_CHOICES} />
      <NumberField source="total_price" label="Сумма" />
      <TextField source="ticket_code" label="Код билета" />
    </Datagrid>
  </List>
);
