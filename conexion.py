import mysql.connector
from dotenv import load_dotenv
import os
import clases

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def devolverUnUsuario(id:int):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()

    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"SELECT * FROM usuarios WHERE usu_id = {id};"
    cursor.execute(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    for resultado in resultados:
        print(resultado)
        
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados

#-----------------------------------------------CONSULTA GENERAL
def devolverRegistros(tabla:str):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()

    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"SELECT * FROM {tabla};"
    cursor.execute(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
        
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados

#-----------------------------------------------CONSULTAS INDIVIDUALES A TABLAS
def devolverArchivos():
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()

    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"SELECT * FROM archivos a JOIN usuarios u ON a.arc_usu_id_fk = u.usu_id;"
    cursor.execute(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
        
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados


#-----------------------------------------------INSERTAR
def registrarUsuario(usuario:clases.Usuario):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()
    
    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"INSERT INTO usuarios(usu_correo, usu_password, usu_nombre, usu_codigo) VALUES ('{usuario.usu_correo}', '{usuario.usu_password}', '{usuario.usu_nombre}', '{usuario.usu_codigo}');"
    cursor.execute(consulta)
    #print(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
    
    #Se envia la información verificando la insersión de datos
    conexion.commit() 
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados
    
def registrarArchivo(archivo:clases.Archivo):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()
    
    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"INSERT INTO archivos(arc_nombre, arc_ruta, arc_tiempo, arc_fecha , arc_usu_id_fk) VALUES ('{archivo.arc_nombre}', '{archivo.arc_ruta}', {archivo.arc_tiempo}, '{archivo.arc_fecha}', {archivo.usuario.usu_id});"
    cursor.execute(consulta)
    #print(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
    
    #Se envia la información verificando la insersión de datos
    conexion.commit() 
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados

#-----------------------------------------------ELIMINAR
def borrarUsuario(usuario:clases.Usuario):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()
    
    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"DELETE FROM usuarios WHERE usu_id = {usuario.usu_id};"
    cursor.execute(consulta)
    #print(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
    
    #Se envia la información verificando la eliminación de datos
    conexion.commit() 
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados
    
def borrarArchivo(archivo:clases.Archivo):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()
    
    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"DELETE FROM archivos WHERE arc_id = {archivo.arc_id};"
    cursor.execute(consulta)
    #print(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
    
    #Se envia la información verificando la eliminación de datos
    conexion.commit() 
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados

#-----------------------------------------------BUSCAR 
def buscarUsuario(id:int):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()

    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"SELECT * FROM usuario WHERE (usu_id = {id});"
    cursor.execute(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
        
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados

def buscarArchivo(id:int):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()

    # Ejecutar una consulta SQL para seleccionar datos
    consulta = f"SELECT * FROM archivos a JOIN usuarios u ON a.arc_usu_id_fk = u.usu_id WHERE (arc_id = {id});"
    cursor.execute(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()

    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
        
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados

#-----------------------------------------------ACTUALIZAR 
def actualizarUsuario(usuario:clases.Usuario):
    conexion = mysql.connector.connect(
        host=os.environ['host'],
        user=os.environ['user'],
        password=os.environ['password'],
        database=os.environ['database'],
        port=os.environ['port']
    )
    
    # Crear un objeto cursor para ejecutar consultas SQL
    cursor = conexion.cursor()

    # Ejecutar una consulta SQL para seleccionar datos
    if usuario.usu_password:
        consulta = f"UPDATE usuarios u SET u.usu_nombre = '{usuario.usu_nombre}', u.usu_password = '{usuario.usu_password}', u.usu_correo = '{usuario.usu_correo}', u.usu_codigo = '{usuario.usu_codigo}'   WHERE (usu_id = {usuario.usu_id});"
    else:
        consulta = f"UPDATE usuarios u SET u.usu_nombre = '{usuario.usu_nombre}', u.usu_correo = '{usuario.usu_correo}', u.usu_codigo = '{usuario.usu_codigo}'   WHERE (usu_id = {usuario.usu_id});"

    cursor.execute(consulta)

    # Obtener todos los resultados de la consulta
    resultados = cursor.fetchall()
    #print(consulta)
    # Mostrar los resultados
    # for resultado in resultados:
    #     print(resultado)
        
    # Cerrar el cursor y la conexión
    cursor.close()
    conexion.close()
    
    return resultados
