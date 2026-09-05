import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";

export default function VerifyCertificate() {
  const { token } = useParams();
  const [cert, setCert] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const [manualToken, setManualToken] = useState("");

  const lookup = (t) => {
    setNotFound(false);
    setCert(null);
    api
      .get(`/certificates/verify/${t}`)
      .then((res) => setCert(res.data))
      .catch(() => setNotFound(true));
  };

  useEffect(() => {
    if (token) lookup(token);
  }, [token]);

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: 460, margin: "40px auto", textAlign: "center" }}>
        <h2>Certificate Verification</h2>
        {!token && (
          <div style={{ display: "flex", gap: 8, justifyContent: "center", marginBottom: 16 }}>
            <input
              placeholder="Enter QR token / certificate code"
              value={manualToken}
              onChange={(e) => setManualToken(e.target.value)}
            />
            <button onClick={() => lookup(manualToken)}>Check</button>
          </div>
        )}

        {cert && (
          <div>
            <p style={{ fontSize: 20, color: "#155724" }}>✓ CERTIFICATE VERIFIED</p>
            <p><strong>Certificate ID:</strong> {cert.certificate_number}</p>
            <p><strong>Instrument:</strong> {cert.instrument_type}</p>
            <p><strong>Status:</strong> <span className={`badge ${cert.status}`}>{cert.status}</span></p>
            <p><strong>Verified On:</strong> {new Date(cert.issue_date).toLocaleDateString()}</p>
            <p><strong>Valid Until:</strong> {new Date(cert.expiry_date).toLocaleDateString()}</p>
          </div>
        )}

        {notFound && <p className="error-text">Certificate not found or invalid.</p>}
      </div>
    </div>
  );
}
