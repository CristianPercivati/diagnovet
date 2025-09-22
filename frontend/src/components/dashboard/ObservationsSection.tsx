import React from "react";
import { Observation } from "@/types/patients";
import StatusBadge from "../common/StatusBadge";

interface ObservationsSectionProps {
  observations: Observation[];
  noDataMessage?: string;
  className?: string;
}

// Función para analizar la observación y determinar el estado
const getObservationStatus = (observacion: string): "normal" | "warning" | "critical" => {
  const lowerObs = observacion.toLowerCase();
  
  // Esta parte es una simulación de cómo me gustaría que quede la sección de observación
  // podría entrenarse un modelo para análisis de sentimientos que clasifique cada observación
  // o agregarla al prompt mismo.

  if (lowerObs.includes("normal") || 
      lowerObs.includes("sin hallazgos") ||
      lowerObs.includes("conservada") ||
      lowerObs.includes("conservados") ||
      lowerObs.includes("conservadas") ||
      lowerObs.includes("normales") ||
    lowerObs.includes("íntegro")) {
    return "normal";
  }
  
  if (lowerObs.includes("leve") || 
      lowerObs.includes("moderado") || 
      lowerObs.includes("aumento") ||
      lowerObs.includes("disminución") ||
      lowerObs.includes("ligero")) {
    return "warning";
  }
  
  if (lowerObs.includes("grave") || 
      lowerObs.includes("sever") || 
      lowerObs.includes("marcado") ||
      lowerObs.includes("significativo") ||
      lowerObs.includes("emergencia")) {
    return "critical";
  }
  
  return "warning"; 
};


const ObservationsSection: React.FC<ObservationsSectionProps> = ({
  observations,
  noDataMessage = "No hay observaciones disponibles para este estudio.",
  className = ""
}) => {
  if (!observations || observations.length === 0) {
    return (
      <div className={`info-section ${className}`}>
        <h4>Observaciones</h4>
        <div className="flex items-center justify-center p-8 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-gray-500 text-center">
            {noDataMessage}
          </p>
        </div>
      </div>
    );
  }

  // Agrupar observaciones por órgano
  const observationsByOrgan = observations.reduce((acc, obs) => {
    if (!acc[obs.organo]) {
      acc[obs.organo] = [];
    }
    acc[obs.organo].push(obs);
    return acc;
  }, {} as { [key: string]: Observation[] });

  return (
    <div className={`info-section ${className}`}>
      <h4>Observaciones</h4>
      <div className="space-y-4">
        {Object.entries(observationsByOrgan).map(([organo, organObservations]) => (
          <div key={organo} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Header del órgano */}
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <h5 className="font-semibold text-gray-800 capitalize">
                    {organo.toLowerCase()}
                  </h5>
                </div>
                <span className="text-sm text-gray-500">
                  {organObservations.length} observación{organObservations.length !== 1 ? 'es' : ''}
                </span>
              </div>
            </div>
            
            {/* Lista de observaciones del órgano */}
            <div className="divide-y divide-gray-100">
              {organObservations.map((observation, index) => {
                const status = getObservationStatus(observation.observacion);
                
                return (
                  <div key={index} className="px-4 py-3 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <StatusBadge 
                        status={status} 
                        size="small" 
                        showIcon={true}
                      />
                      <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                        #{index + 1}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 leading-relaxed">
                      {observation.observacion}
                    </p>
                    
                    {/* Indicadores de keywords */}
                    <div className="flex flex-wrap gap-1 mt-2">
                      {observation.observacion.split(/[.,;]/).map((phrase, phraseIndex) => {
                        const trimmedPhrase = phrase.trim();
                        if (trimmedPhrase.length > 3 && trimmedPhrase.length < 20) {
                          return (
                            <span 
                              key={phraseIndex}
                              className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded"
                            >
                              {trimmedPhrase}
                            </span>
                          );
                        }
                        return null;
                      }).filter(Boolean)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      
      {/* Resumen estadístico */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg border">
        <h5 className="font-semibold text-gray-800 mb-2">Resumen de Observaciones</h5>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {observations.length}
            </div>
            <div className="text-gray-600">Total</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {observations.filter(o => getObservationStatus(o.observacion) === 'normal').length}
            </div>
            <div className="text-gray-600">Normales</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {observations.filter(o => getObservationStatus(o.observacion) === 'critical').length}
            </div>
            <div className="text-gray-600">Críticas</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ObservationsSection;