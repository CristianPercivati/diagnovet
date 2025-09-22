"use client";

import React, { useState, useEffect } from "react";
import Sidebar from "@/components/dashboard/Sidebar";
import InfoTabs from "@/components/dashboard/InfoTabs";
import Viewer from "@/components/dashboard/Viewer";
import { API_BASE_URL } from '@/app/config'

export default function HomePage() {
  const [patients, setPatients] = useState<any[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [patientData, setPatientData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [imageMode, setImageMode] = useState<string[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imageData, setImageData] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/all_diagnoses`)
      .then((res) => res.json())
      .then((data) => setPatients(data))
      .catch(() => setPatients([]));
  }, []);

  useEffect(() => {
    if (!selectedPatientId) return;
    setLoading(true);
    fetch(`${API_BASE_URL}/diagnosis/${selectedPatientId}`)
      .then((res) => res.json())
      .then((data) => setPatientData(data))
      .finally(() => setLoading(false));
  }, [selectedPatientId]);

  useEffect(() => {
  if (patients.length > 0 && selectedPatientId === null) {
    setSelectedPatientId(patients[0].id);
  }
}, [patients, selectedPatientId]);

  return (
    <div className="screen dashboard-screen">
      <div className="main-content">
        <Sidebar
          patients={patients}
          selectedId={selectedPatientId ?? -1}
          onSelect={setSelectedPatientId}
        />
        <Viewer
          organs={imageMode}
          selectedImage={selectedImage}
          imageData={imageData}
          breed={patientData?.paciente.raza}
        />
      </div>

      <div className="bottom-panel rounded-b-lg">
        {selectedPatientId && (
          <InfoTabs
            patientData={patientData}
            loading={loading}
            onChangeImageMode={setImageMode}
            onSelectImage={setSelectedImage}
            onChangeImageData={setImageData}
          />
        )}
      </div>
    </div>
  );
}
