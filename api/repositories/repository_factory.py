from repositories.base_repository import BaseRepository
from repositories.sql_repository import SQLRepository
from repositories.firestore_repository import FirestoreRepository
from app.config import settings, DatabaseType
from monitoring.metrics import metrics_collector
import logging

logger = logging.getLogger(__name__)

class RepositoryFactory:
    _instance = None
    _repository = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RepositoryFactory, cls).__new__(cls)
        return cls._instance
    
    def get_repository(self) -> BaseRepository:
        """Obtener el repositorio configurado (Singleton pattern)"""
        if self._repository is None:
            self._repository = self._create_repository()
        return self._repository
    
    def _create_repository(self) -> BaseRepository:
        """Factory method para crear el repositorio según configuración"""
        try:
            if settings.database_type == DatabaseType.SQL_SERVER:
                logger.info("Inicializando repositorio SQL Server")
                repo = SQLRepository()
                metrics_collector.update_database_status("sql_server", True)
                return repo
            
            elif settings.database_type == DatabaseType.FIRESTORE:
                logger.info("Inicializando repositorio Firestore")
                if not settings.firestore_project_id:
                    raise ValueError("FIRESTORE_PROJECT_ID no configurado")
                
                repo = FirestoreRepository(settings.firestore_project_id)
                metrics_collector.update_database_status("firestore", True)
                return repo
            
            else:
                raise ValueError(f"Tipo de base de datos no soportado: {settings.database_type}")
                
        except Exception as e:
            logger.error(f"Error creando repositorio: {str(e)}")
            # Marcar base de datos como down en métricas
            metrics_collector.update_database_status(settings.database_type.value, False)
            raise e

# Instancia global del factory
repository_factory = RepositoryFactory()