"use client";
import React from "react";

interface SidebarProps {
  patients: any[];
  onSelect: (id: number) => void;
  selectedId: number;
}

const Sidebar: React.FC<SidebarProps> = ({ patients, onSelect, selectedId }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-title">🐕 Pacientes</div>

      {patients.length === 0 ? (
        <p>No hay pacientes disponibles</p>
      ) : (
        patients.map((p) => (
          <div
            key={p.id}
            className={`patient-item ${selectedId === p.id ? "active" : ""}`}
            onClick={() => onSelect(p.id)}
          >
            <div className="patient-name">{p.nombre}</div>
            <div className="patient-info">
              {p.raza ?? "Sin raza"}, {p.edad}
              <br />
              Tutor: {p.tutor}
              <br />
              <span
                style={{ color: selectedId === p.id ? "#4CAF50" : "#666" }}
              >
                📅 {p.fecha}
              </span>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default Sidebar;
