from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# DTOs de entrada (requests)
class PatientCreate(BaseModel):
    nombre: str
    tutor: str
    edad: Optional[str] = None 
    raza: Optional[str] = None 

class VeterinarianCreate(BaseModel):
    nombre: str
    apellido: str
    matricula: Optional[int] = None

class MeasurementCreate(BaseModel):
    tipo_medicion: str
    valor: Optional[float] = 0
    unidad: Optional[str] = None
    organo: str

class ObservationCreate(BaseModel):
    organo: str
    observacion: str

class StudyCreate(BaseModel):
    tipo_estudio: str
    mediciones: List[MeasurementCreate] = []
    observaciones: List[ObservationCreate] = []

class DiagnosisCreate(BaseModel):
    paciente: PatientCreate
    veterinario: VeterinarianCreate
    informe: 'ReportCreate'

class ReportCreate(BaseModel):
    antecedentes: Optional[str] = None
    diagnostico: Optional[str] = None
    img_folder: Optional[str] = None
    fecha: Optional[str] = None
    referido: Optional[str] = None
    estudios: List[StudyCreate] = []

# DTOs de respuesta (responses)
class PatientResponse(BaseModel):
    id: str
    nombre: str
    tutor: str
    edad: Optional[str] = None
    raza: str

class VeterinarianResponse(BaseModel):
    id: str
    nombre: str
    apellido: str
    matricula: Optional[int] = None

class MeasurementResponse(BaseModel):
    id: str
    tipo_medicion: str
    valor: float
    organo: str
    unidad: Optional[str] = None

class ObservationResponse(BaseModel):
    id: str
    observacion: str
    organo: str

class StudyResponse(BaseModel):
    id: str
    tipo_estudio: str
    mediciones: List[MeasurementResponse] = []
    observaciones: List[ObservationResponse] = []

class DiagnosisResponse(BaseModel):
    id: str
    antecedentes: Optional[str] = None
    diagnostico: str
    fecha: date
    img_folder: Optional[str] = None
    paciente: PatientResponse
    veterinario: VeterinarianResponse
    estudios: List[StudyResponse] = []

class SidebarDiagnosisItem(BaseModel):
    id: str
    nombre: str
    tutor: str
    edad: Optional[str] = None
    raza: Optional[str] = None
    fecha: date

class ImageExtractResponse(BaseModel):
    status: str
    message: str
    folder: str

class ImagesResponse(BaseModel):
    status: str
    images: List[str]