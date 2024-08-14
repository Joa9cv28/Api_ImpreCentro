from pydantic import BaseModel
from typing import Optional
from datetime import datetime 

class Usuario(BaseModel):
    usu_id: Optional[int] = None
    usu_correo: str
    usu_password: Optional[str] = None
    usu_nombre: str
    usu_codigo: str
    
class Archivo(BaseModel):
    arc_id: Optional[int] = None
    arc_nombre: str
    arc_ruta: str
    arc_tiempo: float
    arc_fecha: datetime
    usuario: Usuario
    
class Respuesta(BaseModel):
    success: bool
    message: str
    data: object
    
class Login(BaseModel):
    correo: str
    password: str