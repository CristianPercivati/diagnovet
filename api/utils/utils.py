import re 
import os

def normalize_filename(self, filename: str) -> str:
    """
    Normaliza un nombre de archivo para eliminar caracteres especiales, 
    espacios y convertirlo a minúsculas.
    """
    # Eliminar la extensión temporalmente para normalizar el nombre base
    name, ext = os.path.splitext(filename)
    
    # Normalizar caracteres Unicode (convertir á -> a, é -> e, etc.)
    normalized = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    
    # Reemplazar espacios y caracteres no alfanuméricos con guiones bajos
    normalized = re.sub(r'[^\w\s-]', '', normalized)  # Eliminar caracteres especiales
    normalized = re.sub(r'[-\s]+', '_', normalized)   # Reemplazar espacios y guiones con _
    
    # Convertir a minúsculas y agregar la extensión
    return normalized.lower() + ext.lower()

