# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 14:00:31 2024

@author: anggi
"""

# app/server.py

import os
import socket
import json
from threading import Thread
from watchdog.observers import Observer
from flask import Flask, jsonify
from app.database import get_last_batch_number_by_id, insert_data_to_mysql
from app.config import HOST, PORT, FOLDER_PATH
from app.handler import MyHandler
from concurrent.futures import ThreadPoolExecutor
from app import app
import time

def handle_connection(connection, address):
    print('Conexión entrante desde', address)
    try:
        with connection:
            last_batch_number = get_last_batch_numbers()
            print(f"Último lote cargado: {last_batch_number}")

            connection.sendall(json.dumps({"ultimo_lote": last_batch_number}).encode('utf-8'))

            data_received = b''
            while True:
                chunk = connection.recv(1024)
                if not chunk:
                    break
                data_received += chunk
            json_received = data_received.decode("utf-8")
            print(f'Datos recibidos: {json_received}')

            try:
                data = json.loads(json_received)
                connection.sendall('Datos recibidos con éxito. ¡Gracias!'.encode('utf-8'))
            except json.JSONDecodeError:
                print("Error: Datos recibidos no son un JSON válido.")
                connection.sendall('Error: Datos recibidos no son un JSON válido.'.encode('utf-8'))
                return

            if not os.path.exists(FOLDER_PATH):
                os.makedirs(FOLDER_PATH)

            IDequipo = data.get("IDequipo")
            if not IDequipo:
                print("No se encontró el ID del equipo en los datos recibidos.")
                return

            n_lote = data.get("n lote")
            if not n_lote:
                print("No se encontró el número de lote en los datos recibidos.")
                return

            equipo_folder_path = FOLDER_PATH
            base_file_name = f"data_lote_{n_lote}.json"
            file_name = os.path.join(equipo_folder_path, base_file_name)

            counter = 1
            while os.path.exists(file_name):
                file_name = os.path.join(equipo_folder_path, f"data_lote_{n_lote}_{counter}.json")
                counter += 1

            with open(file_name, 'w') as file:
                json.dump(data, file, indent=2)
                file.write("\n")

            print("Datos guardados en", file_name)

    except ConnectionResetError:
        print('Conexión cerrada por el host remoto. Continuando...')
    except socket.timeout:
        print("Tiempo de espera agotado. Continuando...")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("Servidor escuchando en", HOST, ":", PORT)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            while True:
                try:
                    connection, address = server_socket.accept()
                    executor.submit(handle_connection, connection, address)
                except KeyboardInterrupt:
                    print("Servidor detenido por el usuario.")
                    break

# Función para iniciar el monitor de la carpeta
def start_monitor():
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=FOLDER_PATH, recursive=True)
    observer.start()
    print(f'Monitoreando cambios en la carpeta: {FOLDER_PATH}')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

@app.route('/')
def index():
    return '¡Hola, mundo! Esta es la página principal.'

@app.route('/mysql/<rut>', methods=['GET'])
def datos_paciente_por_rut(rut):
    from app.utils import obtener_datos_por_rut

    columnas, datos = obtener_datos_por_rut(rut, "SELECT * FROM paciente_mediciones")
    return jsonify({'columnas': columnas, 'filas': datos})

def run_flask():
    app.run(host='0.0.0.0', port=5000)
