interface PatientCardProps {
  patient: any;
  isSelected: boolean;
  onClick: () => void;
}

const PatientCard: React.FC<PatientCardProps> = ({ patient, isSelected, onClick }) => {
  return (
    <div className={`patient-item ${isSelected ? "active" : ""}`} onClick={onClick}>
      <div className="patient-name">{patient.nombre}</div>
      <div className="patient-info">
        {patient.raza ?? "Sin raza"}, {patient.edad}
        <br />
        Tutor: {patient.tutor}
        <br />
        <span style={{ color: isSelected ? "#4CAF50" : "#666" }}>
          📅 {patient.fecha}
        </span>
      </div>
    </div>
  );
};

export default PatientCard