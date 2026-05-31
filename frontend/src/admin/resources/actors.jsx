import {
  Create,
  Datagrid,
  Edit,
  List,
  NumberField,
  NumberInput,
  SimpleForm,
  TextField,
  TextInput,
} from "react-admin";

const ActorFormFields = () => (
  <>
    <TextInput source="name" label="Имя" required fullWidth />
    <TextInput source="photo_url" label="URL фото" fullWidth />
    <NumberInput source="birth_year" label="Год рождения" />
    <TextInput source="bio" label="Биография" multiline rows={3} fullWidth />
  </>
);

export const ActorList = () => (
  <List>
    <Datagrid rowClick="edit">
      <NumberField source="id" label="ID" />
      <TextField source="name" label="Имя" />
      <NumberField source="birth_year" label="Год рождения" />
    </Datagrid>
  </List>
);

export const ActorCreate = () => (
  <Create>
    <SimpleForm>
      <ActorFormFields />
    </SimpleForm>
  </Create>
);

export const ActorEdit = () => (
  <Edit>
    <SimpleForm>
      <ActorFormFields />
    </SimpleForm>
  </Edit>
);
