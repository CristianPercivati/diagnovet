'use client'
import { API_BASE_URL } from "@/app/config";
import React, { useState, useRef } from "react";


interface OverlayProps {
  component: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  active: boolean;
  danger: 0 | 1 | 2;
  onClick: () => void;
}

const Viewer: React.FC = ({ organs = [], selectedImage, imageData, breed=''  }) => {
  const [activeOverlay, setActiveOverlay] = useState<number | null>(0);
  console.log('[Viewer] organs prop raw:', breed);
const overlays = {
  normal: [],
  mid_body: [
  { src: "/assets/viewer/mid_body/media_bazo.svg", active: organs.includes("bazo"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_corazon.svg", active: organs.includes("corazon"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_diafragma.svg", active: organs.includes("diafragma"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_esofago.svg", active: organs.includes("esofago"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_estomago.svg", active: organs.includes("estomago"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_higado.svg", active: organs.includes("higado"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_intestino_grueso.svg", active: organs.includes("intestino grueso"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_intestino_delgado.svg", active: organs.includes("intestino delgado"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_pancreas.svg", active: organs.includes("pancreas"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_pulmon.svg", active: organs.includes("pulmon"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_rinon.svg", active: organs.includes("rinon"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_vejiga.svg", active: organs.includes("vejiga"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_traquea.svg", active: organs.includes("traquea"), danger: 1 },
  { src: "/assets/viewer/mid_body/media_vesicula_biliar.svg", active: organs.includes("vesicula biliar"), danger: 1 },
  ],
  neck: [],
  head: [],
  urinary_system_female: [
    { src: "/assets/viewer/urinary_system/glandula_suprarenal.svg", active: organs.includes("glándula suprarrenal"), danger: 1 },
    { src: "/assets/viewer/urinary_system/utero.svg", active: organs.includes("útero"), danger: 1 },
    { src: "/assets/viewer/urinary_system/ovario_izquierdo.svg", active: organs.includes("ovario"), danger: 1 },
  ]
};
let mode = "normal"
const razaAImagen = {
  'doberman': "/assets/viewer/dog_1/dog_1.svg",
  'caniche': "/assets/viewer/dog_1/dog_3.png",
  'schnauzer miniatura': "/assets/viewer/dog_1/dog_2.png",
  'schnauzer mini': "/assets/viewer/dog_1/dog_2.png"
};

const baseImages = {
  normal: razaAImagen[breed?.toLowerCase()] || "/assets/viewer/dog_1/dog_1.svg",
  mid_body: "/assets/viewer/mid_body/media_base.png",
  neck: "",
  head: "",
  urinary_system_female: "/assets/viewer/urinary_system/urinary_base.svg"
}

if (!selectedImage) {
const midBodyOrgans = [
    "corazon",
    "pulmon",
    "bazo",
    "diafragma",
    "esofago",
    "estomago",
    "higado",
    "intestino delgado",
    "intestino grueso",
    "pancreas",
    "rinon",
    "vejiga",
    "traquea",
    "vesicula biliar"
  ];

  if (midBodyOrgans.some(o => organs.includes(o))) {
    mode = "mid_body";
  }
const urinaryFemale = [
    "glándula suprarrenal",
    'útero',
    'ovario',
    'ovario izquierdo',
    'ovario derecho'
  ];

  if (urinaryFemale.some(o => organs.includes(o))) {
    mode = "urinary_system_female";
  }}
  const baseImage = selectedImage ? `${API_BASE_URL}${selectedImage}` : (baseImages[mode] || baseImages["normal"]);
  const zoomRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!zoomRef.current) return;
    const rect = zoomRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    zoomRef.current.style.transformOrigin = `${x}% ${y}%`;
  };

  const handleMouseEnter = () => {
    if (zoomRef.current) zoomRef.current.style.transform = `scale(1.5)`;
  };

  const handleMouseLeave = () => {
    if (zoomRef.current) {
      zoomRef.current.style.transform = "scale(1)";
      zoomRef.current.style.transformOrigin = "center center";
    }
  };

  return (
    <div className="viewer-container">
      <div className="viewer-header">
        <h2 className="viewer-title">Visor anatómico</h2>

        {/*
        <div className="view-controls">
          <button className="control-btn active">Órganos</button>
          <button className="control-btn">Radiografía</button>
        </div>
        */}
      </div>

      <div className="anatomy-viewer">
        <div className="anatomy-model" style={{ position: 'relative' }}>
            <img src={baseImage} alt="Anatomía del paciente" style={{ width: 'auto', height: '100%'}} />

     {!selectedImage && overlays[mode].filter(o => o.active).map((overlay, i) => (
            <div
              key={i}
              ref={zoomRef}
              onMouseMove={handleMouseMove}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                backgroundImage: `url(${overlay.src})`,
                backgroundSize: "contain",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
                alignItems: "center",
                opacity: 0.8,
                transition: "transform 0.3s ease, transform-origin 0.1s",
                pointerEvents: "none",
              }}
            />
          ))}

          {selectedImage && (
            <div
              ref={zoomRef}
              onMouseMove={handleMouseMove}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                
                height: "500px",
                backgroundImage: `url(${selectedImage || baseImage})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                transition: "transform 0.3s ease, transform-origin 0.1s",
              }}
            />
          )}
</div>
      </div>
    </div>
  );
};

export default Viewer;
