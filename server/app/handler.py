# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:00:26 2024

@author: anggi
"""

# app/handler.py

import json
import os
from watchdog.events import FileSystemEventHandler
from app.utils import is_file_processed, mark_file_as_processed
from app.database import insert_data_to_mysql

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return None
        else:
            if event.src_path.endswith(".json"):
                print(f'Archivo nuevo detectado: {event.src_path}')
                if not is_file_processed(event.src_path):
                    self.json_to_mysql(event.src_path)
                    mark_file_as_processed(event.src_path)
                else:
                    print(f'Archivo ya procesado: {event.src_path}')

    def json_to_mysql(self, json_file_path):
        try:
            # Leer el archivo JSON
            with open(json_file_path, 'r', encoding='utf-8-sig') as json_file:
                json_data = json.load(json_file)
                print(f'Datos JSON leídos: {json_data}')

            n_lote = json_data.get('n lote')
            datos = {
                "IDequipo": json_data.get('IDequipo'),
                "fecha": json_data.get('fecha'),
                "hora": json_data.get('hora'),
                "elapsedtime": json_data.get('elapsedtime'),
                "unidades": json_data.get('unidades'),
                "frecuencia": json_data.get('frecuencia'),
                "ECG": json_data.get('ECG', []),
                "PPG": json_data.get('PPG', []),
                "Resp": json_data.get('Resp', []),
                "Spo2": json_data.get('Spo2', []),
                "temp": json_data.get('temp', []),
                "SIS": json_data.get('SIS', []),
                "DIA": json_data.get('DIA', [])
            }

            json_row = json.dumps(datos)
            print(f'Datos convertidos a JSON: {json_row}')

            table_name = f"equipo_{datos['IDequipo']}"
            insert_data_to_mysql(n_lote, json_row, table_name)
            print(f'Datos insertados en la base de datos: Lote {n_lote}')
            
        except Exception as e:
            print(f"Error: {e}")

def process_existing_files(folder_path):
    handler = MyHandler()
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                print(f'Procesando archivo existente: {file_path}')
                if not is_file_processed(file_path):
                    handler.json_to_mysql(file_path)
                    mark_file_as_processed(file_path)
                    print(f'Archivo procesado: {file_path}')
                else:
                    print(f'Archivo ya procesado: {file_path}')
