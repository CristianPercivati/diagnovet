from typing import List, Optional
from repositories.base_repository import BaseRepository
from models.schemas import PatientCreate, PatientResponse, VeterinarianCreate, VeterinarianResponse
from monitoring.metrics import metrics_collector
import time
import logging

logger = logging.getLogger(__name__)

class PatientService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    async def get_all_patients(self) -> List[PatientResponse]:
        """Obtener todos los pacientes"""
        start_time = time.time()
        
        try:
            patients = await self.repository.get_patients()
            
            # Métricas
            metrics_collector.record_diagnosis_operation(
                "get_patients", 
                "success", 
                time.time() - start_time
            )
            
            logger.info(f"Obtenidos {len(patients)} pacientes")
            return patients
            
        except Exception as e:
            metrics_collector.record_diagnosis_operation("get_patients", "error")
            logger.error(f"Error obteniendo pacientes: {str(e)}")
            raise e
    
    async def create_patient(self, patient_data: PatientCreate) -> str:
        """Crear un nuevo paciente"""
        start_time = time.time()
        
        try:
            # Validaciones de negocio
            self._validate_patient_data(patient_data)
            
            # Convertir a dict para el repositorio
            patient_dict = {
                "nombre": patient_data.nombre,
                "tutor": patient_data.tutor,
                "edad": patient_data.edad
            }
            
            patient_id = await self.repository.create_patient(patient_dict)
            
            # Métricas
            metrics_collector.record_diagnosis_operation(
                "create_patient", 
                "success", 
                time.time() - start_time
            )
            
            logger.info(f"Paciente creado exitosamente: {patient_id}")
            return patient_id
            
        except ValueError as e:
            metrics_collector.record_diagnosis_operation("create_patient", "validation_error")
            logger.warning(f"Error de validación creando paciente: {str(e)}")
            raise e
        except Exception as e:
            metrics_collector.record_diagnosis_operation("create_patient", "error")
            logger.error(f"Error creando paciente: {str(e)}")
            raise e
    
    async def search_patients_by_tutor(self, tutor_name: str) -> List[PatientResponse]:
        """Buscar pacientes por nombre del tutor"""
        try:
            all_patients = await self.repository.get_patients()
            
            # Filtrar por tutor (case insensitive)
            filtered_patients = [
                patient for patient in all_patients
                if tutor_name.lower() in patient.tutor.lower()
            ]
            
            logger.info(f"Encontrados {len(filtered_patients)} pacientes para tutor '{tutor_name}'")
            return filtered_patients
            
        except Exception as e:
            logger.error(f"Error buscando pacientes por tutor '{tutor_name}': {str(e)}")
            raise e
    
    def _validate_patient_data(self, patient_data: PatientCreate):
        """Validaciones de negocio para pacientes"""
        
        # Validar nombre
        if not patient_data.nombre or len(patient_data.nombre.strip()) < 2:
            raise ValueError("El nombre del paciente debe tener al menos 2 caracteres")
        
        # Validar tutor
        if not patient_data.tutor or len(patient_data.tutor.strip()) < 2:
            raise ValueError("El nombre del tutor debe tener al menos 2 caracteres")
        
        # Validar edad
        if not patient_data.edad:
            raise ValueError("La edad del paciente es obligatoria")
        
        # Validar formato de edad (puede ser "5 años", "2 meses", etc.)
        edad_lower = patient_data.edad.lower().strip()
        if not any(unit in edad_lower for unit in ['año', 'mes', 'semana', 'día']):
            logger.warning(f"Formato de edad inusual: {patient_data.edad}")

class VeterinarianService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository
    
    async def create_veterinarian(self, vet_data: VeterinarianCreate) -> str:
        """Crear un nuevo veterinario"""
        start_time = time.time()
        
        try:
            # Validaciones de negocio
            self._validate_veterinarian_data(vet_data)
            
            # Convertir a dict para el repositorio
            vet_dict = {
                "nombre": vet_data.nombre,
                "apellido": vet_data.apellido,
                "matricula": vet_data.matricula
            }
            
            vet_id = await self.repository.create_veterinarian(vet_dict)
            
            # Métricas
            metrics_collector.record_diagnosis_operation(
                "create_veterinarian", 
                "success", 
                time.time() - start_time
            )
            
            logger.info(f"Veterinario creado exitosamente: {vet_id}")
            return vet_id
            
        except ValueError as e:
            metrics_collector.record_diagnosis_operation("create_veterinarian", "validation_error")
            logger.warning(f"Error de validación creando veterinario: {str(e)}")
            raise e
        except Exception as e:
            metrics_collector.record_diagnosis_operation("create_veterinarian", "error")
            logger.error(f"Error creando veterinario: {str(e)}")
            raise e
    
    async def get_veterinarian(self, vet_id: str) -> Optional[dict]:
        """Obtener veterinario por ID"""
        try:
            veterinarian = await self.repository.get_veterinarian(vet_id)
            
            if veterinarian:
                logger.info(f"Veterinario encontrado: {vet_id}")
            else:
                logger.warning(f"Veterinario no encontrado: {vet_id}")
            
            return veterinarian
            
        except Exception as e:
            logger.error(f"Error obteniendo veterinario {vet_id}: {str(e)}")
            raise e
    
    def _validate_veterinarian_data(self, vet_data: VeterinarianCreate):
        """Validaciones de negocio para veterinarios"""
        
        # Validar nombre
        if not vet_data.nombre or len(vet_data.nombre.strip()) < 2:
            raise ValueError("El nombre del veterinario debe tener al menos 2 caracteres")
        
        # Validar apellido
        if not vet_data.apellido or len(vet_data.apellido.strip()) < 2:
            raise ValueError("El apellido del veterinario debe tener al menos 2 caracteres")
        
        # Validar matrícula (opcional pero si está, debe ser válida)
        if vet_data.matricula is not None:
            if not isinstance(vet_data.matricula, int) or vet_data.matricula <= 0:
                raise ValueError("La matrícula debe ser un número positivo")