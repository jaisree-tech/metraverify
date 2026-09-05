import React, { useEffect, useState } from "react";
import api, { API_BASE_URL } from "../api";

export default function Certificates() {
  const [certs, setCerts] = useState([]);

  useEffect(() => {
    api.get("/certificates/").then((res) => setCerts(res.data));
  }, []);

  return (
    <div className="container">
      <h2>Certificates</h2>
      <div className="grid">
        {certs.map((c) => (
          <div className="card" key={c.id}>
            <strong>{c.certificate_number}</strong>
            <p className={`badge ${c.status}`}>{c.status}</p>
            <img
              src={`${API_BASE_URL}/static/qr/${c.qr_token}.png`}
              alt="QR code"
              width={140}
            />
            <p className="muted">
              Issued: {new Date(c.issue_date).toLocaleDateString()}<br />
              Valid until: {new Date(c.expiry_date).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
      {certs.length === 0 && <p className="muted">No certificates issued yet.</p>}
    </div>
  );
}
