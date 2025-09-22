import React from "react";
import { Study, Measurement } from "@/types/patients";

interface StudySelectorProps {
  studies: Study[];
  selectedValue: string;
  onStudyChange: (value: string, studyIndex: number | null, measurements: Measurement[]) => void;
  loading: boolean;
  className?: string;
}

const StudySelector: React.FC<StudySelectorProps> = ({
  studies,
  selectedValue,
  onStudyChange,
  loading,
  className = ""
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const selectedOption = e.target.selectedOptions[0];
    
    if (value === "normal") {
      onStudyChange(value, null, []);
      return;
    }

    const studyIndex = selectedOption.getAttribute("data-index");
    const measurementsJson = selectedOption.getAttribute("data-mediciones");
    
    const index = studyIndex !== null ? parseInt(studyIndex, 10) : null;
    const measurements = measurementsJson ? JSON.parse(measurementsJson) as Measurement[] : [];

    onStudyChange(value, index, measurements);
  };

  if (loading) {
    return (
      <select 
        className={`filter-select ${className}`}
        disabled
      >
        <option>Cargando estudios...</option>
      </select>
    );
  }

  if (!studies || studies.length === 0) {
    return (
      <select 
        className={`filter-select ${className}`}
        disabled
      >
        <option>No hay estudios disponibles</option>
      </select>
    );
  }

  return (
    <select 
      className={`filter-select ${className}`}
      value={selectedValue}
      onChange={handleChange}
    >
      <option value="normal">Normal</option>
      {studies.map((study, index) => {
        const organs = Array.from(new Set(study.mediciones.map((m: Measurement) => m.organo)));
        const organsText = organs.join(", ");

        return (
          <option
            key={index}
            value={organsText}
            data-index={index}
            data-mediciones={JSON.stringify(study.mediciones)}
          >
            {study.tipo_estudio || `Estudio ${index + 1}`}
          </option>
        );
      })}
    </select>
  );
};

export default StudySelector;