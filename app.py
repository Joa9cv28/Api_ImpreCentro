from fastapi import FastAPI, HTTPException, APIRouter, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import os
import conexion
import clases
from datetime import datetime

app = FastAPI()
# Crear un router
api_router = APIRouter(prefix="/api")

# Carpeta donde se guardarán los archivos
UPLOAD_DIRECTORY = "documentos"

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
    filename = file.filename
    file_extension = os.path.splitext(filename)[1]
    now = datetime.now()
    filename = now.strftime("%Y%m%d%H%M%S")+str(now.microsecond)+file_extension
    file_location = os.path.join(UPLOAD_DIRECTORY, filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(datetime.now())
    return clases.Respuesta(success=True, message='All ok', data={"location": file_location})
    #return {"file_extension": file_extension,"filename": file.filename, "location": file_location}


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
    print(usuario)
    if (len(resultado) == 1):
        if (resultado[0][2] == usuario.password and resultado[0][1] == usuario.correo):
            return clases.Respuesta(success=True, message='All ok', data=None)
        else:
            return clases.Respuesta(success=False, message='Invalid password or email', data=None)
    elif (len(resultado) > 1):
        return clases.Respuesta(success=False, message='Please contact an administrator', data=None)
    elif (len(resultado) < 1):
        return clases.Respuesta(success=False, message='Invalid password or email', data=None)
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

