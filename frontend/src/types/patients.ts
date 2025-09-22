export interface Patient {
  id: number;
  nombre: string;
  raza?: string;
  edad: string;
  tutor: string;
  fecha: string;
  img_folder?: string;
}

export interface Observation {
  organo: string;
  observacion: string;
}

export interface Measurement {
  organo: string;
  tipo_medicion: string;
  valor: number;
  unidad?: string;
}

export interface Study {
  tipo_estudio?: string;
  observaciones: Observation[];
  mediciones: Measurement[];
}

export interface PatientData {
  paciente: Patient;
  estudios: Study[];
  diagnostico?: string;
}