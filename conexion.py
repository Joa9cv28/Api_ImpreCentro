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
    print(consulta)

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
    