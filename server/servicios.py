import socket
import os
import json
import time
import mysql.connector
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
from flask import Flask, jsonify
from datetime import timedelta

# Configura el host y el puerto del servidor
HOST = '192.168.0.2'  # Cambia esto por la dirección IP del servidor
PORT = 49152  # Puerto del servidor

# Ruta de la carpeta donde se guardarán los archivos JSON
folder_path = "C:\\Users\\anggi\\OneDrive\\Escritorio\\GIT\\proyecto_biomedico\\server\\received_data"

# Ruta del archivo de registro de archivos procesados
processed_files_log = os.path.join(folder_path, "processed_files.log")

# Verificar y crear la carpeta si no existe
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"Carpeta creada: {folder_path}")

# Verificar y crear el archivo de registro si no existe
if not os.path.exists(processed_files_log):
    with open(processed_files_log, 'w') as log_file:
        log_file.write('')
    print(f"Archivo de registro creado: {processed_files_log}")

# Configuración de la conexión a MySQL
mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": "Dolasso.2015",
    "database": "bdseñales1lineaporeq"
}

# Función para verificar si un archivo ya ha sido procesado
def is_file_processed(file_name):
    with open(processed_files_log, 'r') as log_file:
        processed_files = log_file.read().splitlines()
    return file_name in processed_files

# Función para marcar un archivo como procesado
def mark_file_as_processed(file_name):
    with open(processed_files_log, 'a') as log_file:
        log_file.write(file_name + '\n')

# Clase para manejar eventos de creación de archivos en la carpeta monitoreada
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
                print(f'Datos JSON leídos: {json_data}')  # Añade esta línea para depuración

            # Extraer los datos directamente del JSON
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
            print(f'Datos convertidos a JSON: {json_row}')  # Añade esta línea para depuración

            # Conectar a la base de datos
            db_connection = mysql.connector.connect(**mysql_config)
            cursor = db_connection.cursor()

            # Crear tabla si no existe
            table_name = f"equipo_{datos['IDequipo']}"
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
            print(f'Datos insertados en la base de datos: Lote {n_lote}')  # Añade esta línea para depuración

            # Confirmar los cambios en la base de datos
            db_connection.commit()



        except mysql.connector.Error as err:
            print(f"Error de MySQL: {err}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Cerrar el cursor y la conexión a la base de datos
            if cursor:
                cursor.close()
            if db_connection:
                db_connection.close()

# Función para obtener el último lote cargado en la base de datos
def get_last_batch_numbers():
    try:
        db_connection = mysql.connector.connect(**mysql_config)
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

# Función para iniciar el servidor
def start_server():
    # Crear un socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Enlazar el socket al puerto
        server_socket.bind((HOST, PORT))

        # Empezar a escuchar conexiones entrantes
        server_socket.listen()
        server_socket.settimeout(20)

        print("Servidor escuchando en", HOST, ":", PORT)

        while True:
            try:
                # Aceptar la conexión entrante
                connection, address = server_socket.accept()
                print('Conexión entrante desde', address)

                with connection:
                    # Obtener el último lote cargado
                    last_batch_number = get_last_batch_numbers()
                    print(f"Último lote cargado: {last_batch_number}")

                    # Enviar el número del último lote al cliente
                    connection.sendall(json.dumps({"ultimo_lote": last_batch_number}).encode('utf-8'))

                    data_received = b''
                    while True:
                        # Recibir los datos del cliente
                        chunk = connection.recv(1024)
                        if not chunk:
                            break  # Si no hay datos, salir del bucle
                        data_received += chunk

                    json_received = data_received.decode("utf-8")
                    print(f'Datos recibidos: {json_received}')

                    try:
                        data = json.loads(json_received)
                        connection.sendall('Datos recibidos con éxito. ¡Gracias!'.encode('utf-8'))
                    except json.JSONDecodeError:
                        error_msg = 'Error: Datos recibidos no son un JSON válido.'
                        print(error_msg)
                        connection.sendall(error_msg.encode('utf-8'))
                        continue

                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                    # Obtener el ID del equipo
                    IDequipo = data.get("IDequipo")
                    if not IDequipo:
                        error_msg = "Error: No se encontró el ID del equipo en los datos recibidos."
                        print(error_msg)
                        connection.sendall(error_msg.encode('utf-8'))
                        continue

                    # Obtener el número de lote
                    n_lote = data.get("n lote")
                    if not n_lote:
                        error_msg = "Error: No se encontró el número de lote en los datos recibidos."
                        print(error_msg)
                        connection.sendall(error_msg.encode('utf-8'))
                        continue

                    # Crear una subcarpeta basada en el ID del equipo
                    equipo_folder_path = os.path.join(folder_path, IDequipo)
                    if not os.path.exists(equipo_folder_path):
                        os.makedirs(equipo_folder_path)

                    # Generar un nombre de archivo basado en el número de lote
                    base_file_name = f"data_lote_{n_lote}.json"
                    file_name = os.path.join(equipo_folder_path, base_file_name)

                    # Manejar nombres de archivos duplicados
                    counter = 1
                    while os.path.exists(file_name):
                        file_name = os.path.join(equipo_folder_path, f"data_lote_{n_lote}_{counter}.json")
                        counter += 1

                    # Guardar los datos recibidos en el archivo
                    with open(file_name, 'w') as file:
                        json.dump(data, file, indent=2)
                        file.write("\n")

                    print("Datos guardados en", file_name)

            except ConnectionResetError:
                print('Conexión cerrada por el host remoto. Continuando...')
            except socket.timeout:
                print("Tiempo de espera agotado. Continuando...")
            except Exception as e:
                error_msg = f"Error inesperado: {e}"
                print(error_msg)
                if connection:
                    connection.sendall(error_msg.encode('utf-8'))




# Función para procesar archivos existentes en la carpeta
def process_existing_files():
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


# Función para iniciar el monitor de la carpeta
def start_monitor():
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_path, recursive=True)
    observer.start()
    print(f'Monitoreando cambios en la carpeta: {folder_path}')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


app = Flask(__name__)


def obtener_datos_por_rut(rut, consulta):
    conn = mysql.connector.connect(**mysql_config)
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

    # Convertir objetos timedelta a cadenas de texto y convertir JSON strings a diccionarios
    data_converted = []
    for row in datos:
        converted_row = []
        for item in row:
            if isinstance(item, timedelta):
                converted_row.append(str(item))  # Convertir timedelta a cadena de texto
            elif isinstance(item, str):
                try:
                    json_item = json.loads(item)  # Intentar convertir cadenas JSON a diccionarios
                    converted_row.append(json_item)
                except json.JSONDecodeError:
                    converted_row.append(item)  # Si no es un JSON válido, dejarlo como está
            else:
                converted_row.append(item)
        data_converted.append(converted_row)

    return columnas, data_converted

# Ruta para obtener datos de un paciente por su RUT desde MySQL
@app.route('/')
def index():
    return '¡Hola, mundo! Esta es la página principal.'

@app.route('/mysql/<rut>', methods=['GET'])
def datos_paciente_por_rut(rut):
    # Obtener los datos asociados con ese RUT
    columnas, datos = obtener_datos_por_rut(rut, "SELECT * FROM paciente_mediciones")

    return jsonify({'columnas': columnas, 'filas': datos})


# Iniciar el servidor
if __name__ == "__main__":
    # Procesar archivos existentes en la carpeta
    process_existing_files()

    # Iniciar el servidor en un hilo separado
    server_thread = Thread(target=start_server)
    server_thread.start()

    # Esperar a que el servidor Flask se inicie completamente antes de continuar
    time.sleep(2)  # Ajusta este tiempo según sea necesario

    # Iniciar la API Flask en un hilo separado
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False))
    flask_thread.start()

    # Esperar a que la API Flask se inicie completamente antes de continuar
    time.sleep(2)  # Ajusta este tiempo según sea necesario

    # Iniciar el monitor de la carpeta en el hilo principal
    start_monitor()

