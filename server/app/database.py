# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:00:07 2024

@author: anggi
"""

# app/database.py

import mysql.connector
from app.config import MYSQL_CONFIG

def get_last_batch_numbers():
    try:
        db_connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db_connection.cursor()
        
        # Obtener todas las tablas que comienzan con "equipo_"
        query = """
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_name LIKE 'equipo_%'
        """
        cursor.execute(query)
        tables = cursor.fetchall()
        
        last_batch_numbers = []
        
        # Iterar sobre cada tabla y obtener el máximo número de lote
        for table_name in tables:
            table_name = table_name[0]  # Obtener el nombre de la tabla
            query_max = f"SELECT MAX(numero_lote) FROM {table_name}"
            cursor.execute(query_max)
            result = cursor.fetchone()
            last_batch_number = result[0] if result[0] is not None else 0
            
            # Obtener el ID del equipo desde el nombre de la tabla
            equipo_id = table_name.split('_')[1]  # Obtener el ID del equipo
            equipo_id = equipo_id.lower()
            
            # Guardar el resultado en la lista
            last_batch_numbers.append({'ID equipo': equipo_id, 'Numero de lote': last_batch_number})
            
    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
        last_batch_numbers = 0
    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()
    
    return last_batch_numbers

def insert_data_to_mysql(n_lote, json_row, table_name):
    try:
        db_connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db_connection.cursor()

        # Crear tabla si no existe
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            numero_lote INT PRIMARY KEY UNIQUE,
            datos JSON
        )
        """
        cursor.execute(create_table_query)

        # Insertar la fila de datos JSON en la tabla correspondiente
        query = f"""
        INSERT INTO {table_name} (numero_lote, datos)
        VALUES (%s, %s)
        """
        cursor.execute(query, (n_lote, json_row))
        db_connection.commit()
        
    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()
