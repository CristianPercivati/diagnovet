"use client";

import React, { useState, useEffect } from "react";
import { PatientData, Study, Measurement } from "@/types/patient";
import TabNavigation from "./TabNavigation";
import StudySelector from "./StudySelector";
import DiagnosisSection from "./DiagnosisSection";
import ObservationsSection from "./ObservationsSection";
import MeasurementGrid from "./MeasurementGrid";
import ImageCarousel from "./ImageCarousel";
import LoadingSpinner from "../common/LoadingSpinner";

import { API_BASE_URL } from "@/app/config";

interface InfoTabsProps {
  patientData: PatientData | null;
  loading: boolean;
  onChangeImageMode: (organs: string[]) => void;
  onSelectImage: (imgUrl: string | null) => void;
  onChangeImageData: (data: Measurement[] | null) => void;
}

type TabType = "diagnostico" | "observaciones" | "mediciones" | "recomendaciones" | "imagenes";

const InfoTabs: React.FC<InfoTabsProps> = ({
  patientData,
  loading,
  onChangeImageMode,
  onSelectImage,
  onChangeImageData,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>("diagnostico");
  const [selectedValue, setSelectedValue] = useState<string>("normal");
  const [selectedStudyIndex, setSelectedStudyIndex] = useState<number | null>(null);
  const [images, setImages] = useState<string[]>([]);

  const tabs: TabType[] = ["diagnostico", "observaciones", "mediciones", "recomendaciones", "imagenes"];

  // Fetch imágenes cuando se selecciona la tab de imágenes
  useEffect(() => {
    
    if (activeTab !== "imagenes" || !patientData?.img_folder) return;
    console.log("asdasdasdas")
    const fetchImages = async () => {
      try {
        const folderUrl = patientData.img_folder;
        console.log("asdasd2",folderUrl)
        const response = await fetch(`${API_BASE_URL}/images/${folderUrl}`);
        const data = await response.json();
        setImages(data.images ?? []);
      } catch (error) {
        console.error("Error fetching images:", error);
        setImages([]);
      }
    };

    fetchImages();
  }, [activeTab, patientData]);

  useEffect(() => {
    setSelectedValue("normal");
    setSelectedStudyIndex(null);
    onChangeImageMode([]);
    onSelectImage(null);
    onChangeImageData(null);
  }, [patientData, onChangeImageMode, onSelectImage, onChangeImageData]);

  const handleStudyChange = (value: string, studyIndex: number | null, measurements: Measurement[]) => {
    setSelectedValue(value);
    setSelectedStudyIndex(studyIndex);

    if (value === "normal") {
      onChangeImageMode([]);
      onChangeImageData(null);
    } else {
      const organs = value.split(",").map(s => s.trim()).filter(Boolean);
      const normalizedOrgans = organs.map(org => 
        org.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
      );
      
      onChangeImageMode(normalizedOrgans);
      onChangeImageData(measurements);
    }
    
    onSelectImage(null);
  };

  const getCurrentStudy = (): Study | null => {
    if (selectedStudyIndex === null || !patientData?.estudios) return null;
    return patientData.estudios[selectedStudyIndex] || null;
  };

  const renderTabContent = () => {
    if (loading) {
      return <LoadingSpinner text="Cargando datos del paciente..." />;
    }

    if (!patientData) {
      return <p>No hay datos disponibles para el paciente seleccionado.</p>;
    }

    const currentStudy = getCurrentStudy();

    switch (activeTab) {
      case "diagnostico":
        return <DiagnosisSection diagnostico={patientData.diagnostico} />;

case "observaciones":
  return (
    <ObservationsSection 
      observations={currentStudy?.observaciones || []} 
      noDataMessage={!currentStudy ? "Selecciona un estudio para ver las observaciones" : "No hay observaciones para este estudio"}
    />
  );

      case "mediciones":
        return (
          <MeasurementGrid 
            measurements={currentStudy?.mediciones || []}
            noDataMessage={!currentStudy ? "Selecciona un estudio para ver las mediciones" : undefined}
          />
        );

      case "recomendaciones":
        return (
          <div className="info-section">
            <h4>📝 Recomendaciones</h4>
            <p>
              Seguimiento clínico recomendado con controles periódicos.
              Evaluar tratamiento para bronquitis crónica y control cardíaco.
            </p>
          </div>
        );

      case "imagenes":
        return (
          <ImageCarousel 
            images={images}
            selectedImage={null}
            onImageSelect={onSelectImage}
            loading={activeTab === "imagenes" && images.length === 0 && patientData.paciente.img_folder !== undefined}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="info-tabs">
      <div className="tab-nav">
        <TabNavigation 
          tabs={tabs} 
          activeTab={activeTab} 
          onTabChange={setActiveTab} 
        />
        
        <StudySelector
          studies={patientData?.estudios || []}
          selectedValue={selectedValue}
          onStudyChange={handleStudyChange}
          loading={loading}
        />
      </div>

      <div className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default InfoTabs;