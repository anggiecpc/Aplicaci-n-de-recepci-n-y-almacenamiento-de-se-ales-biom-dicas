# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:00:07 2024

@author: anggi
"""

# app/database.py



import mysql.connector
from app.config import MYSQL_CONFIG

def get_last_batch_number_by_id(ID_equipo):
    try:
        db_connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db_connection.cursor()
        
        # Obtener el máximo número de lote para el ID de equipo dado
        query_max = f"""
            SELECT MAX(numero_lote) 
            FROM registros 
            WHERE ID_equipo = %s
        """
        cursor.execute(query_max, (ID_equipo,))
        result = cursor.fetchone()
        last_batch_number = result[0] if result[0] is not None else 0
        
    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
        last_batch_number = 0
    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()
    
    return last_batch_number

def insert_data_to_mysql(n_lote, json_row, ID_equipo):
    try:
        db_connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db_connection.cursor()
        # Insertar la fila de datos JSON en la tabla correspondiente
        query = """
        INSERT INTO registros (numero_lote, ID_equipo, datos)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (n_lote, ID_equipo, json_row))
        db_connection.commit()
        
    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()

