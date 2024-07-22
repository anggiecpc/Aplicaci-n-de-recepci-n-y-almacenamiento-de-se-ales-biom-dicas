#!/usr/bin/env python3  
import os
import sys
import time
import threading
import socket
import csv
import json
from datetime import datetime

# Configura el host y el puerto del servidor al que te conectarás
HOST = '192.168.0.2'  # Cambia esto por la dirección IP del servidor
PORT = 49152  # Puerto del servidor

# Variable global para controlar el estado del envío de datos
data_sending_active = True

send_data_mutex = threading.Lock()
def send_data(data):
    global data_sending_active
    try:
        with send_data_mutex:
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
            client_socket.sendall(request.encode())

            # Recibe la respuesta del servidor
            data = client_socket.recv(1024)
            response = json.loads(data.decode())
            print(f"Respuesta recibida del servidor: {response}")  # Agregar mensaje de depuración

            # Verificar y procesar la respuesta
            if isinstance(response, dict) and 'ultimo_lote' in response:
                for item in response['ultimo_lote']:
                    if 'ID equipo' in item and 'Numero de lote' in item:
                        if item['ID equipo'] == str(equipo_id):
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
    num = start_batch
    with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)  # Leer la fila de encabezados

        # Leer las dos primeras filas para obtener unidades y frecuencia
        unidades = next(csv_reader)
        frecuencia = next(csv_reader)

        batch_size = 500  # Número de filas a leer en cada lote
        batch_count = 0
        batch_data = []
        patient_data = []

        # Leer los datos y almacenarlos en una lista
        for row in csv_reader:
            patient_data.append(row)

        total_batches = len(patient_data) // batch_size
        if total_batches == 0:
            print("No hay suficientes datos para procesar al menos un lote.")
            return

        max_batch_number = total_batches * 2

        if start_batch > max_batch_number:
            print("El número de lote inicial es mayor que el número máximo de lotes posibles. Proceso de envío de datos finalizado.")
            return

        if patient_data:
            total_batches = len(patient_data) // batch_size
            num_repetitions = start_batch // total_batches
            start_batch_in_cycle = start_batch % total_batches

            tiempo_1 = time.time()

            for i in range(num_repetitions, num_repetitions + 2):  # 2 repeticiones
                for j, row in enumerate(patient_data):
                    if j < start_batch_in_cycle * batch_size:
                        continue  # Salta las filas hasta el lote inicial

                    if num > (max_batch_number-1):
                        print("Proceso de envío de datos finalizado.")
                        return

                    # Calcular nuevo tiempo basado en la fila actual y el índice de repetición
                    new_elapsed_time = float(row[3]) + (i * 179.999)
                    new_time = datetime.now()
                    new_row = row.copy()
                    new_row[1] = new_time.strftime('%Y-%m-%d')
                    new_row[2] = new_time.strftime('%H:%M:%S')
                    new_row[3] = f"{new_elapsed_time:.3f}"
                    batch_data.append(new_row)
                    batch_count += 1

                    if batch_count == batch_size:
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
                        tiempo_2 = time.time()
                        diff = tiempo_2 - tiempo_1
                        while diff < 0.5:
                            tiempo_2 = time.time()
                            diff = tiempo_2 - tiempo_1
                        print(f"Enviando lote {num} después de {diff} segundos")
                        send_data(batch_json)
                        num += 1
                        batch_count = 0
                        batch_data = []
                        tiempo_1 = time.time()  # Reinicia el temporizador

            # Enviar los datos restantes si los hay
            if batch_data and num <= max_batch_number:
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
                print(f"Enviando lote final de datos de pacientes {num}")
                send_data(batch_json)
                num += 1

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
    csv_file_path =  "C:\\Users\\anggie\\Desktop\\CLIENTE_PRO\\SINCRONICO\\Paciente_6646069.csv"

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

    # Procesar y enviar los datos comenzando desde el lote especificado
    process_and_send_data(csv_file_path, start_batch)
