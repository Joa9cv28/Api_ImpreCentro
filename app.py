from datetime import datetime
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import clases
import conexion
import os
import re
import jwt
import requests
from dotenv import load_dotenv


# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración de AWS
BUCKET_NAME = os.getenv("BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")

# Cliente de AWS
session = boto3.Session(profile_name="default")
s3_client = boto3.client("s3", region_name=AWS_REGION)
cognito_client = boto3.client("cognito-idp", region_name=AWS_REGION)
rekognition_client = boto3.client("rekognition", region_name=AWS_REGION)

# Inicializar FastAPI
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Carpeta local
UPLOAD_DIRECTORY = "documentos"
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")

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
    if not file.filename.lower().endswith(".gcode"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .gcode")

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
    folder_path = Path(UPLOAD_FOLDER)
    folder_path.mkdir(parents=True, exist_ok=True)  # Asegura que toda la ruta se crea

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
    file_path = Path(UPLOAD_FOLDER) / file_name  # Asegurar consistencia en la ruta
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

#############################################################################
# ----------------- Autenticación con Cognito y Rekognition -----------------
#############################################################################
class RegisterUser:
    def __init__(
        self,
        email: str = Form(...),
        full_name: str = Form(...),
        student_code: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...)
    ):
        self.email = email
        self.full_name = full_name
        self.student_code = student_code
        self.password = password
        self.confirm_password = confirm_password

@api_router.post("/register/")
def register_user(user: RegisterUser = Depends(), file: UploadFile = File(...)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")

    # Leer imagen y enviarla a Rekognition
    image_bytes = file.file.read()
    response = rekognition_client.detect_text(Image={'Bytes': image_bytes})
    detected_text = [item['DetectedText'].lower() for item in response['TextDetections']]

    # Extraer código de estudiante
    extracted_code = None
    detected_text_joined = " ".join(detected_text)
    match = re.findall(r"c[oó]digo[:\s]+(\d+)", detected_text_joined)
    if match:
        extracted_code = match[0]

    if extracted_code is None:
        for i, word in enumerate(detected_text):
            if "código" in word or "codigo" in word:
                if i + 1 < len(detected_text) and detected_text[i + 1].isdigit():
                    extracted_code = detected_text[i + 1]
                    break

    if extracted_code != user.student_code:
        raise HTTPException(status_code=400, detail="El código de estudiante no coincide con la credencial")

    # Verificar que pertenece a CUCEI
    if not any("cucei" in text for text in detected_text):
        raise HTTPException(status_code=400, detail="La credencial no pertenece a CUCEI")

    # Validar si el correo ya está registrado en Cognito
    try:
        existing_users = cognito_client.list_users(
            UserPoolId=USER_POOL_ID,
            Filter=f'email="{user.email}"'
        )
        if existing_users["Users"]:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al verificar el correo en Cognito")
    print(f"USER_POOL_ID: {USER_POOL_ID}, CLIENT_ID: {CLIENT_ID}") ############################################################# Debug de variables de entorno

    ########################################################################################################################################################## 
    ################################################################ Debug de objetos ########################################################################
    ##########################################################################################################################################################
    print(f"user.student_code: {user.student_code}, user.password: {user.password}, user.email: {user.email}, user.full_name: {user.full_name}")
    print(f"response: {response}")
    print(f"detected_text: {detected_text}")
    print(f"extracted_code: {extracted_code}")
    print(f"existing_users: {existing_users}")

    ####################################################################################
    # ----------------- Registro de usuario en Cognito y Base de Datos -----------------
    ####################################################################################
    try:
        response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=user.student_code,
            Password=user.password,
            UserAttributes=[
                {'Name': 'email', 'Value': user.email},
                {'Name': 'name', 'Value': user.full_name}
            ]
        )

        nuevo_usuario = clases.Usuario(
            usu_correo=user.email,
            usu_password=user.password,
            usu_nombre=user.full_name,
            usu_codigo=user.student_code
        )
        conexion.registrarUsuario(nuevo_usuario)

        return {"message": "Usuario registrado correctamente. Verifica tu correo.", "user_sub": response["UserSub"]}
    except cognito_client.exceptions.UsernameExistsException:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Cognito: {str(e)}")

class LoginUser:
    def __init__(self, student_code: str = Form(...), password: str = Form(...)):
        self.student_code = student_code
        self.password = password

@api_router.post("/login/")
def login_user(user: LoginUser = Depends()):
    try:
        response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": user.student_code,
                "PASSWORD": user.password
            }
        )
        return {"access_token": response["AuthenticationResult"]["AccessToken"]}
    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Cognito: {str(e)}")

class VerifyUser:
    def __init__(self, student_code: str = Form(...), code: str = Form(...)):
        self.student_code = student_code
        self.code = code

@api_router.post("/verify/")
def verify_user(user: VerifyUser = Depends()):
    try:
        cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=user.student_code,
            ConfirmationCode=user.code
        )
        return {"message": "Cuenta verificada exitosamente. Ya puedes iniciar sesión."}
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    except cognito_client.exceptions.CodeMismatchException:
        raise HTTPException(status_code=400, detail="Código incorrecto")
    except cognito_client.exceptions.ExpiredCodeException:
        raise HTTPException(status_code=400, detail="El código ha expirado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Cognito: {str(e)}")

def verify_token(request: Request):
    """Función para validar el token de acceso de Cognito"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Token requerido")

    token = auth_header.split("Bearer ")[-1]
    try:
        keys_url = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
        keys = requests.get(keys_url).json()["keys"]
        decoded_token = jwt.decode(token, options={"verify_signature": False})

        if decoded_token["iss"] != f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}":
            raise HTTPException(status_code=401, detail="Token inválido")
        
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

class DeleteUser:
    def __init__(self, student_code: str = Form(...)):
        self.student_code = student_code

#######################################################################################
# ----------------- Eliminación de usuario en Cognito y Base de Datos -----------------
#######################################################################################
class DeleteUser:
    def __init__(self, student_code: str = Form(...)):
        self.student_code = student_code

@api_router.delete("/delete_user/")
def delete_user(user: DeleteUser = Depends()):
    try:
        # Buscar usuario en la base de datos
        usuario_db = conexion.buscarUsuarioPorCodigo(user.student_code)
        if not usuario_db:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos")

        # Eliminar usuario en Cognito
        cognito_client.admin_delete_user(
            UserPoolId=USER_POOL_ID,
            Username=user.student_code
        )

        # Eliminar usuario en la base de datos
        conexion.borrarUsuarioPorCodigo(user.student_code)

        return {"message": "Usuario eliminado en Cognito y base de datos"}

    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en Cognito")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando usuario: {str(e)}")

# Incluir router en la aplicación principal
app.include_router(api_router)
