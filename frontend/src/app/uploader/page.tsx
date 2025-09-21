"use client";

import React, { useState } from "react";

interface FileStatus {
  file: File;
  status: "pending" | "uploading" | "success" | "error";
}

export default function HomePage() {
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<FileStatus[]>([]);

  // Selección de archivos
  const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const newFiles: FileStatus[] = Array.from(e.target.files).map((f) => ({
      file: f,
      status: "pending",
    }));
    setFiles(newFiles);
  };

  // Enviar archivos uno por uno
  const uploadFiles = async () => {
    setLoading(true);
    const updatedFiles = [...files];

    for (let i = 0; i < updatedFiles.length; i++) {
      updatedFiles[i].status = "uploading";
      setFiles([...updatedFiles]);

      try {
        const formData = new FormData();
        formData.append("file", updatedFiles[i].file);

        const res = await fetch(
          "http://localhost:5678/webhook/pdf-upload",
          {
            method: "POST",
            body: formData,
          }
        );

        if (!res.ok) throw new Error("Error en pipeline");

        updatedFiles[i].status = "success";
      } catch (err) {
        updatedFiles[i].status = "error";
      }

      setFiles([...updatedFiles]);
    }

    setLoading(false);
  };

  return (
    <div className="screen dashboard-screen flex items-center justify-center p-8">
      <div className="uploader w-full max-w-lg bg-white rounded-2xl shadow-lg p-8 flex flex-col gap-6">
        <h3 className="text-2xl font-semibold text-gray-800 flex items-center gap-2">
          Subir PDFs al pipeline
        </h3>

        {/* Botón para seleccionar archivos */}
        <label className="cursor-pointer inline-block">
          <input
            type="file"
            multiple
            accept="application/pdf"
            onChange={handleFilesChange}
            className="hidden"
          />
          <div className="bg-blue-500 hover:bg-green-600 text-white font-medium px-6 py-3 rounded-xl text-center transition">
            Seleccionar archivos
          </div>
        </label>

        {/* Lista de archivos */}
        {files.length > 0 && (
          <ul className="file-list flex flex-col gap-3 max-h-60 overflow-y-auto">
            {files.map((f, i) => {
              let statusClass = "";
              let statusText = "";

              switch (f.status) {
                case "pending":
                  statusClass = "bg-gray-100 text-gray-600";
                  statusText = "⏳ Pendiente";
                  break;
                case "uploading":
                  statusClass = "bg-blue-100 text-blue-700";
                  statusText = "⬆️ Enviando...";
                  break;
                case "success":
                  statusClass = "bg-green-100 text-green-700";
                  statusText = "✅ Enviado";
                  break;
                case "error":
                  statusClass = "bg-red-100 text-red-700";
                  statusText = "❌ Error";
                  break;
              }

              return (
                <li
                  key={i}
                  className={`flex justify-between items-center p-3 rounded-xl border border-gray-200 ${statusClass}`}
                >
                  <span className="truncate">{f.file.name}</span>
                  <span className="font-medium">{statusText}</span>
                </li>
              );
            })}
          </ul>
        )}

        {/* Botón enviar */}
        <button
          onClick={uploadFiles}
          disabled={
            loading ||
            files.length === 0 ||
            files.every((f) => f.status === "success")
          }
          className={`w-full py-3 rounded-xl font-semibold text-white transition ${
            loading || files.every((f) => f.status === "success")
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-green-500 hover:bg-green-600"
          }`}
        >
          {loading ? "Procesando..." : "Enviar al pipeline"}
        </button>
      </div>
    </div>
  );
}
