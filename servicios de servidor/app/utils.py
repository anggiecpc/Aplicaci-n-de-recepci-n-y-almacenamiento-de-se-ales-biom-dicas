# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:01:09 2024

@author: anggi
"""

# app/utils.py

import os
import json
from datetime import timedelta
from app.config import PROCESSED_FILES_LOG, MYSQL_CONFIG
import mysql.connector

def is_file_processed(file_name):
    with open(PROCESSED_FILES_LOG, 'r') as log_file:
        processed_files = log_file.read().splitlines()
    return file_name in processed_files

def mark_file_as_processed(file_name):
    with open(PROCESSED_FILES_LOG, 'a') as log_file:
        log_file.write(file_name + '\n')

def obtener_datos_por_rut(rut, consulta):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    consulta_rut = """
      SELECT *
      FROM ({}) AS subconsulta
      WHERE ID_paciente = '{}'
      ORDER BY Fecha_salida DESC, Hora_salida DESC
      LIMIT 300000
    """.format(consulta, rut)

    cursor.execute(consulta_rut)
    columnas = [desc[0] for desc in cursor.description]
    datos = cursor.fetchall()
    cursor.close()
    conn.close()

    data_converted = []
    for row in datos:
        converted_row = []
        for item in row:
            if isinstance(item, timedelta):
                converted_row.append(str(item))
            elif isinstance(item, str):
                try:
                    json_item = json.loads(item)
                    converted_row.append(json_item)
                except json.JSONDecodeError:
                    converted_row.append(item)
            else:
                converted_row.append(item)
        data_converted.append(converted_row)

    return columnas, data_converted
