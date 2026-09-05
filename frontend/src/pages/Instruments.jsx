import React, { useEffect, useState } from "react";
import api from "../api";

const emptyForm = {
  instrument_type: "",
  manufacturer: "",
  model: "",
  serial_number: "",
  capacity: "",
  location: "",
  year_of_manufacture: "",
};

export default function Instruments() {
  const [instruments, setInstruments] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");

  const load = () => api.get("/instruments/").then((res) => setInstruments(res.data));

  useEffect(() => {
    load();
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const payload = {
        ...form,
        year_of_manufacture: form.year_of_manufacture ? Number(form.year_of_manufacture) : null,
      };
      await api.post("/instruments/", payload);
      setForm(emptyForm);
      setShowForm(false);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to add instrument");
    }
  };

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>My Instruments</h2>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ Add Instrument"}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <form onSubmit={handleSubmit}>
            <input name="instrument_type" placeholder="Instrument Type (e.g. Electronic Weighing Scale)" value={form.instrument_type} onChange={handleChange} required />
            <input name="manufacturer" placeholder="Manufacturer" value={form.manufacturer} onChange={handleChange} />
            <input name="model" placeholder="Model Number" value={form.model} onChange={handleChange} />
            <input name="serial_number" placeholder="Serial Number" value={form.serial_number} onChange={handleChange} />
            <input name="capacity" placeholder="Capacity (e.g. 500 kg)" value={form.capacity} onChange={handleChange} />
            <input name="location" placeholder="Location of Use" value={form.location} onChange={handleChange} />
            <input name="year_of_manufacture" type="number" placeholder="Year of Manufacture" value={form.year_of_manufacture} onChange={handleChange} />
            {error && <div className="error-text">{error}</div>}
            <button type="submit">Save Instrument</button>
          </form>
        </div>
      )}

      <table>
        <thead>
          <tr>
            <th>Registration ID</th>
            <th>Type</th>
            <th>Manufacturer</th>
            <th>Serial No.</th>
            <th>Location</th>
          </tr>
        </thead>
        <tbody>
          {instruments.map((i) => (
            <tr key={i.id}>
              <td>{i.registration_id}</td>
              <td>{i.instrument_type}</td>
              <td>{i.manufacturer}</td>
              <td>{i.serial_number}</td>
              <td>{i.location}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {instruments.length === 0 && <p className="muted">No instruments yet. Add one to get started.</p>}
    </div>
  );
}
