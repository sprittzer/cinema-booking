import {
  BooleanField,
  BooleanInput,
  Create,
  Datagrid,
  Edit,
  List,
  NumberField,
  SelectField,
  SelectInput,
  SimpleForm,
  TextField,
  TextInput,
} from "react-admin";

const ROLE_CHOICES = [
  { id: "user", name: "Пользователь" },
  { id: "admin", name: "Администратор" },
];

export const UserList = () => (
  <List>
    <Datagrid rowClick="edit">
      <NumberField source="id" label="ID" />
      <TextField source="name" label="Имя" />
      <TextField source="email" label="Email" />
      <SelectField source="role" label="Роль" choices={ROLE_CHOICES} />
      <BooleanField source="is_active" label="Активен" />
    </Datagrid>
  </List>
);

export const UserEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" label="Имя" disabled fullWidth />
      <TextInput source="email" label="Email" disabled fullWidth />
      <SelectInput source="role" label="Роль" choices={ROLE_CHOICES} />
      <BooleanInput source="is_active" label="Активен" />
    </SimpleForm>
  </Edit>
);

export const UserCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="name" label="Имя" required fullWidth />
      <TextInput source="email" label="Email" required fullWidth />
      <TextInput source="password" label="Пароль" required type="password" fullWidth />
      <SelectInput source="role" label="Роль" choices={ROLE_CHOICES} defaultValue="user" />
    </SimpleForm>
  </Create>
);
