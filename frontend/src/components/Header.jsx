import { LogOut, ScanLine } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import Logo from "./Logo";
import { getCurrentUser, hasRole, initials, logout } from "../utils/storage";

export default function Header() {
  const user = getCurrentUser();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="topbar">
      <Logo />

      <nav className="topnav">
        <NavLink to="/afisha" className="nav-pill">
          Афиша
        </NavLink>

        {hasRole(user, ["admin"]) && (
          <NavLink to="/scanner" className="nav-pill">
            <ScanLine size={15} /> Сканер
          </NavLink>
        )}

        {hasRole(user, ["admin"]) && (
          <NavLink to="/admin" className="nav-pill">
            Админ
          </NavLink>
        )}

        <NavLink to="/profile" className="user-link">
          <span className="avatar-mini">{initials(user?.name)}</span>
          <span>{user?.name}</span>
        </NavLink>

        <button className="icon-btn" onClick={handleLogout} title="Выйти">
          <LogOut size={20} />
        </button>
      </nav>
    </header>
  );
}
