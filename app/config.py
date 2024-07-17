# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 13:59:32 2024

@author: anggi
"""

# app/config.py

import os

# Configura el host y el puerto del servidor
HOST = '192.168.1.107'  # Cambia esto por la dirección IP del servidor
PORT = 49152  # Puerto del servidor

# Ruta de la carpeta donde se guardarán los archivos JSON
FOLDER_PATH = "C:\\Users\\anggi\\OneDrive\\Escritorio\\GIT\\Aplicación de recepción y almacenamiento de señales biomédicas\\received_data"

# Ruta del archivo de registro de archivos procesados
PROCESSED_FILES_LOG = os.path.join(FOLDER_PATH, "processed_files.log")

# Verificar y crear la carpeta si no existe
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)
    print(f"Carpeta creada: {FOLDER_PATH}")

# Verificar y crear el archivo de registro si no existe
if not os.path.exists(PROCESSED_FILES_LOG):
    with open(PROCESSED_FILES_LOG, 'w') as log_file:
        log_file.write('')
    print(f"Archivo de registro creado: {PROCESSED_FILES_LOG}")

# Configuración de la conexión a MySQL
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Dolasso.2015",
    "database": "bdseñales1lineaporeq"
}
