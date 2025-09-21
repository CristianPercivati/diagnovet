import os
from enum import Enum
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class DatabaseType(str, Enum):
    SQL_SERVER = "sql_server"
    FIRESTORE = "firestore"

class Settings(BaseSettings):
    # Database config
    database_type: DatabaseType = DatabaseType.SQL_SERVER
    
    # SQL Server config
    sql_server: str = os.getenv('SQL_ENGINE', 'localhost')
    sql_database: str = os.getenv('DB', 'diagnovet')
    sql_user: str = os.getenv('USER', 'sa')
    sql_driver: str = "ODBC Driver 17 for SQL Server"
    
    # Firestore config
    firestore_project_id: str = os.getenv('FIRESTORE_PROJECT_ID', '')
    firestore_credentials_path: str = os.getenv('FIRESTORE_CREDENTIALS', '')
    
    # API config
    base_url: str = "http://localhost:8000"
    images_directory: str = "./extracted_images"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 8001
    
    class Config:
        env_file = ".env"

settings = Settings()