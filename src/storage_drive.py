import os
from google.cloud import storage
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

def upload_photo(file_path, file_name):
    """
    Sube un archivo local al bucket de Google Cloud Storage,
    lo hace público y devuelve la URL para visualizarlo.
    """
    if not GCS_BUCKET_NAME:
        raise ValueError("No se encontró GCS_BUCKET_NAME en el archivo .env")
    
    # Autenticar usando el mismo JSON de credenciales
    creds = Credentials.from_service_account_file('credentials.json')
    client = storage.Client(credentials=creds, project=creds.project_id)
    
    # Obtener el bucket
    bucket = client.bucket(GCS_BUCKET_NAME)
    
    # Crear el objeto (blob)
    blob = bucket.blob(file_name)
    
    # Subir el archivo
    blob.upload_from_filename(file_path, content_type='image/jpeg')
    
    # Devolver la URL pública que Sheets podrá leer directamente
    return blob.public_url
