from google.cloud import firestore
from google.oauth2 import service_account
from app.config import settings
from monitoring.metrics import metrics_collector
import logging
import os

logger = logging.getLogger(__name__)

class FirestoreConnection:
    _instance = None
    _client = None
    _collections = {
        'patients': 'pacientes',
        'veterinarians': 'veterinarios',
        'diagnoses': 'diagnosticos',
        'studies': 'estudios',
        'measurements': 'mediciones',
        'observations': 'observaciones',
        'organs': 'organos',
        'units': 'unidades',
        'measures': 'medidas',
        'study_types': 'tipos_estudios'
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirestoreConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._create_client()

    def _create_client(self):
        """Crear cliente de Firestore compatible con Cloud Run y local"""
        try:
            if not settings.firestore_project_id:
                raise ValueError("FIRESTORE_PROJECT_ID no configurado")

            # 1️⃣ Si hay JSON local y existe, usarlo (desarrollo local)
            if settings.firestore_credentials_path and os.path.exists(settings.firestore_credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    settings.firestore_credentials_path
                )
                self._client = firestore.Client(
                    project=settings.firestore_project_id,
                    credentials=credentials
                )
                logger.info("Cliente Firestore creado con credenciales de archivo (local)")
            else:
                # 2️⃣ Si no hay JSON, usar Application Default Credentials (Cloud Run)
                self._client = firestore.Client(project=settings.firestore_project_id)
                logger.info("Cliente Firestore creado con credenciales por defecto (ADC / Cloud Run)")

            # Probar conexión
            self._test_connection()
            metrics_collector.update_database_status("firestore", True)

        except Exception as e:
            logger.error(f"Error creando cliente Firestore: {str(e)}")
            metrics_collector.update_database_status("firestore", False)
            raise e

    def _test_connection(self):
        """Probar conexión a Firestore con un documento temporal"""
        try:
            test_ref = self._client.collection('_connection_test').document('test')
            test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP}, merge=True)
            doc = test_ref.get()
            if doc.exists:
                logger.info("Conexión Firestore verificada exitosamente")
                test_ref.delete()
            else:
                raise Exception("No se pudo verificar la escritura en Firestore")
        except Exception as e:
            logger.error(f"Error verificando conexión Firestore: {str(e)}")
            raise e

    def get_client(self) -> firestore.Client:
        if self._client is None:
            self._create_client()
        return self._client

    def get_collection_name(self, collection_key: str) -> str:
        return self._collections.get(collection_key, collection_key)

    def get_collection(self, collection_key: str):
        collection_name = self.get_collection_name(collection_key)
        return self._client.collection(collection_name)

    def test_connection(self) -> bool:
        try:
            self._test_connection()
            metrics_collector.update_database_status("firestore", True)
            return True
        except Exception as e:
            metrics_collector.update_database_status("firestore", False)
            logger.error(f"Error en conexión Firestore: {str(e)}")
            return False

# Instancia global
firestore_connection = FirestoreConnection()

def get_firestore_client() -> firestore.Client:
    return firestore_connection.get_client()

def get_firestore_collection(collection_key: str):
    return firestore_connection.get_collection(collection_key)
