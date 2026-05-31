import {
  Create,
  Datagrid,
  DateInput,
  Edit,
  List,
  NumberField,
  NumberInput,
  ReferenceField,
  ReferenceInput,
  SelectField,
  SelectInput,
  SimpleForm,
  TextField,
  TextInput,
} from "react-admin";

const FORMAT_CHOICES = [
  { id: "2d", name: "2D" },
  { id: "3d", name: "3D" },
  { id: "imax", name: "IMAX" },
];

const LANGUAGE_CHOICES = [
  { id: "ru", name: "Русский" },
  { id: "en", name: "English" },
  { id: "en_sub", name: "English + субтитры" },
];

const STATUS_CHOICES = [
  { id: "scheduled", name: "Запланирован" },
  { id: "ongoing", name: "Идёт" },
  { id: "completed", name: "Завершён" },
  { id: "cancelled", name: "Отменён" },
];

export const SessionList = () => (
  <List>
    <Datagrid rowClick="edit">
      <NumberField source="id" label="ID" />
      <ReferenceField source="movie_id" reference="movies" label="Фильм">
        <TextField source="title" />
      </ReferenceField>
      <ReferenceField source="hall_id" reference="halls" label="Зал">
        <TextField source="name" />
      </ReferenceField>
      <TextField source="date" label="Дата" />
      <TextField source="time" label="Время" />
      <SelectField source="format" label="Формат" choices={FORMAT_CHOICES} />
      <SelectField source="language" label="Язык" choices={LANGUAGE_CHOICES} />
      <NumberField source="base_price" label="Цена" />
      <SelectField source="status" label="Статус" choices={STATUS_CHOICES} />
    </Datagrid>
  </List>
);

const SessionForm = () => (
  <>
    <ReferenceInput source="movie_id" reference="movies">
      <SelectInput optionText="title" label="Фильм" required />
    </ReferenceInput>
    <ReferenceInput source="hall_id" reference="halls">
      <SelectInput optionText="name" label="Зал" required />
    </ReferenceInput>
    <DateInput source="date" label="Дата" required />
    <TextInput source="time" label="Время (ЧЧ:ММ)" placeholder="19:30" required />
    <SelectInput source="format" label="Формат" choices={FORMAT_CHOICES} defaultValue="2d" />
    <SelectInput source="language" label="Язык" choices={LANGUAGE_CHOICES} defaultValue="ru" />
    <NumberInput source="base_price" label="Базовая цена" defaultValue={500} />
  </>
);

export const SessionCreate = () => (
  <Create>
    <SimpleForm>
      <SessionForm />
    </SimpleForm>
  </Create>
);

export const SessionEdit = () => (
  <Edit>
    <SimpleForm>
      <SessionForm />
    </SimpleForm>
  </Edit>
);
