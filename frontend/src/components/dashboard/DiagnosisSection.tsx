import React from "react";

interface DiagnosisSectionProps {
  diagnostico?: string;
}

const DiagnosisSection: React.FC<DiagnosisSectionProps> = ({ diagnostico }) => {
  const diagnoses = diagnostico ? diagnostico.split(";").map(d => d.trim()) : [];

  return (
    <div className="info-section">
      <h4>🎯 Diagnóstico Principal</h4>
      {diagnoses.length > 0 ? (
        <ul className="space-y-2">
          {diagnoses.map((diag, i) => (
            <li key={i} className="flex items-start">
              <span className="mr-2">•</span>
              <span>{diag}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p>No hay diagnóstico disponible.</p>
      )}
    </div>
  );
};

export default DiagnosisSection;