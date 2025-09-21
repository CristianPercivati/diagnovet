from google.cloud import firestore
from google.oauth2 import service_account
from google.cloud.exceptions import GoogleCloudError
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
        """Crear cliente de Firestore"""
        try:
            if not settings.firestore_project_id:
                raise ValueError("FIRESTORE_PROJECT_ID no configurado")
            
            # Configurar credenciales si están especificadas
            if settings.firestore_credentials_path and os.path.exists(settings.firestore_credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    settings.firestore_credentials_path
                )
                self._client = firestore.Client(
                    project=settings.firestore_project_id,
                    credentials=credentials
                )
                logger.info("Cliente Firestore creado con credenciales de archivo")
            else:
                # Usar credenciales por defecto (ADC - Application Default Credentials)
                self._client = firestore.Client(project=settings.firestore_project_id)
                logger.info("Cliente Firestore creado con credenciales por defecto")
            
            # Probar conexión
            self._test_connection()
            metrics_collector.update_database_status("firestore", True)
            
        except Exception as e:
            logger.error(f"Error creando cliente Firestore: {str(e)}")
            metrics_collector.update_database_status("firestore", False)
            raise e
    
    def _test_connection(self):
        """Probar conexión a Firestore"""
        try:
            # Intentar una operación simple para verificar la conexión
            test_ref = self._client.collection('_connection_test').document('test')
            test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP}, merge=True)
            
            # Leer el documento para confirmar
            doc = test_ref.get()
            if doc.exists:
                logger.info("Conexión Firestore verificada exitosamente")
                # Limpiar documento de prueba
                test_ref.delete()
            else:
                raise Exception("No se pudo verificar la escritura en Firestore")
                
        except Exception as e:
            logger.error(f"Error verificando conexión Firestore: {str(e)}")
            raise e
    
    def get_client(self) -> firestore.Client:
        """Obtener cliente de Firestore"""
        if self._client is None:
            self._create_client()
        return self._client
    
    def get_collection_name(self, collection_key: str) -> str:
        """Obtener nombre de colección por clave"""
        return self._collections.get(collection_key, collection_key)
    
    def get_collection(self, collection_key: str):
        """Obtener referencia a colección"""
        collection_name = self.get_collection_name(collection_key)
        return self._client.collection(collection_name)
    
    def test_connection(self) -> bool:
        """Probar conexión a Firestore"""
        try:
            self._test_connection()
            metrics_collector.update_database_status("firestore", True)
            return True
        except Exception as e:
            metrics_collector.update_database_status("firestore", False)
            logger.error(f"Error en conexión Firestore: {str(e)}")
            return False
    
    def initialize_collections(self):
        """Inicializar colecciones con documentos de configuración"""
        try:
            # Crear documento de configuración en cada colección
            for key, collection_name in self._collections.items():
                config_ref = self._client.collection(collection_name).document('_config')
                config_ref.set({
                    'collection_type': key,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'version': '1.0'
                }, merge=True)
            
            logger.info("Colecciones Firestore inicializadas")
            
        except Exception as e:
            logger.error(f"Error inicializando colecciones: {str(e)}")
            raise e
    
    def batch_writer(self):
        """Obtener batch writer para operaciones en lote"""
        return self._client.batch()
    
    def transaction(self):
        """Obtener transacción"""
        return self._client.transaction()

# Instancia global
firestore_connection = FirestoreConnection()

def get_firestore_client() -> firestore.Client:
    """Obtener cliente Firestore"""
    return firestore_connection.get_client()

def get_firestore_collection(collection_key: str):
    """Obtener colección Firestore"""
    return firestore_connection.get_collection(collection_key)

def test_firestore_connection() -> bool:
    """Probar conexión Firestore"""
    return firestore_connection.test_connection()

# Context manager para transacciones
class FirestoreTransaction:
    def __init__(self):
        self.client = get_firestore_client()
        self.transaction = None
    
    def __enter__(self):
        self.transaction = self.client.transaction()
        return self.transaction
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Las transacciones en Firestore se comitean automáticamente
        # si no hay excepciones
        pass

# Context manager para batch operations
class FirestoreBatch:
    def __init__(self):
        self.client = get_firestore_client()
        self.batch = None
    
    def __enter__(self):
        self.batch = self.client.batch()
        return self.batch
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.batch.commit()
        # Si hay excepción, no se comitea el batch