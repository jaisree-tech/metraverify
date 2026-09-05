import React, { useEffect, useState } from "react";
import api from "../api";

export default function Admin() {
  const [users, setUsers] = useState([]);

  const load = () => api.get("/admin/users").then((res) => setUsers(res.data));

  useEffect(() => {
    load();
  }, []);

  const promote = async (id) => {
    await api.post(`/admin/users/${id}/make-officer`);
    load();
  };

  return (
    <div className="container">
      <h2>Admin — User Management</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.name}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
              <td>
                {u.role === "USER" && (
                  <button onClick={() => promote(u.id)}>Make LMO Officer</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
