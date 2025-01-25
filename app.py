from fastapi import FastAPI, HTTPException, APIRouter, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import os
import conexion
import clases
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile, HTTPException 
from pathlib import Path

app = FastAPI()
# Crear un router
api_router = APIRouter(prefix="/api")

# Carpeta donde se guardarán los archivos
UPLOAD_DIRECTORY = "documentos"

UPLOAD_FOLDER = Path("test")
UPLOAD_FOLDER.mkdir(exist_ok=True)  # Crea la carpeta si no existe

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins='*', ##IMPORTANTE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Asegúrate de que la carpeta exista
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.exception_handler(Exception)                     #TRY-CATCH
async def global_exception_handler(request, exc):
    # Registra la excepción o realiza acciones de manejo
    #imprimimos y devolvemos
    print(f"Error interno: {exc}")
    raise HTTPException(status_code=500, detail="Error interno del servidor")

@api_router.get('/') #RUTA RAIZ
def read_root():
    return {"welcome":"Welcome to my api"}

@api_router.get('/usuarios')
def read_usuarios():
    registros = conexion.devolverRegistros('usuarios')
    usuarios = []
    for registro in registros:
        usuarios.append(clases.Usuario(usu_id=registro[0], usu_correo=registro[1], usu_nombre=registro[3], usu_codigo=registro[4]))
    return clases.Respuesta(success=True, message='All ok', data=usuarios)

@api_router.get('/archivos')
def read_archivos():
    registros = conexion.devolverArchivos()
    archivos = []
    for registro in registros:
        archivos.append(clases.Archivo(arc_id=registro[0], arc_nombre=registro[1], arc_ruta=registro[2], arc_tiempo=registro[3], arc_fecha=registro[4], usuario=clases.Usuario(usu_id=registro[6], usu_correo=registro[7], usu_nombre=registro[9], usu_codigo=registro[10])))
    return clases.Respuesta(success=True, message='All ok', data=archivos)

@api_router.post('/usuario')
def registrarUsuarios(usuario:clases.Usuario):
    resultado = conexion.registrarUsuario(usuario)
    return clases.Respuesta(success=True, message='All ok', data=resultado)

@api_router.post('/archivo')
def registrarArchivo(archivo:clases.Archivo):
    archivo.arc_ruta = archivo.arc_ruta.replace("\\", "\\\\")
    print(archivo.arc_ruta)
    resultado = conexion.registrarArchivo(archivo)
    return clases.Respuesta(success=True, message='All ok', data=resultado)

    
    
@api_router.post("/subirArchivo")
async def subirArchivo(file: UploadFile):
    """
    Endpoint para subir un archivo de tipo .jpg y almacenarlo en la carpeta 'test'.
    """
    # Verifica que el archivo tenga extensión .jpg
    if not file.filename.lower().endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .jpg")

    # Limpia el nombre del archivo para evitar problemas de seguridad
    safe_filename = file.filename.replace("/", "").replace("\\", "")

    # Crea una ruta absoluta para garantizar que la carpeta esté bien definida
    file_path = UPLOAD_FOLDER / safe_filename

    # Asegúrate de que la carpeta de destino exista
    try:
        UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error al crear la carpeta: {e}")
        raise HTTPException(status_code=500, detail="No se pudo crear la carpeta de destino")

    try:
        # Guarda el archivo en la carpeta de destino
        with file_path.open("wb") as f:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="El archivo está vacío")
            f.write(content)

        print(f"Archivo guardado en: {file_path}")
        return {
            "success": True,
            "message": f"Archivo '{safe_filename}' subido correctamente",
            "data": {"filename": safe_filename, "path": str(file_path)}
        }
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        raise HTTPException(status_code=500, detail="No se pudo guardar el archivo")

    # filename = file.filename
    # file_extension = os.path.splitext(filename)[1]
    # now = datetime.now()
    # filename = now.strftime("%Y%m%d%H%M%S")+str(now.microsecond)+file_extension
    # file_location = os.path.join(UPLOAD_DIRECTORY, filename)
    # with open(file_location, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    # print(datetime.now())
    # return clases.Respuesta(success=True, message='All ok', data={"location": file_location})
    #return {"file_extension": file_extension,"filename": file.filename, "location": file_location}

    # @app.post("/upload")
    # async def upload_file(file: UploadFile = File(...)):

@api_router.get("/descargarArchivo/{id}")
async def get_file(id: int):
    archivo = conexion.buscarArchivo(id)
    file_path = archivo[0][2].replace("\\", "\\\\")
    if os.path.exists(file_path):
        print(file_path)
        return FileResponse(file_path, filename=archivo[0][1], media_type='application/octet-stream')
    return {"error": "Archivo no encontrado"} 

@api_router.post('/login')
def loginUsuario(usuario:clases.Login):
    resultado = conexion.loginUsuario(usuario)
    print(resultado)
    print()
    if (resultado['success'] == True):
        return clases.Respuesta(success=True, message='All ok', data=None)
    elif (resultado['success'] == False):
        if (resultado['message'] == 'Usuario no encontrado.' or resultado['message'] == 'Contraseña incorrecta.'):
            return clases.Respuesta(success=False, message='Invalid password or email', data=None)
        else:
            return clases.Respuesta(success=False, message='Please contact an administrator', data=None)
    return clases.Respuesta(success=False, message='Intern problems, please contact an administrator', data=None)

@api_router.delete('/usuario')
def borrarUsuario(usuario:clases.Usuario):
    resultado = conexion.borrarUsuario(usuario)
    return clases.Respuesta(success=True, message='All ok', data=resultado)

@api_router.delete('/archivo')
def borrarArchivo(archivo:clases.Archivo):
    resultado = conexion.borrarArchivo(archivo)
    return clases.Respuesta(success=True, message='All ok', data=resultado)

@api_router.put('/usuario')
def actualizarUsuario(usuario:clases.Usuario):
    resultado = conexion.actualizarUsuario(usuario)
    return clases.Respuesta(success=True, message='All ok', data=resultado)

# Incluir el router en la aplicación principal
app.include_router(api_router)


# {
# stauts: true,
# message: "All ok"
# data: {
# }}

# {
# stauts: true,
# message: "All ok",
# data: {
# id: 20,
# correo: "ASDASD",
# nombre: "ASDASDAS",
# password: "ASDASD",
# codigo: 12313122
# }
# }

