import ConfirmationNumberIcon from "@mui/icons-material/ConfirmationNumber";
import EventIcon from "@mui/icons-material/Event";
import MeetingRoomIcon from "@mui/icons-material/MeetingRoom";
import MovieIcon from "@mui/icons-material/Movie";
import PeopleIcon from "@mui/icons-material/People";
import PersonIcon from "@mui/icons-material/Person";
import { Admin, Resource } from "react-admin";
import authProvider from "./authProvider";
import dataProvider from "./dataProvider";
import { ActorCreate, ActorEdit, ActorList } from "./resources/actors";
import { BookingList } from "./resources/bookings";
import { HallCreate, HallList, HallShow } from "./resources/halls";
import { MovieCreate, MovieEdit, MovieList } from "./resources/movies";
import { SessionCreate, SessionEdit, SessionList } from "./resources/sessions";
import { UserCreate, UserEdit, UserList } from "./resources/users";

export default function AdminApp() {
  return (
    <Admin
      basename="/admin"
      dataProvider={dataProvider}
      authProvider={authProvider}
      title="НеКино — Панель управления"
    >
      <Resource
        name="movies"
        list={MovieList}
        create={MovieCreate}
        edit={MovieEdit}
        icon={MovieIcon}
        options={{ label: "Фильмы" }}
      />
      <Resource
        name="sessions"
        list={SessionList}
        create={SessionCreate}
        edit={SessionEdit}
        icon={EventIcon}
        options={{ label: "Сеансы" }}
      />
      <Resource
        name="halls"
        list={HallList}
        create={HallCreate}
        show={HallShow}
        icon={MeetingRoomIcon}
        options={{ label: "Залы" }}
      />
      <Resource
        name="bookings"
        list={BookingList}
        icon={ConfirmationNumberIcon}
        options={{ label: "Брони" }}
      />
      <Resource
        name="users"
        list={UserList}
        edit={UserEdit}
        create={UserCreate}
        icon={PeopleIcon}
        options={{ label: "Пользователи" }}
      />
      <Resource
        name="actors"
        list={ActorList}
        create={ActorCreate}
        edit={ActorEdit}
        icon={PersonIcon}
        options={{ label: "Актёры" }}
      />
    </Admin>
  );
}
