from typing import List, Optional, Dict, Any
from sqlalchemy.orm import sessionmaker, joinedload
from models.entities import *
from models.schemas import DiagnosisCreate, DiagnosisResponse, PatientResponse, VeterinarianResponse, StudyResponse, MeasurementResponse, ObservationResponse, SidebarDiagnosisItem
from repositories.base_repository import BaseRepository
from database.sql_connection import get_sql_session
from datetime import datetime


class SQLRepository(BaseRepository):
    def __init__(self):
        self.session_factory = get_sql_session()
    
    async def create_diagnosis(self, diagnosis_data: DiagnosisCreate) -> str:
        print("=== create_diagnosis START ===", diagnosis_data.paciente.nombre)
        session = self.session_factory()
        try:
            # Crear paciente
            paciente = self._create_patient_entity(diagnosis_data.paciente, session)
            
            # Crear veterinario
            veterinario = self._create_veterinarian_entity(diagnosis_data.veterinario, session)
            
            diagnostico = diagnosis_data.informe.diagnostico
            if isinstance(diagnostico, list): # En caso de que el LLM quiera darnos una lista
                diagnostico = "; ".join(diagnostico)
            
            fecha_str = diagnosis_data.informe.fecha
            fecha_obj = None
            if fecha_str:
                fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y").date()
            # Crear informe
            informe = Informes(
                antecedentes=diagnosis_data.informe.antecedentes,
                diagnostico=diagnostico,
                img_folder=diagnosis_data.informe.img_folder,
                fecha=fecha_obj,
                fk_paciente=paciente.id,
                fk_referido=veterinario.id
            )
            session.add(informe)
            session.commit()
            
            # Crear estudios
            for estudio_data in diagnosis_data.informe.estudios:
                self._create_study_entity(estudio_data, informe.id, session)
            
            session.commit()
            return str(informe.id)
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    async def get_diagnosis(self, diagnosis_id: str) -> Optional[DiagnosisResponse]:
        session = self.session_factory()
        try:
            informe = session.query(Informes).options(
                joinedload(Informes.paciente),
                joinedload(Informes.veterinario),
                joinedload(Informes.estudios).joinedload(Estudios.mediciones),
                joinedload(Informes.estudios).joinedload(Estudios.observaciones),
                joinedload(Informes.estudios).joinedload(Estudios.tipo_estudio)
            ).filter(Informes.id == int(diagnosis_id)).first()
            
            if not informe:
                return None
                
            return self._map_to_diagnosis_response(informe)
            
        except Exception as e:
            raise e
        finally:
            session.close()

    async def get_all_diagnoses(self) -> List[SidebarDiagnosisItem]:
        session = self.session_factory()
        try:
            results = session.query(
                Informes.id,
                Pacientes.nombre,
                Pacientes.tutor, 
                Pacientes.edad,
                Pacientes.raza,
                Informes.fecha
            ).join(Pacientes, Informes.fk_paciente == Pacientes.id).all()
            
            return [
                SidebarDiagnosisItem(
                    id=str(row.id),
                    nombre=row.nombre,
                    tutor=row.tutor,
                    edad=row.edad,
                    raza=row.raza,
                    fecha=row.fecha
                )
                for row in results
            ]
        finally:
            session.close()


    async def get_patients(self) -> List[PatientResponse]:
        session = self.session_factory()
        try:
            pacientes = session.query(Pacientes).all()
            return [
                PatientResponse(
                    id=str(p.id),
                    nombre=p.nombre,
                    tutor=p.tutor,
                    edad=str(p.edad),
                    raza=p.raza
                ) for p in pacientes
            ]
        finally:
            session.close()
    
    def _create_patient_entity(self, patient_data, session):

        existing = session.query(Pacientes).filter_by(
            nombre=patient_data.nombre,
            tutor=patient_data.tutor,
            edad=patient_data.edad,
            raza=patient_data.raza
        ).first()
        if not existing:
            paciente = Pacientes(
                nombre=patient_data.nombre,
                tutor=patient_data.tutor,
                edad=patient_data.edad,
                raza=getattr(patient_data, 'raza', None)
            )
            session.add(paciente)
            session.commit()
            return paciente
        return existing
    
    def _create_veterinarian_entity(self, vet_data, session):
        existing = session.query(Veterinarios).filter_by(
            nombre=vet_data.nombre,
            apellido=vet_data.apellido
        ).first()
        
        if not existing:
            veterinario = Veterinarios(
                nombre=vet_data.nombre,
                apellido=vet_data.apellido,
                matricula=vet_data.matricula
            )
            session.add(veterinario)
            session.commit()
            return veterinario
        return existing
    
    def _create_study_entity(self, study_data, informe_id, session):
        # Crear tipo de estudio si no existe
        tipo_estudio = session.query(Tipos_Estudios).filter_by(
            tipo_estudio=study_data.tipo_estudio
        ).first()
        
        if not tipo_estudio:
            tipo_estudio = Tipos_Estudios(tipo_estudio=study_data.tipo_estudio)
            session.add(tipo_estudio)
            session.commit()
        
        # Crear estudio
        estudio = Estudios(
            fk_informe=informe_id,
            fk_tipos_estudios=tipo_estudio.id
        )
        session.add(estudio)
        session.commit()
        
        # Crear mediciones y observaciones
        for medicion in study_data.mediciones:
            self._create_measurement_entity(medicion, estudio.id, session)
        
        for obs in study_data.observaciones:
            self._create_observation_entity(obs, estudio.id, session)
        
        session.commit()
    
    def _create_measurement_entity(self, measurement_data, estudio_id, session):
        # Crear órgano si no existe
        organo = session.query(Organos).filter_by(nombre=measurement_data.organo).first()
        if not organo:
            organo = Organos(nombre=measurement_data.organo)
            session.add(organo)
            session.commit()
        
        # Crear unidad si no existe
        unidad = None
        if measurement_data.unidad:
            unidad = session.query(Unidades).filter_by(unidad=measurement_data.unidad).first()
            if not unidad:
                unidad = Unidades(unidad=measurement_data.unidad)
                session.add(unidad)
                session.commit()
        
        # Crear medida si no existe
        medida = session.query(Medidas).filter_by(medida=measurement_data.tipo_medicion).first()
        if not medida:
            medida = Medidas(medida=measurement_data.tipo_medicion)
            session.add(medida)
            session.commit()
        
        medicion = Mediciones(
            tipo_medicion=measurement_data.tipo_medicion,
            valor=str(measurement_data.valor) if measurement_data.valor is not None else None,
            fk_organo=organo.id,
            fk_medida=medida.id,
            fk_unidad=unidad.id if unidad else None,
            fk_estudio=estudio_id
        )
        session.add(medicion)
    
    def _create_observation_entity(self, obs_data, estudio_id, session):
        # Crear órgano si no existe
        organo = session.query(Organos).filter_by(nombre=obs_data.organo).first()
        if not organo:
            organo = Organos(nombre=obs_data.organo)
            session.add(organo)
            session.commit()
        
        observacion = Observaciones(
            observacion=obs_data.observacion,
            fk_organo=organo.id,
            fk_estudio=estudio_id
        )
        session.add(observacion)
    
    def _map_to_diagnosis_response(self, informe) -> DiagnosisResponse:
        return DiagnosisResponse(
            id=str(informe.id),
            antecedentes=informe.antecedentes,
            diagnostico=informe.diagnostico,
            fecha=informe.fecha,
            img_folder=informe.img_folder,
            paciente=PatientResponse(
                id=str(informe.paciente.id),
                nombre=informe.paciente.nombre,
                tutor=informe.paciente.tutor,
                edad=str(informe.paciente.edad),
                raza=informe.paciente.raza
            ),
            veterinario=VeterinarianResponse(
                id=str(informe.veterinario.id),
                nombre=informe.veterinario.nombre,
                apellido=informe.veterinario.apellido,
                matricula=informe.veterinario.matricula
            ),
            estudios=[
                StudyResponse(
                    id=str(estudio.id),
                    tipo_estudio=estudio.tipo_estudio.tipo_estudio,
                    mediciones=[
                        MeasurementResponse(
                            id=str(med.id),
                            tipo_medicion=med.tipo_medicion,
                            valor=med.valor,
                            organo=med.organo.nombre,
                            unidad=med.unidad.unidad if med.unidad else None
                        ) for med in estudio.mediciones
                    ],
                    observaciones=[
                        ObservationResponse(
                            id=str(obs.id),
                            observacion=obs.observacion,
                            organo=obs.organo.nombre
                        ) for obs in estudio.observaciones
                    ]
                ) for estudio in informe.estudios
            ]
        )

    # Implementar métodos restantes del BaseRepository
    async def create_patient(self, patient_data: Dict[str, Any]) -> str:
        # Implementación similar
        pass
    
    async def get_veterinarian(self, vet_id: str) -> Optional[Dict[str, Any]]:
        # Implementación similar
        pass
    
    async def create_veterinarian(self, vet_data: Dict[str, Any]) -> str:
        # Implementación similar
        pass