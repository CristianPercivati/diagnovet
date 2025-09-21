from typing import List, Optional, Dict, Any
from google.cloud import firestore
from models.schemas import DiagnosisCreate, DiagnosisResponse, PatientResponse, SidebarDiagnosisItem
from repositories.base_repository import BaseRepository
import uuid
from datetime import datetime

class FirestoreRepository(BaseRepository):
    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
        self.collections = {
            'patients': 'pacientes',
            'veterinarians': 'veterinarios',
            'diagnoses': 'diagnosticos',
            'studies': 'estudios',
            'measurements': 'mediciones',
            'observations': 'observaciones'
        }
    
    async def create_diagnosis(self, diagnosis_data: DiagnosisCreate) -> str:
        try:
            # Crear referencias
            diagnosis_id = str(uuid.uuid4())
            patient_id = str(uuid.uuid4())
            vet_id = str(uuid.uuid4())
            
            batch = self.db.batch()
            
            # Crear paciente
            patient_ref = self.db.collection(self.collections['patients']).document(patient_id)
            batch.set(patient_ref, {
                'nombre': diagnosis_data.paciente.nombre,
                'tutor': diagnosis_data.paciente.tutor,
                'edad': diagnosis_data.paciente.edad,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            
            # Crear veterinario
            vet_ref = self.db.collection(self.collections['veterinarians']).document(vet_id)
            batch.set(vet_ref, {
                'nombre': diagnosis_data.veterinario.nombre,
                'apellido': diagnosis_data.veterinario.apellido,
                'matricula': diagnosis_data.veterinario.matricula,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            
            # Crear diagnóstico
            diagnosis_ref = self.db.collection(self.collections['diagnoses']).document(diagnosis_id)
            batch.set(diagnosis_ref, {
                'antecedentes': diagnosis_data.informe.antecedentes,
                'diagnostico': diagnosis_data.informe.diagnostico,
                'img_folder': diagnosis_data.informe.img_folder,
                'fecha': diagnosis_data.informe.fecha,
                'referido': diagnosis_data.informe.referido,
                'patient_id': patient_id,
                'veterinarian_id': vet_id,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            
            # Crear estudios
            for estudio_data in diagnosis_data.informe.estudios:
                study_id = str(uuid.uuid4())
                study_ref = self.db.collection(self.collections['studies']).document(study_id)
                
                batch.set(study_ref, {
                    'tipo_estudio': estudio_data.tipo_estudio,
                    'diagnosis_id': diagnosis_id,
                    'created_at': firestore.SERVER_TIMESTAMP
                })
                
                # Crear mediciones
                for medicion in estudio_data.mediciones:
                    measurement_id = str(uuid.uuid4())
                    measurement_ref = self.db.collection(self.collections['measurements']).document(measurement_id)
                    
                    batch.set(measurement_ref, {
                        'tipo_medicion': medicion.tipo_medicion,
                        'valor': medicion.valor,
                        'unidad': medicion.unidad,
                        'organo': medicion.organo,
                        'study_id': study_id,
                        'created_at': firestore.SERVER_TIMESTAMP
                    })
                
                # Crear observaciones
                for obs in estudio_data.observaciones:
                    obs_id = str(uuid.uuid4())
                    obs_ref = self.db.collection(self.collections['observations']).document(obs_id)
                    
                    batch.set(obs_ref, {
                        'observacion': obs.observacion,
                        'organo': obs.organo,
                        'study_id': study_id,
                        'created_at': firestore.SERVER_TIMESTAMP
                    })
            
            batch.commit()
            return diagnosis_id
            
        except Exception as e:
            raise e
    
    async def get_diagnosis(self, diagnosis_id: str) -> Optional[DiagnosisResponse]:
        try:
            # Obtener diagnóstico principal
            diagnosis_doc = self.db.collection(self.collections['diagnoses']).document(diagnosis_id).get()
            
            if not diagnosis_doc.exists:
                return None
            
            diagnosis_data = diagnosis_doc.to_dict()
            
            # Obtener paciente
            patient_doc = self.db.collection(self.collections['patients']).document(
                diagnosis_data['patient_id']
            ).get()
            patient_data = patient_doc.to_dict()
            
            # Obtener veterinario
            vet_doc = self.db.collection(self.collections['veterinarians']).document(
                diagnosis_data['veterinarian_id']
            ).get()
            vet_data = vet_doc.to_dict()
            
            # Obtener estudios
            studies_query = self.db.collection(self.collections['studies']).where(
                'diagnosis_id', '==', diagnosis_id
            ).get()
            
            estudios = []
            for study_doc in studies_query:
                study_data = study_doc.to_dict()
                study_id = study_doc.id
                
                # Obtener mediciones del estudio
                measurements_query = self.db.collection(self.collections['measurements']).where(
                    'study_id', '==', study_id
                ).get()
                
                mediciones = [doc.to_dict() for doc in measurements_query]
                
                # Obtener observaciones del estudio
                observations_query = self.db.collection(self.collections['observations']).where(
                    'study_id', '==', study_id
                ).get()
                
                observaciones = [doc.to_dict() for doc in observations_query]
                
                estudios.append({
                    'id': study_id,
                    'tipo_estudio': study_data['tipo_estudio'],
                    'mediciones': mediciones,
                    'observaciones': observaciones
                })
            
            return DiagnosisResponse(
                id=diagnosis_id,
                antecedentes=diagnosis_data.get('antecedentes'),
                diagnostico='; '.join(diagnosis_data['diagnostico']) if isinstance(diagnosis_data['diagnostico'], list) else diagnosis_data['diagnostico'],
                fecha=datetime.strptime(diagnosis_data['fecha'], '%Y-%m-%d').date(),
                img_folder=diagnosis_data.get('img_folder'),
                paciente=PatientResponse(
                    id=diagnosis_data['patient_id'],
                    nombre=patient_data['nombre'],
                    tutor=patient_data['tutor'],
                    edad=patient_data['edad']
                ),
                veterinario=VeterinarianResponse(
                    id=diagnosis_data['veterinarian_id'],
                    nombre=vet_data['nombre'],
                    apellido=vet_data['apellido'],
                    matricula=vet_data.get('matricula')
                ),
                estudios=[]  # Se puede expandir según necesidades
            )
            
        except Exception as e:
            raise e

    async def get_all_diagnoses(self) -> List[SidebarDiagnosisItem]:
        try:
            diagnoses_query = self.db.collection(self.collections['diagnoses']).get()
            sidebar_items = []
            
            for doc in diagnoses_query:
                diagnosis_data = doc.to_dict()
                
                # Obtener paciente
                patient_doc = self.db.collection(self.collections['patients']).document(
                    diagnosis_data['patient_id']
                ).get()
                
                if patient_doc.exists:
                    patient_data = patient_doc.to_dict()
                    
                    sidebar_items.append(
                        SidebarDiagnosisItem(
                            id=int(doc.id),  # Convertir a int para coincidir con el schema
                            nombre=patient_data.get('nombre', ''),
                            tutor=patient_data.get('tutor', ''),
                            edad=patient_data.get('edad', ''),
                            raza=patient_data.get('raza', None),  # Usar None si no existe
                            fecha=diagnosis_data.get('fecha')  # Ya debería ser date object
                        )
                    )
            
            return sidebar_items
            
        except Exception as e:
            raise e
            
    async def get_patients(self) -> List[PatientResponse]:
        try:
            patients_query = self.db.collection(self.collections['patients']).get()
            return [
                PatientResponse(
                    id=doc.id,
                    nombre=doc.to_dict()['nombre'],
                    tutor=doc.to_dict()['tutor'],
                    edad=doc.to_dict()['edad']
                ) for doc in patients_query
            ]
        except Exception as e:
            raise e
    
    # Implementar métodos restantes del BaseRepository
    async def create_patient(self, patient_data: Dict[str, Any]) -> str:
        patient_id = str(uuid.uuid4())
        patient_ref = self.db.collection(self.collections['patients']).document(patient_id)
        patient_ref.set({
            **patient_data,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return patient_id
    
    async def get_veterinarian(self, vet_id: str) -> Optional[Dict[str, Any]]:
        doc = self.db.collection(self.collections['veterinarians']).document(vet_id).get()
        return doc.to_dict() if doc.exists else None
    
    async def create_veterinarian(self, vet_data: Dict[str, Any]) -> str:
        vet_id = str(uuid.uuid4())
        vet_ref = self.db.collection(self.collections['veterinarians']).document(vet_id)
        vet_ref.set({
            **vet_data,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return vet_id