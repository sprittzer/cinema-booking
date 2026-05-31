import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import AfishaPage from "./pages/AfishaPage";
import ProfilePage from "./pages/ProfilePage";
import MoviePage from "./pages/MoviePage";
import MovieBookingPage from "./pages/MovieBookingPage";
import ModeratorPage from "./pages/ModeratorPage";
import ScannerPage from "./pages/ScannerPage";
import AdminApp from "./admin/AdminApp";
import ThemeToggle from "./components/ThemeToggle";

function CursorTrail() {
  useEffect(() => {
    let lastX = 0, lastY = 0;

    function onMove(e) {
      if (Math.hypot(e.clientX - lastX, e.clientY - lastY) < 14) return;
      lastX = e.clientX;
      lastY = e.clientY;

      const el = document.createElement("span");
      el.className = "cursor-plus";
      el.textContent = "+";
      el.style.left = e.clientX + "px";
      el.style.top = e.clientY + "px";
      document.body.appendChild(el);
      setTimeout(() => el.remove(), 1400);
    }

    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  return null;
}

export default function App() {
  const location = useLocation();
  const isAdmin = location.pathname.startsWith("/admin");

  return (
    <>
      <div className="center-panel" aria-hidden="true" />
      <div className="side-glow" aria-hidden="true" />
      <CursorTrail />
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route path="/afisha" element={<ProtectedRoute><AfishaPage /></ProtectedRoute>} />
        <Route path="/movies/:movieId" element={<ProtectedRoute><MoviePage /></ProtectedRoute>} />
        <Route path="/movies/:movieId/booking" element={<ProtectedRoute><MovieBookingPage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />

        <Route path="/moderator" element={<ProtectedRoute roles={["admin"]}><ModeratorPage /></ProtectedRoute>} />
        <Route path="/scanner" element={<ProtectedRoute roles={["admin"]}><ScannerPage /></ProtectedRoute>} />
        <Route path="/admin/*" element={<AdminApp />} />

        <Route path="/" element={<Navigate to="/afisha" replace />} />
        <Route path="*" element={<Navigate to="/afisha" replace />} />
      </Routes>
      {!isAdmin && <ThemeToggle />}
    </>
  );
}
