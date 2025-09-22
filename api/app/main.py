from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
import json
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from services.diagnosis_service import DiagnosisService
from services.image_service import ImageService
from repositories.repository_factory import repository_factory
from models.schemas import DiagnosisCreate, DiagnosisResponse, PatientResponse, SidebarDiagnosisItem
from monitoring.metrics import metrics_collector
from app.config import settings

import logging
from typing import List

from urllib.parse import unquote
import unicodedata


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="DiagnoVet API",
    description="API para gestión de diagnósticos veterinarios",
    version="2.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/extracted_images", StaticFiles(directory=settings.images_directory), name="extracted_images")

# Dependency injection
def get_diagnosis_service() -> DiagnosisService:
    repository = repository_factory.get_repository()
    return DiagnosisService(repository)

def get_image_service() -> ImageService:
    return ImageService()

# Rutas de la API
@app.get("/")
async def root():
    return {
        "message": "DiagnoVet API v2.0",
        "database": settings.database_type.value,
        "status": "active"
    }

@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    if request.url.path == "/diagnosis" and request.method == "POST":
        try:
            # Leer el cuerpo de la solicitud
            body = await request.body()
            body_str = body.decode()
            logger.info(f"📨 RAW REQUEST BODY: {body_str}")
            
            # Intentar parsear JSON
            try:
                json_data = json.loads(body_str)
                logger.info(f"📋 PARSED JSON: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ INVALID JSON: {e}")
                
        except Exception as e:
            logger.error(f"❌ ERROR reading body: {e}")
    
    response = await call_next(request)
    return response

@app.post("/diagnosis", response_model=dict)
async def create_diagnosis(
    diagnosis_data: DiagnosisCreate,
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    """Crear un nuevo diagnóstico"""
    try:
        logger.info(f"Datos recibidos: {diagnosis_data.dict()}")
        diagnosis_id = await service.create_diagnosis(diagnosis_data)
        return {
            "status": "success",
            "diagnosis_id": diagnosis_id,
            "message": "Diagnóstico creado exitosamente"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creando diagnóstico: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/diagnosis/{diagnosis_id}", response_model=DiagnosisResponse)
async def get_diagnosis(
    diagnosis_id: str,
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    """Obtener un diagnóstico por ID"""
    diagnosis = await service.get_diagnosis(diagnosis_id)
    
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
    
    return diagnosis

@app.get("/patients", response_model=List[PatientResponse])
async def get_patients(
    service: DiagnosisService = Depends(get_diagnosis_service)
):
    """Obtener todos los pacientes"""
    return await service.get_patients()

@app.post("/images/extract")
async def extract_images(
    file: UploadFile = File(...),
    service: ImageService = Depends(get_image_service)
):
    """Extraer imágenes de un archivo PDF"""
    file_content = await file.read()
    return await service.extract_images_from_pdf(file.filename, file_content)

@app.get("/images/{folder_name}")
async def get_images(
    folder_name: str,
    service: ImageService = Depends(get_image_service)
):
    """Obtener imágenes de una carpeta"""
    return await service.get_images_from_folder(folder_name)

# Endpoint de métricas para Prometheus
@app.get("/metrics")
async def get_metrics():
    """Endpoint de métricas para Prometheus"""
    return Response(
        content=metrics_collector.get_metrics(),
        media_type="text/plain"
    )


@app.get("/all_diagnoses", response_model=None)
async def get_sidebar_diagnoses(service: DiagnosisService = Depends(get_diagnosis_service)):
    return await service.get_all_diagnoses()


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexión a la base de datos
        repository = repository_factory.get_repository()
        
        return {
            "status": "healthy",
            "database": settings.database_type.value,
            "timestamp": "2025-09-19T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/delete-all")
async def delete_all_data(
    service: DiagnosisService = Depends(get_diagnosis_service),
):
    """
    Elimina todos los datos del sistema manteniendo las estructuras.
    
    ⚠️ **ADVERTENCIA**: Esta operación es irreversible y elimina todos los datos.
    Solo para uso en desarrollo/testing.
    """
    try:
        success = await service.delete_all_data()
        
        if success:
            return {"message": "Todos los datos han sido eliminados exitosamente"}
        else:
            raise HTTPException(
                status_code=500, 
                detail="Error al eliminar los datos"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando datos: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)