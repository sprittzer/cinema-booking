import { Navigate } from "react-router-dom";
import { getCurrentUser, hasRole } from "../utils/storage";

export default function ProtectedRoute({ children, roles }) {
  const user = getCurrentUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !hasRole(user, roles)) {
    return <Navigate to="/afisha" replace />;
  }

  return children;
}
