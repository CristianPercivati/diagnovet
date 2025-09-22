"use client";

import React, { useState } from "react";
import { API_BASE_URL } from "@/app/config";
import LoadingSpinner from "../common/LoadingSpinner";

interface ImageCarouselProps {
  images: string[];
  selectedImage: string | null;
  onImageSelect: (imgUrl: string) => void;
  loading?: boolean;
  className?: string;
}

const ImageCarousel: React.FC<ImageCarouselProps> = ({
  images,
  selectedImage,
  onImageSelect,
  loading = false,
  className = ""
}) => {

  const handleImageClick = (imgUrl: string, index: number) => {
      onImageSelect(imgUrl);
  };

  const getImageUrl = (imgPath: string): string => {
    if (imgPath.startsWith('http')) return imgPath;
    return `${API_BASE_URL}${imgPath}`;
  };

  if (loading) {
    return (
      <div className={`image-carousel ${className}`}>
        <div className="carousel-title">
          Imágenes del Estudio
        </div>
        <div className="flex justify-center items-center h-32">
          <LoadingSpinner text="Cargando imágenes..." size="small" />
        </div>
      </div>
    );
  }

  if (!images || images.length === 0) {
    return (
      <div className={`image-carousel ${className}`}>
        <div className="carousel-title">
          Imágenes del Estudio
        </div>
        <div className="flex justify-center items-center h-32 text-gray-500">
          No hay imágenes disponibles
        </div>
      </div>
    );
  }

  return (
    <div className={`image-carousel ${className}`}>
      <div className="carousel-title">
        Imágenes del Estudio
        <span className="text-sm text-gray-500 ml-2">
          ({images.length} {images.length === 1 ? 'imagen' : 'imágenes'})
        </span>
      </div>
      
      <div className="carousel-container">
        {images.map((imgUrl, index) => {
          const fullImageUrl = getImageUrl(imgUrl);
          const isSelected = selectedImage === fullImageUrl;

          return (
            <div
              key={index}
              className={`carousel-image ${isSelected ? 'active' : ''}`}
              onClick={() => handleImageClick(fullImageUrl, index)}
              title={`Imagen ${index + 1}`}
            >
             
                <img
                  src={fullImageUrl}
                  alt={`Imagen de estudio ${index + 1}`}
                  className="w-full h-full object-cover rounded"
                  loading="lazy"
                />
              
              
              {/* Badge de número */}
              <div className="absolute bottom-1 right-1 bg-black bg-opacity-50 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {index + 1}
              </div>
            </div>
          );
        })}
      </div>

      {/* Indicador de imagen seleccionada */}
      {selectedImage && (
        <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded text-sm text-green-700">
          ✅ Imagen seleccionada para vista detallada
        </div>
      )}

      {/* Controles de navegación para muchos elementos */}
      {images.length > 8 && (
        <div className="flex justify-between items-center mt-3 text-xs text-gray-500">
          <span>← Desliza para ver más →</span>
          <span>{images.length} imágenes</span>
        </div>
      )}
    </div>
  );
};

export default ImageCarousel;