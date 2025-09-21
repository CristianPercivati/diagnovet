from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from models.schemas import DiagnosisCreate, DiagnosisResponse, PatientResponse, SidebarDiagnosisItem

class BaseRepository(ABC):
    """Interfaz base para repositorios (DAO Pattern)"""
    
    @abstractmethod
    async def create_diagnosis(self, diagnosis_data: DiagnosisCreate) -> str:
        """Crear un nuevo diagnóstico"""
        pass
    
    @abstractmethod
    async def get_diagnosis(self, diagnosis_id: str) -> Optional[DiagnosisResponse]:
        """Obtener un diagnóstico por ID"""
        pass

    @abstractmethod
    async def get_all_diagnoses(self) -> List[SidebarDiagnosisItem]:
        """Obtener todos los diagnósticos"""
        pass
    
    @abstractmethod
    async def get_patients(self) -> List[PatientResponse]:
        """Obtener todos los pacientes"""
        pass
    
    @abstractmethod
    async def create_patient(self, patient_data: Dict[str, Any]) -> str:
        """Crear un nuevo paciente"""
        pass
    
    @abstractmethod
    async def get_veterinarian(self, vet_id: str) -> Optional[Dict[str, Any]]:
        """Obtener veterinario por ID"""
        pass
    
    @abstractmethod
    async def create_veterinarian(self, vet_data: Dict[str, Any]) -> str:
        """Crear un nuevo veterinario"""
        pass