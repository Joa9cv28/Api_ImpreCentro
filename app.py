from fastapi import FastAPI, HTTPException, APIRouter
import conexion
import clases

app = FastAPI()
# Crear un router
api_router = APIRouter(prefix="/api")
# Incluir el router en la aplicación principal
app.include_router(api_router)

@app.exception_handler(Exception)                     #TRY-CATCH
async def global_exception_handler(request, exc):
    # Registra la excepción o realiza acciones de manejo
    #imprimimos y devolvemos
    print(f"Error interno: {exc}")
    raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get('/') #RUTA RAIZ
def read_root():
    return {"welcome":"Welcome to my api"}

@app.get('/usuarios')
def read_usuarios():
    registros = conexion.devolverRegistros('usuarios')
    usuarios = []
    for registro in registros:
        usuarios.append(clases.Usuario(usu_id=registro[0], usu_correo=registro[1], usu_nombre=registro[3], usu_codigo=registro[4]))
    return clases.Respuesta(success=True, message='All ok', data=usuarios)

@app.get('/archivos')
def read_archivos():
    registros = conexion.devolverRegistros('archivos')
    archivos = []
    for registro in registros:
        archivos.append(clases.Archivo(arc_id=registro[0], arc_nombre=registro[1], arc_ruta=registro[2], arc_tiempo=registro[3], arc_fecha=registro[4], arc_usu_id_fk=registro[5]))
    return clases.Respuesta(success=True, message='All ok', data=archivos)

@app.post('/usuario')
def registrarUsuarios(usuario:clases.Usuario):
    resultado = conexion.registrarUsuario(usuario)
    return clases.Respuesta(success=True, message='All ok', data=resultado)




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

