import React, { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.get("/analytics/dashboard").then((res) => setStats(res.data));
  }, []);

  return (
    <div className="container">
      <h2>Welcome, {user?.name} <span className="muted">({user?.role})</span></h2>
      {stats && (
        <div className="grid">
          {Object.entries(stats).map(([key, value]) => (
            <div className="stat-box" key={key}>
              <div className="value">{value}</div>
              <div className="label">{key.replace(/_/g, " ")}</div>
            </div>
          ))}
        </div>
      )}
      <div className="card" style={{ marginTop: 20 }}>
        <h3>Quick links</h3>
        <ul>
          {user?.role === "USER" && (
            <>
              <li><a href="/instruments">My Instruments</a> — register a new weighing/measuring instrument</li>
              <li><a href="/applications">My Applications</a> — apply for verification &amp; track status</li>
            </>
          )}
          {user?.role === "LMO" && (
            <li><a href="/applications">Assigned Applications</a> — enter inspection observations</li>
          )}
          {user?.role === "ADMIN" && (
            <>
              <li><a href="/applications">All Applications</a> — assign officers</li>
              <li><a href="/admin">Admin Panel</a> — manage users &amp; officers</li>
            </>
          )}
          <li><a href="/verify">Public Certificate Verification</a></li>
        </ul>
      </div>
    </div>
  );
}
