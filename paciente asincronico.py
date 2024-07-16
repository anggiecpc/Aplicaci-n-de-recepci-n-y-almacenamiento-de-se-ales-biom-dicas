#!/usr/bin/env python3  
import socket
import csv
import json
import sys
import os
import threading
import time

# Configura el host y el puerto del servidor al que te conectarás
HOST = '172.16.253.29'  # Cambia esto por la dirección IP del servidor
PORT = 49152  # Puerto del servidor

# Variable global para controlar el estado del envío de datos
data_sending_active = True

def send_data(data):
    global data_sending_active
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # Conéctate al servidor
            client_socket.connect((HOST, PORT))
            client_socket.settimeout(10)

            # Convierte los datos a JSON
            json_data = json.dumps(data)

            # Envía los datos al servidor
            client_socket.sendall(json_data.encode())
            print("Datos enviados")
            data_sending_active = True  # Indicar que los datos se están enviando
    except (socket.timeout, socket.error) as e:
        print(f"Error al enviar datos: {e}")
        data_sending_active = False  # Indicar que el envío de datos falló

def get_last_batch_number(equipo_id):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # Conéctate al servidor
            client_socket.connect((HOST, PORT))
            client_socket.settimeout(10)

            # Solicita el último número de lote procesado para el ID del equipo al servidor
            request = json.dumps({"action": "GET_LAST_BATCH_NUMBER", "equipo_id": equipo_id})
            print(f"Enviando solicitud al servidor: {request}")  # Agregar mensaje de depuración
            client_socket.sendall(request.encode())

            # Recibe la respuesta del servidor
            data = client_socket.recv(1024)
            response = json.loads(data.decode())
            print(f"Respuesta recibida del servidor: {response}")  # Agregar mensaje de depuración

            # Verificar y procesar la respuesta
            if isinstance(response, dict) and 'ultimo_lote' in response:
                for item in response['ultimo_lote']:
                    if 'ID equipo' in item and 'Numero de lote' in item:
                        if item['ID equipo'].lower() == str(equipo_id).lower():
                            last_batch_number = item['Numero de lote']
                            print(f"Último número de lote recibido del servidor para equipo {equipo_id}: {last_batch_number}")
                            return last_batch_number
            # Si no se encuentra el ID del equipo, retornar 0 por defecto
            print(f"No se encontró el ID del equipo {equipo_id} en la respuesta del servidor.")
            return 0
    except (socket.timeout, socket.error) as e:
        print(f"Error al obtener el último número de lote: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar la respuesta JSON: {e}")
        sys.exit(1)

def process_and_send_data(csv_file_path, start_batch):
    num = start_batch  # Iniciar desde el siguiente lote después del último registrado
    print("Último lote", num)

    with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)  # Leer la fila de encabezados

        # Leer las dos primeras filas para obtener unidades y frecuencia
        unidades = next(csv_reader)
        frecuencia = next(csv_reader)

        batch_size = 500  # Número de filas a leer en cada lote
        batch_count = 0
        batch_data = []

        # Saltar filas según el lote en el que va
        for _ in range(start_batch * batch_size):
            next(csv_reader)

        # Leer los datos y enviarlos al servidor en lotes de 500 filas
        tiempo_1 = time.time()
        for row in csv_reader:
            batch_data.append(row)
            batch_count += 1

            # Si el tamaño del lote alcanza 500, envía el lote al servidor
            if batch_count == batch_size:
                # Construir el JSON del lote
                batch_json = {
                    "n lote": num,
                    "IDequipo": batch_data[0][0],
                    "fecha": batch_data[0][1],
                    "hora": batch_data[0][2],
                    "elapsedtime": batch_data[0][3],
                    "unidades": unidades,
                    "frecuencia": frecuencia,
                    "ECG": [float(row[4]) for row in batch_data if float(row[4]) != 0],
                    "PPG": [float(row[5]) for row in batch_data if float(row[5]) != 0],
                    "Resp": [float(row[6]) for row in batch_data if float(row[6]) != 0],
                    "Spo2": [float(row[7]) for row in batch_data if float(row[7]) != 0],
                    "temp": [float(row[8]) for row in batch_data if float(row[8]) != 0],
                    "SIS": [float(row[9]) for row in batch_data if float(row[9]) != 0],
                    "DIA": [float(row[10]) for row in batch_data if float(row[10]) != 0]
                }

                # Envía el lote al servidor
                tiempo_2 = time.time()
                diff = tiempo_2 - tiempo_1
                while diff < 0.5:
                    tiempo_2 = time.time()
                    diff = tiempo_2 - tiempo_1
                print(f"Enviando lote {num} después de {diff} segundos")
                send_data(batch_json)
                num += 1
                # Reiniciar el lote
                batch_data = []
                batch_count = 0
                tiempo_1 = time.time()

        # Enviar los datos restantes si hay menos de 500 en el último lote
        if batch_count > 0:
            batch_json = {
                "n lote": num,
                "IDequipo": batch_data[0][0],
                "fecha": batch_data[0][1],
                "hora": batch_data[0][2],
                "elapsedtime": batch_data[0][3],
                "unidades": unidades,
                "frecuencia": frecuencia,
                "ECG": [float(row[4]) for row in batch_data if float(row[4]) != 0],
                "PPG": [float(row[5]) for row in batch_data if float(row[5]) != 0],
                "Resp": [float(row[6]) for row in batch_data if float(row[6]) != 0],
                "Spo2": [float(row[7]) for row in batch_data if float(row[7]) != 0],
                "temp": [float(row[8]) for row in batch_data if float(row[8]) != 0],
                "SIS": [float(row[9]) for row in batch_data if float(row[9]) != 0],
                "DIA": [float(row[10]) for row in batch_data if float(row[10]) != 0]
            }
            print(f"Enviando último lote {num}")
            send_data(batch_json)

def watchdog():
    global data_sending_active
    while True:
        if not data_sending_active:
            print("Interrupción detectada. Reiniciando el script...")
            restart_script()
        time.sleep(5)  # Verificar cada 5 segundos

def restart_script():
    python = sys.executable
    os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    # Ruta al archivo CSV
    csv_file_path =  "/home/anggiecpc/Desktop/paciente 123/Paciente 123.csv"

    # Obtener el ID del equipo desde el archivo CSV
    with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)  # Leer la fila de encabezados
        unidades = next(csv_reader)
        frecuencia = next(csv_reader)
        first_data_row = next(csv_reader)  # Leer la primera fila de datos
        equipo_id = first_data_row[0]  # Asumiendo que el ID del equipo está en la primera columna
        equipo_id = equipo_id.lower()
        print(equipo_id)

    # Iniciar el watchdog en un hilo separado
    watchdog_thread = threading.Thread(target=watchdog)
    watchdog_thread.daemon = True
    watchdog_thread.start()

    # Obtener el último número de lote desde el servidor para el ID del equipo
    start_batch = get_last_batch_number(equipo_id)

    # Asegurarse de que start_batch sea un número
    if start_batch is None:
        start_batch = 0

    # Procesar y enviar los datos comenzando desde el lote especificado
    process_and_send_data(csv_file_path, start_batch)
