from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings
from models.entities import Base
from monitoring.metrics import metrics_collector
import logging


logger = logging.getLogger(__name__)

class SQLConnection:
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SQLConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._create_engine()
            self._create_session_factory()
            self._create_tables()
    
    def _create_engine(self):
        """Crear engine de SQLAlchemy con configuración optimizada"""
        try:
            # Construir connection string
            connection_string = (
            f"DRIVER={settings.sql_driver};"
            f"SERVER={settings.sql_server};"
            f"DATABASE={settings.sql_database};"
            f"UID={settings.sql_user};"
            f"PWD={settings.sql_password};"
            f"Encrypt=yes;"  # Necesario para Cloud SQL
            f"TrustServerCertificate=yes;"  # Necesario para Cloud SQL
            f"Connection Timeout=30;"  # Timeout más largo
        )
            
            # Crear engine con pool de conexiones
            self._engine = create_engine(
                f"mssql+pyodbc:///?odbc_connect={connection_string}",
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verificar conexiones antes de usar
                pool_recycle=3600,   # Reciclar conexiones cada hora
                echo=False  # Cambiar a True para debug SQL
            )
            
            # Event listeners para métricas
            self._setup_metrics_listeners()
            
            logger.info("SQL Server engine creado exitosamente")
            metrics_collector.update_database_status("sql_server", True)
            
        except Exception as e:
            logger.error(f"Error creando SQL Server engine: {str(e)}")
            metrics_collector.update_database_status("sql_server", False)
            raise e
    
    def _create_session_factory(self):
        """Crear factory de sesiones"""
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )
        logger.info("Session factory creada exitosamente")
    
    def _create_tables(self):
        """Crear tablas si no existen"""
        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("Tablas de base de datos verificadas/creadas")
        except Exception as e:
            logger.error(f"Error creando tablas: {str(e)}")
            raise e
    
    def _setup_metrics_listeners(self):
        """Configurar listeners para métricas de base de datos"""
        
        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            logger.debug("Nueva conexión SQL Server establecida")
            metrics_collector.update_database_status("sql_server", True)
        
        @event.listens_for(self._engine, "engine_connect")
        def receive_engine_connect(conn, branch):
            logger.debug("Engine connect event")
        
        @event.listens_for(self._engine, "close")
        def receive_close(dbapi_connection, connection_record):
            logger.debug("Conexión SQL Server cerrada")
    
    def get_engine(self):
        """Obtener engine de SQLAlchemy"""
        return self._engine
    
    def get_session_factory(self):
        """Obtener factory de sesiones"""
        return self._session_factory
    
    def test_connection(self) -> bool:
        """Probar conexión a la base de datos"""
        try:
            with self._engine.connect() as conn:
                conn.execute("SELECT 1")
            
            metrics_collector.update_database_status("sql_server", True)
            logger.info("Conexión SQL Server OK")
            return True
            
        except Exception as e:
            metrics_collector.update_database_status("sql_server", False)
            logger.error(f"Error en conexión SQL Server: {str(e)}")
            return False
    
    def close_connections(self):
        """Cerrar todas las conexiones"""
        if self._engine:
            self._engine.dispose()
            logger.info("Conexiones SQL Server cerradas")

# Instancia global
sql_connection = SQLConnection()

def get_sql_engine():
    """Obtener engine SQL Server"""
    return sql_connection.get_engine()

def get_sql_session():
    """Obtener factory de sesiones SQL Server"""
    return sql_connection.get_session_factory()

def test_sql_connection() -> bool:
    """Probar conexión SQL Server"""
    return sql_connection.test_connection()

# Context manager para sesiones
class SQLSession:
    def __init__(self):
        self.session = get_sql_session()()
    
    def __enter__(self):
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()