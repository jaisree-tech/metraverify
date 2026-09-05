import React, { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../AuthContext";

export default function Applications() {
  const { user } = useAuth();
  const [applications, setApplications] = useState([]);
  const [instruments, setInstruments] = useState([]);
  const [officers, setOfficers] = useState([]);

  const [newApp, setNewApp] = useState({ instrument_id: "", application_type: "New Verification", preferred_date: "" });
  const [assignMap, setAssignMap] = useState({});
  const [verifyForm, setVerifyForm] = useState({});
  const [error, setError] = useState("");
  const [showApplyForm, setShowApplyForm] = useState(false);

  const loadApplications = () => api.get("/applications/").then((res) => setApplications(res.data));

  useEffect(() => {
    loadApplications();
    if (user?.role === "USER") {
      api.get("/instruments/").then((res) => setInstruments(res.data));
    }
    if (user?.role === "ADMIN") {
      api.get("/admin/users").then((res) => setOfficers(res.data.filter((u) => u.role === "LMO")));
    }
  }, [user]);

  const applyForVerification = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/applications/", {
        instrument_id: Number(newApp.instrument_id),
        application_type: newApp.application_type,
        preferred_date: newApp.preferred_date || null,
      });
      setNewApp({ instrument_id: "", application_type: "New Verification", preferred_date: "" });
      setShowApplyForm(false);
      loadApplications();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit application");
    }
  };

  const assignOfficer = async (appId) => {
    const officerId = assignMap[appId];
    if (!officerId) return;
    await api.post(`/applications/${appId}/assign`, { officer_id: Number(officerId) });
    loadApplications();
  };

  const submitVerification = async (appId) => {
    const data = verifyForm[appId];
    if (!data?.expected_value || !data?.observed_value || !data?.tolerance) {
      setError("Fill expected, observed and tolerance values first.");
      return;
    }
    try {
      await api.post(`/verification/${appId}/submit`, {
        expected_value: Number(data.expected_value),
        observed_value: Number(data.observed_value),
        tolerance: Number(data.tolerance),
        remarks: data.remarks || "",
      });
      loadApplications();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit verification");
    }
  };

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>{user?.role === "USER" ? "My Applications" : user?.role === "LMO" ? "Assigned Applications" : "All Applications"}</h2>
        {user?.role === "USER" && (
          <button onClick={() => setShowApplyForm(!showApplyForm)}>
            {showApplyForm ? "Cancel" : "+ Apply for Verification"}
          </button>
        )}
      </div>

      {showApplyForm && (
        <div className="card">
          <form onSubmit={applyForVerification}>
            <select
              value={newApp.instrument_id}
              onChange={(e) => setNewApp({ ...newApp, instrument_id: e.target.value })}
              required
            >
              <option value="">Select Instrument</option>
              {instruments.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.registration_id} — {i.instrument_type}
                </option>
              ))}
            </select>
            <select
              value={newApp.application_type}
              onChange={(e) => setNewApp({ ...newApp, application_type: e.target.value })}
            >
              <option>New Verification</option>
              <option>Re-Verification</option>
              <option>Renewal</option>
              <option>Correction/Reinspection</option>
            </select>
            <input
              type="date"
              value={newApp.preferred_date}
              onChange={(e) => setNewApp({ ...newApp, preferred_date: e.target.value })}
            />
            {error && <div className="error-text">{error}</div>}
            <button type="submit">Submit Application</button>
          </form>
        </div>
      )}

      {applications.map((app) => (
        <div className="card" key={app.id}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <strong>{app.application_number}</strong>
            <span className={`badge ${app.status}`}>{app.status.replace(/_/g, " ")}</span>
          </div>
          <p className="muted">
            Instrument ID: {app.instrument_id} · Type: {app.application_type} · Submitted:{" "}
            {new Date(app.submitted_date).toLocaleDateString()}
          </p>

          {user?.role === "ADMIN" && !app.assigned_officer_id && (
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <select
                onChange={(e) => setAssignMap({ ...assignMap, [app.id]: e.target.value })}
                defaultValue=""
              >
                <option value="" disabled>Select LMO officer</option>
                {officers.map((o) => (
                  <option key={o.id} value={o.id}>{o.name}</option>
                ))}
              </select>
              <button onClick={() => assignOfficer(app.id)}>Assign Officer</button>
            </div>
          )}

          {user?.role === "LMO" &&
            app.assigned_officer_id === user.id &&
            !["APPROVED", "REJECTED", "CERTIFICATE_ISSUED"].includes(app.status) && (
              <div style={{ marginTop: 10 }}>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <input
                    style={{ width: 140 }}
                    type="number"
                    step="any"
                    placeholder="Expected value"
                    onChange={(e) =>
                      setVerifyForm({ ...verifyForm, [app.id]: { ...verifyForm[app.id], expected_value: e.target.value } })
                    }
                  />
                  <input
                    style={{ width: 140 }}
                    type="number"
                    step="any"
                    placeholder="Observed value"
                    onChange={(e) =>
                      setVerifyForm({ ...verifyForm, [app.id]: { ...verifyForm[app.id], observed_value: e.target.value } })
                    }
                  />
                  <input
                    style={{ width: 120 }}
                    type="number"
                    step="any"
                    placeholder="Tolerance"
                    onChange={(e) =>
                      setVerifyForm({ ...verifyForm, [app.id]: { ...verifyForm[app.id], tolerance: e.target.value } })
                    }
                  />
                  <input
                    style={{ width: 200 }}
                    placeholder="Remarks"
                    onChange={(e) =>
                      setVerifyForm({ ...verifyForm, [app.id]: { ...verifyForm[app.id], remarks: e.target.value } })
                    }
                  />
                </div>
                {error && <div className="error-text">{error}</div>}
                <button style={{ marginTop: 8 }} onClick={() => submitVerification(app.id)}>
                  Submit Verification Result
                </button>
              </div>
            )}
        </div>
      ))}
      {applications.length === 0 && <p className="muted">No applications found.</p>}
    </div>
  );
}
