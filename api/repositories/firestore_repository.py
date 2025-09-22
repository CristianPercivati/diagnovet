from typing import List, Optional, Dict, Any
from google.cloud import firestore
from models.schemas import (
    DiagnosisCreate, DiagnosisResponse, PatientResponse, VeterinarianResponse,
    StudyResponse, MeasurementResponse, ObservationResponse, SidebarDiagnosisItem
)
from repositories.base_repository import BaseRepository
import uuid
from datetime import datetime
import os


class FirestoreRepository(BaseRepository):
    def __init__(self, project_id: str, credentials_path: str = None):
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
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
            diagnosis_id = str(uuid.uuid4())
            patient_id = str(uuid.uuid4())
            vet_id = str(uuid.uuid4())

            batch = self.db.batch()

            # Paciente
            patient_ref = self.db.collection(self.collections['patients']).document(patient_id)
            batch.set(patient_ref, {
                'nombre': diagnosis_data.paciente.nombre,
                'tutor': diagnosis_data.paciente.tutor,
                'edad': diagnosis_data.paciente.edad,
                'raza': getattr(diagnosis_data.paciente, 'raza', None),
                'created_at': firestore.SERVER_TIMESTAMP
            })

            # Veterinario
            vet_ref = self.db.collection(self.collections['veterinarians']).document(vet_id)
            batch.set(vet_ref, {
                'nombre': diagnosis_data.veterinario.nombre,
                'apellido': diagnosis_data.veterinario.apellido,
                'matricula': diagnosis_data.veterinario.matricula,
                'created_at': firestore.SERVER_TIMESTAMP
            })

            # Diagnóstico
            diagnostico = diagnosis_data.informe.diagnostico
            if isinstance(diagnostico, list):
                diagnostico = "; ".join(diagnostico)

            fecha_obj = None
            if diagnosis_data.informe.fecha:
                fecha_obj = datetime.strptime(diagnosis_data.informe.fecha, "%d/%m/%Y")

            diagnosis_ref = self.db.collection(self.collections['diagnoses']).document(diagnosis_id)
            batch.set(diagnosis_ref, {
                'antecedentes': diagnosis_data.informe.antecedentes,
                'diagnostico': diagnostico,
                'img_folder': diagnosis_data.informe.img_folder,
                'fecha': fecha_obj if fecha_obj else None,
                'patient_id': patient_id,
                'veterinarian_id': vet_id,
                'created_at': firestore.SERVER_TIMESTAMP
            })

            # Estudios
            for estudio_data in diagnosis_data.informe.estudios:
                study_id = str(uuid.uuid4())
                study_ref = self.db.collection(self.collections['studies']).document(study_id)

                batch.set(study_ref, {
                    'tipo_estudio': estudio_data.tipo_estudio,
                    'diagnosis_id': diagnosis_id,
                    'created_at': firestore.SERVER_TIMESTAMP
                })

                # Mediciones
                for medicion in estudio_data.mediciones:
                    measurement_id = str(uuid.uuid4())
                    measurement_ref = self.db.collection(self.collections['measurements']).document(measurement_id)

                    batch.set(measurement_ref, {
                        'tipo_medicion': medicion.tipo_medicion,
                        'valor': str(medicion.valor) if medicion.valor is not None else None,
                        'unidad': medicion.unidad,
                        'organo': medicion.organo,
                        'study_id': study_id,
                        'created_at': firestore.SERVER_TIMESTAMP
                    })

                # Observaciones
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
            diagnosis_doc = self.db.collection(self.collections['diagnoses']).document(diagnosis_id).get()
            if not diagnosis_doc.exists:
                return None

            diagnosis_data = diagnosis_doc.to_dict()

            # Paciente
            patient_doc = self.db.collection(self.collections['patients']).document(
                diagnosis_data['patient_id']
            ).get()
            patient_data = patient_doc.to_dict()

            # Veterinario
            vet_doc = self.db.collection(self.collections['veterinarians']).document(
                diagnosis_data['veterinarian_id']
            ).get()
            vet_data = vet_doc.to_dict()

            # Estudios
            studies_query = self.db.collection(self.collections['studies']).where(
                'diagnosis_id', '==', diagnosis_id
            ).get()

            estudios = []
            for study_doc in studies_query:
                study_data = study_doc.to_dict()
                study_id = study_doc.id

                # Mediciones
                measurements_query = self.db.collection(self.collections['measurements']).where(
                    'study_id', '==', study_id
                ).get()
                mediciones = [
                    MeasurementResponse(
                        id=doc.id,
                        tipo_medicion=md['tipo_medicion'],
                        valor=md['valor'],
                        organo=md['organo'],
                        unidad=md.get('unidad')
                    )
                    for doc in measurements_query
                    for md in [doc.to_dict()]
                ]

                # Observaciones
                observations_query = self.db.collection(self.collections['observations']).where(
                    'study_id', '==', study_id
                ).get()
                observaciones = [
                    ObservationResponse(
                        id=doc.id,
                        observacion=od['observacion'],
                        organo=od['organo']
                    )
                    for doc in observations_query
                    for od in [doc.to_dict()]
                ]

                estudios.append(
                    StudyResponse(
                        id=study_id,
                        tipo_estudio=study_data['tipo_estudio'],
                        mediciones=mediciones,
                        observaciones=observaciones
                    )
                )

            fecha = diagnosis_data.get('fecha')
            if isinstance(fecha, datetime):
                fecha = fecha.date()
            elif isinstance(fecha, str):
                fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

            return DiagnosisResponse(
                id=diagnosis_id,
                antecedentes=diagnosis_data.get('antecedentes'),
                diagnostico=diagnosis_data.get('diagnostico'),
                fecha=fecha,
                img_folder=diagnosis_data.get('img_folder'),
                paciente=PatientResponse(
                    id=diagnosis_data['patient_id'],
                    nombre=patient_data['nombre'],
                    tutor=patient_data['tutor'],
                    edad=str(patient_data['edad']),
                    raza=patient_data.get('raza')
                ),
                veterinario=VeterinarianResponse(
                    id=diagnosis_data['veterinarian_id'],
                    nombre=vet_data['nombre'],
                    apellido=vet_data['apellido'],
                    matricula=vet_data.get('matricula')
                ),
                estudios=estudios
            )

        except Exception as e:
            raise e

    async def get_all_diagnoses(self) -> List[SidebarDiagnosisItem]:
        try:
            diagnoses_query = self.db.collection(self.collections['diagnoses']).get()
            sidebar_items = []

            for doc in diagnoses_query:
                diagnosis_data = doc.to_dict()
                patient_doc = self.db.collection(self.collections['patients']).document(
                    diagnosis_data['patient_id']
                ).get()

                if patient_doc.exists:
                    patient_data = patient_doc.to_dict()

                    fecha = diagnosis_data.get('fecha')
                    if isinstance(fecha, datetime):
                        fecha = fecha.date()
                    elif isinstance(fecha, str):
                        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

                    sidebar_items.append(
                        SidebarDiagnosisItem(
                            id=str(doc.id),
                            nombre=patient_data.get('nombre', ''),
                            tutor=patient_data.get('tutor', ''),
                            edad=patient_data.get('edad', ''),
                            raza=patient_data.get('raza', None),
                            fecha=fecha
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
                    nombre=data['nombre'],
                    tutor=data['tutor'],
                    edad=str(data['edad']),
                    raza=data.get('raza')
                )
                for doc in patients_query
                for data in [doc.to_dict()]
            ]
        except Exception as e:
            raise e

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

    async def delete_all_data(self) -> bool:
            """Elimina todos los documentos de Firestore manteniendo las colecciones"""
            try:
                batch = self.db.batch()
                
                # Eliminar todos los documentos de cada colección
                collections_to_clear = [
                    self.collections['observations'],
                    self.collections['measurements'], 
                    self.collections['studies'],
                    self.collections['diagnoses'],
                    self.collections['patients'],
                    self.collections['veterinarians']
                ]
                
                deleted_count = 0
                for collection_name in collections_to_clear:
                    docs = self.db.collection(collection_name).stream()
                    for doc in docs:
                        batch.delete(doc.reference)
                        deleted_count += 1
                        
                        # Firestore limita los batches a 500 operaciones
                        if deleted_count % 450 == 0:
                            batch.commit()
                            batch = self.db.batch()
                
                # Commit final
                if deleted_count % 450 != 0:
                    batch.commit()
                    
                return True
                
            except Exception as e:
                logger.error(f"Error eliminando datos Firestore: {str(e)}")
                raise e