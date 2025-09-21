from typing import List, Optional
from repositories.base_repository import BaseRepository
from models.schemas import DiagnosisCreate, DiagnosisResponse, PatientResponse, SidebarDiagnosisItem
from monitoring.metrics import diagnosis_counter, diagnosis_duration
import time
import logging

logger = logging.getLogger(__name__)

class DiagnosisService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    async def create_diagnosis(self, diagnosis_data: DiagnosisCreate) -> str:
        """Crear un nuevo diagnóstico con validaciones de negocio"""
        start_time = time.time()
        
        try:
            # Validaciones de negocio
            self._validate_diagnosis_data(diagnosis_data)
            
            # Crear diagnóstico usando el repositorio
            diagnosis_id = await self.repository.create_diagnosis(diagnosis_data)
            
            # Métricas
            diagnosis_counter.labels(operation="create", status="success").inc()
            diagnosis_duration.labels(operation="create").observe(time.time() - start_time)
            
            logger.info(f"Diagnóstico creado exitosamente: {diagnosis_id}")
            return diagnosis_id
            
        except Exception as e:
            diagnosis_counter.labels(operation="create", status="error").inc()
            logger.error(f"Error creando diagnóstico: {str(e)}")
            raise e
    
    async def get_diagnosis(self, diagnosis_id: str) -> Optional[DiagnosisResponse]:
        """Obtener un diagnóstico por ID"""
        start_time = time.time()
        
        try:
            diagnosis = await self.repository.get_diagnosis(diagnosis_id)
            
            if diagnosis:
                diagnosis_counter.labels(operation="get", status="success").inc()
                logger.info(f"Diagnóstico encontrado: {diagnosis_id}")
            else:
                diagnosis_counter.labels(operation="get", status="not_found").inc()
                logger.warning(f"Diagnóstico no encontrado: {diagnosis_id}")
            
            diagnosis_duration.labels(operation="get").observe(time.time() - start_time)
            return diagnosis
            
        except Exception as e:
            diagnosis_counter.labels(operation="get", status="error").inc()
            logger.error(f"Error obteniendo diagnóstico {diagnosis_id}: {str(e)}")
            raise e

    async def get_all_diagnoses(self) -> List[SidebarDiagnosisItem]:
        """Obtener todos los diagnósticos"""
        try:
            return await self.repository.get_all_diagnoses()
        except Exception as e:
            logger.error(f"Error obteniendo diagnósticos: {str(e)}")
            raise e

    async def get_patients(self) -> List[PatientResponse]:
        """Obtener todos los pacientes"""
        try:
            return await self.repository.get_patients()
        except Exception as e:
            logger.error(f"Error obteniendo pacientes: {str(e)}")
            raise e
    
    def _validate_diagnosis_data(self, diagnosis_data: DiagnosisCreate):
        """Validaciones de negocio para el diagnóstico"""
        
        # Validar paciente
        if not diagnosis_data.paciente.nombre or not diagnosis_data.paciente.tutor:
            raise ValueError("Nombre y tutor del paciente son obligatorios")
        
        # Validar veterinario
        if not diagnosis_data.veterinario.nombre or not diagnosis_data.veterinario.apellido:
            raise ValueError("Nombre y apellido del veterinario son obligatorios")
        
        # Validar informe
        if not diagnosis_data.informe.diagnostico:
            raise ValueError("El diagnóstico no puede estar vacío")
        
        if not diagnosis_data.informe.fecha:
            raise ValueError("La fecha del informe es obligatoria")
        
        # Validar estudios
        for estudio in diagnosis_data.informe.estudios:
            if not estudio.tipo_estudio:
                raise ValueError("Tipo de estudio es obligatorio")
            
            # Validar mediciones
            for medicion in estudio.mediciones:
                if medicion.valor is None or medicion.valor < 0:
                    raise ValueError("El valor de la medición debe ser positivo")
                if not medicion.organo:
                    raise ValueError("El órgano de la medición es obligatorio")