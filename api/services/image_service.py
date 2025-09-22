import os
import fitz
from typing import List
from fastapi import HTTPException
from models.schemas import ImageExtractResponse, ImagesResponse
from app.config import settings
import logging
from io import BytesIO
from utils.cnn_classifier import load_model, cnn_inference
from PIL import Image
import re

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        self.images_directory = settings.images_directory
        os.makedirs(self.images_directory, exist_ok=True)
    
    async def extract_images_from_pdf(self, filename: str, file_content: bytes) -> ImageExtractResponse:
        """Extraer imágenes de un archivo PDF"""
        if not filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF.")
        
        try:
            # Normalización del nombre
            #normalized_name = self.normalize_filename(filename)
            # Crear carpeta específica para este PDF
            #folder_name = filename.replace(".pdf", "_images")
            next_number = self.get_next_folder_number()
            folder_name = f'{next_number}_images'
            output_folder = os.path.join(self.images_directory, folder_name)
            os.makedirs(output_folder, exist_ok=True)
            
            # Guardar archivo PDF temporalmente
            pdf_path = os.path.join(output_folder, filename)
            with open(pdf_path, "wb") as f:
                f.write(file_content)
            
            # Extraer imágenes
            total_images = await self._extract_images(pdf_path, output_folder)
            
            # Eliminar PDF temporal
            os.remove(pdf_path)
            
            logger.info(f"Extraídas {total_images} imágenes de {filename}")
            
            return ImageExtractResponse(
                status="success",
                message=f"Extraídas {total_images} imágenes exitosamente",
                folder=folder_name
            )
            
        except Exception as e:
            logger.error(f"Error extrayendo imágenes de {filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error procesando PDF: {str(e)}")
    
    async def get_images_from_folder(self, folder_name: str) -> ImagesResponse:
        """Obtener lista de imágenes de una carpeta"""
        folder_path = os.path.join(self.images_directory, folder_name)
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise HTTPException(status_code=400, detail="Carpeta no válida.")
        
        try:
            # Filtrar solo archivos de imagen
            image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
            images = [
                f'/extracted_images/{folder_name}/{f}'
                for f in os.listdir(folder_path)
                if f.lower().endswith(image_extensions)
            ]
            
            logger.info(f"Encontradas {len(images)} imágenes en {folder_name}")
            
            return ImagesResponse(
                status="success",
                images=images
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo imágenes de {folder_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error obteniendo imágenes: {str(e)}")
    
    async def _extract_images(self, pdf_path: str, output_folder: str) -> int:
        """Extraer imágenes del PDF usando PyMuPDF"""
        total_images = 0
        model, device = load_model()
        with fitz.open(pdf_path) as pdf_document:
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images(full=True)
                
                if not image_list:
                    continue
                
                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_extension = base_image["ext"]
                    
                    img = Image.open(BytesIO(image_bytes)).convert("RGB")
                    pred = cnn_inference(img, model, device)

                    if pred == 1:
                        image_filename = os.path.join(
                            output_folder,
                            f"page_{page_num + 1}_image_{img_index + 1}.{image_extension}"
                        )
                        img.save(image_filename)
                        total_images += 1
        
        return total_images
    def get_next_folder_number(self) -> int:
        """Obtener el próximo número secuencial para carpeta de imágenes"""

        if not os.path.exists(self.images_directory):
            return 1
        
        # Buscar todas las carpetas que siguen el patrón numérico
        folder_pattern = re.compile(r'^(\d+)_images$')
        numbers = []
        
        for item in os.listdir(self.images_directory):
            if os.path.isdir(os.path.join(self.images_directory, item)):
                match = folder_pattern.match(item)
                if match:
                    numbers.append(int(match.group(1)))
        
        if not numbers:
            return 1
        
        return max(numbers) + 1