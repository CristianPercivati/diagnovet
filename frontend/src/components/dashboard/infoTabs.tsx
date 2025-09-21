"use client";

import React, { useState, useEffect } from "react";

interface InfoTabsProps {
  patientData: any;
  loading: boolean;
  onChangeImageMode: (organs: string[]) => void;
  onSelectImage: (imgUrl: string | null) => void;
  onChangeImageData: (data: any) => void;
}

const InfoTabs: React.FC<InfoTabsProps> = ({
  patientData,
  loading,
  onChangeImageMode,
  onSelectImage,
  onChangeImageData,
}) => {
  const [activeTab, setActiveTab] = useState("diagnostico");
  const [selectedValue, setSelectedValue] = useState<string>("normal");
  const [selectedStudyIndex, setSelectedStudyIndex] = useState<number | null>(
    0
  );
  const [images, setImages] = useState<string[]>([]);

  // fetch de imágenes (solo si cambio tab a "imagenes")
  useEffect(() => {
    if (activeTab !== "imagenes" || !patientData) return;
    const folderUrl = patientData?.img_folder;

    if (!folderUrl) return;

    fetch(`http://localhost:8000/images/${folderUrl}`)
      .then((res) => res.json())
      .then((data) => setImages(data.images ?? []))
      .catch(() => setImages([]));
  }, [activeTab, patientData]);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const selectedOption = e.target.selectedOptions[0];
    const mediciones = selectedOption
      ? selectedOption.dataset.mediciones
      : "[]";
    const medicionesParsed = JSON.parse(mediciones || "[]");

    setSelectedValue(value);

    if (value === "normal") {
      onChangeImageMode([]);
      setSelectedStudyIndex(-1);
    } else {
      const arr = value
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const normalize = (str: string) =>
        str
          .toLowerCase()
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "");

      const organsLower = arr.map(normalize);

      const indexAttr = selectedOption.getAttribute("data-index");
      const studyIndex = indexAttr !== null ? parseInt(indexAttr, 10) : null;

      setSelectedStudyIndex(studyIndex);
      onChangeImageMode(organsLower);
      onSelectImage(null);
      onChangeImageData(medicionesParsed);
    }
  };

  return (
    <div className="info-tabs">
      <div className="tab-nav">
        {["diagnostico", "observaciones", "mediciones", "recomendaciones", "imagenes"].map(
          (tab) => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? "active" : ""}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab[0].toUpperCase() + tab.slice(1)}
            </button>
          )
        )}

        <select className="filter-select" value={selectedValue} onChange={handleChange}>
          {loading ? (
            <option>Cargando...</option>
          ) : patientData?.estudios?.length ? (
            <>
              <option value="normal">Normal</option>
              {patientData.estudios.map((estudio: any, index: number) => {
                const organos = [
                  ...new Set(estudio.mediciones.map((m: any) => m.organo)),
                ];
                console.log("Estudios del paciente:", patientData?.estudios);

                return (
                  <option
                    key={index}
                    data-index={index}
                    value={organos.join(",")}
                    data-mediciones={JSON.stringify(estudio.mediciones)}
                  >
                    {estudio.tipo_estudio ?? `Estudio ${index + 1}`}
                  </option>
                );
              })}
            </>
          ) : (
            <option>No hay estudios disponibles</option>
          )}
        </select>
      </div>

      <div className="tab-content">
        {activeTab === "diagnostico" && (
          <div className="info-section">
            <h4>🎯 Diagnóstico Principal</h4>
            {loading ? (
              <p>Cargando...</p>
            ) : patientData ? (
              <ul>
                {(patientData.diagnostico
                  ? patientData.diagnostico.split(";").map((d: string) => d.trim())
                  : []
                ).map((diag: string, i: number) => (
                  <li key={i}>{diag}</li>
                ))}
              </ul>
            ) : (
              <p>No hay diagnóstico disponible.</p>
            )}
          </div>
        )}

        {activeTab === "observaciones" && selectedStudyIndex !== null && (
          <div className="info-section">
            <h4>👀 Observaciones</h4>
            {patientData?.estudios?.[selectedStudyIndex]?.observaciones?.map(
              (obs: any, i: number) => (
                <p key={i}>
                  <strong>{obs.organo}:</strong> {obs.observacion}
                </p>
              )
            )}
          </div>
        )}

        {activeTab === "mediciones" && selectedStudyIndex !== null && (
          <div className="info-section">
            <h4>📊 Mediciones Clave</h4>
            <div className="measurement-grid">
              {patientData?.estudios?.[selectedStudyIndex]?.mediciones?.map(
                (m: any, i: number) => (
                  <div key={i} className="measurement-card">
                    <div className="measurement-label">{m.tipo_medicion}</div>
                    <div className="measurement-value">
                      {m.valor} {m.unidad ?? ""}
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        )}

        {activeTab === "recomendaciones" && (
          <div className="info-section">
            <h4>📝 Recomendaciones</h4>
            <p>
              Seguimiento clínico recomendado con controles periódicos.
              Evaluar tratamiento para bronquitis crónica y control cardíaco.
            </p>
          </div>
        )}

        {activeTab === "imagenes" && (
          <div className="info-section">
            <h4>🖼️ Imágenes</h4>
            {loading ? (
              <p>Cargando...</p>
            ) : images.length ? (
              <div className="carousel-container">
                {images.map((imgUrl, i) => (
                  <div
                    key={i}
                    className="carousel-image"
                    onClick={() => onSelectImage(imgUrl)}
                  >
                    <img
                      src={`http://localhost:8000${imgUrl}`}
                      alt={`Imagen ${i + 1}`}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <p>No hay imágenes disponibles.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default InfoTabs;
