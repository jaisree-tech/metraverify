import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="navbar">
      <Link to="/" className="brand">MetraVerify</Link>
      <div>
        <Link to="/verify">Verify Certificate</Link>
        {user && (
          <>
            <Link to="/dashboard">Dashboard</Link>
            {user.role === "USER" && <Link to="/instruments">Instruments</Link>}
            <Link to="/applications">Applications</Link>
            <Link to="/certificates">Certificates</Link>
            {user.role === "ADMIN" && <Link to="/admin">Admin</Link>}
            <a href="#" onClick={handleLogout}>Logout ({user.name})</a>
          </>
        )}
        {!user && (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </div>
  );
}
