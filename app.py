from datetime import datetime
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import clases
import conexion
import os
import shutil

# Configuración de AWS S3
BUCKET_NAME = "mi-app-web-bucket"

# Cliente de S3
session = boto3.Session(profile_name="default")
s3_client = boto3.client("s3", region_name="us-east-1")

# Inicializar FastAPI
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Carpeta local
UPLOAD_DIRECTORY = "documentos"
UPLOAD_FOLDER = Path("test")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador global de errores
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"Error interno: {exc}")
    raise HTTPException(status_code=500, detail="Error interno del servidor")

# Rutas del API
@api_router.get("/")
def read_root():
    return {"welcome": "Welcome to my api"}

@api_router.get("/usuarios")
def read_usuarios():
    registros = conexion.devolverRegistros("usuarios")
    usuarios = [clases.Usuario(
        usu_id=registro[0],
        usu_correo=registro[1],
        usu_nombre=registro[3],
        usu_codigo=registro[4]
    ) for registro in registros]
    return clases.Respuesta(success=True, message="All ok", data=usuarios)

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Sube un archivo al bucket S3."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos de imagen")

    try:
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file.filename,
            ExtraArgs={"ContentType": file.content_type},
        )
        return {"message": f"Archivo {file.filename} subido correctamente a S3"}
    except (BotoCoreError, ClientError) as e:
        print(f"Error subiendo archivo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al subir el archivo")

@api_router.get("/download-all")
async def download_all_files():
    """Descarga todos los archivos del bucket S3 a una carpeta local."""
    folder_path = Path("C:/laragon/www/servicioImpreCentro/documents")
    folder_path.mkdir(exist_ok=True)

    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        objects = response.get("Contents", [])
        for obj in objects:
            key = obj["Key"]
            local_file_path = folder_path / key
            s3_client.download_file(BUCKET_NAME, key, str(local_file_path))

        return {"message": "Archivos descargados correctamente", "files": [obj["Key"] for obj in objects]}
    except Exception as e:
        print("Error:", str(e))
        raise HTTPException(status_code=500, detail="Error al descargar archivos")

@api_router.get("/static-files/{file_name}")
async def get_static_file(file_name: str):
    """Sirve un archivo descargado del bucket S3."""
    file_path = Path("C:/laragon/www/servicioImpreCentro/documents") / file_name  # Asegurar consistencia en la ruta
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)

@api_router.put("/rename")
async def rename_file(request: BaseModel):
    """Renombra un archivo en el bucket S3."""
    old_name = request.old_name
    new_name = request.new_name
    if not new_name.lower().endswith(".jpg"):
        raise HTTPException(status_code=400, detail="El archivo debe tener extensión .jpg")
    try:
        s3_client.copy_object(
            Bucket=BUCKET_NAME,
            CopySource={"Bucket": BUCKET_NAME, "Key": old_name},
            Key=new_name,
        )
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=old_name)
        return {"message": f"Archivo {old_name} renombrado a {new_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al renombrar el archivo: {str(e)}")

# Incluir router en la aplicación principal
app.include_router(api_router)
