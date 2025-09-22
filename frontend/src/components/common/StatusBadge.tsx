import React from "react";

export type StatusType = 
  | "pending" 
  | "uploading" 
  | "success" 
  | "error" 
  | "normal" 
  | "warning" 
  | "critical";

interface StatusBadgeProps {
  status: StatusType;
  text?: string;
  size?: "small" | "medium";
  showIcon?: boolean;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  text,
  size = "medium",
}) => {
  const statusConfig = {
    pending: { 
      class: "bg-gray-100 text-gray-600", 
      defaultText: "Pendiente" 
    },
    uploading: { 
      class: "bg-blue-100 text-blue-700", 
      defaultText: "Enviando..." 
    },
    success: { 
      class: "bg-green-100 text-green-700", 
      defaultText: "Enviado" 
    },
    error: { 
      class: "bg-red-100 text-red-700", 
      defaultText: "Error" 
    },
    normal: { 
      class: "bg-green-100 text-green-700", 
      defaultText: "Normal" 
    },
    warning: { 
      class: "bg-yellow-100 text-yellow-700", 
      defaultText: "Advertencia" 
    },
    critical: { 
      class: "bg-red-100 text-red-700", 
      defaultText: "Crítico" 
    }
  };

  const config = statusConfig[status];
  const displayText = text || config.defaultText;
  const sizeClass = size === "small" ? "px-2 py-1 text-xs" : "px-3 py-1 text-sm";

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${sizeClass} ${config.class}`}>
      {displayText}
    </span>
  );
};

export default StatusBadge;