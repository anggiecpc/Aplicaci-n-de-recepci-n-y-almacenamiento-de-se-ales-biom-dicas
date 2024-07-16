# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:53:09 2024

@author: anggi
"""
import pandas as pd
import numpy as np
import neurokit2 as nk
import random
import string

# Función para generar números aleatorios de 9 dígitos sin repetir
def generar_numeros_aleatorios_sin_repetir(cantidad):
    numeros_generados = set()  # Conjunto para mantener valores únicos
    numeros = []
    while len(numeros) < cantidad:
        numero = random.randint(5000000, 23000000)
        if numero not in numeros_generados:
            numeros_generados.add(numero)
            numeros.append(numero)
    return numeros

# Función para generar fecha aleatoria en formato YYYY-MM-DD
def generar_fecha():
    year = random.randint(2020, 2025)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Limitado a 28 días para simplificar
    fecha = f'{year}-{month:02}-{day:02}'
    return fecha

# Función para generar hora aleatoria en formato HH:MM:SS
def generar_hora():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    hora = f'{hour:02}:{minute:02}:{second:02}'
    return hora

# Función para generar ID de equipo aleatorio sin repetir
def generar_ids_equipo_repetidos(cantidad):
    letra = random.choice(string.ascii_uppercase)  # Elegir una letra aleatoria
    numeros = random.randint(10, 99)  # Generar dos dígitos aleatorios
    id_equipo = f'{letra}{numeros}'
    ids_equipos = [id_equipo] * cantidad
    return ids_equipos

# Función para simular y guardar archivos CSV
def simular_y_guardar_archivos():
    # Generar 50 números aleatorios para identificar a los pacientes y a los equipos
    numeros_pacientes = generar_numeros_aleatorios_sin_repetir(10)
    ids_equipos = generar_ids_equipo_repetidos(10)
    
    # Archivo de texto para guardar parámetros utilizados
    with open('valores_utilizados.txt', 'w') as file:
        file.write('Parámetros utilizados:\n\n')
        
        # Generar y guardar datos para cada paciente
        for paciente_id, equipo_id in zip(numeros_pacientes, ids_equipos):
            # Parámetros comunes
            duration = 180  # Duración en segundos
            sampling_rate_ecg = 1000
            sampling_rate_others = 100
            valores_ecg = random.randint(70, 120)
            valores_ppg = random.randint(60, 100)
            valores_resp = random.randint(12, 20)

            # Generar señales
            ecg_signal = nk.ecg_simulate(duration=duration, heart_rate=valores_ecg, sampling_rate=sampling_rate_ecg)
            ppg_signal = nk.ppg_simulate(duration=duration, heart_rate=valores_ppg, sampling_rate=sampling_rate_others)
            resp_signal = nk.rsp_simulate(duration=duration, respiratory_rate= valores_resp, sampling_rate=sampling_rate_others)
            t_spo2 = np.arange(0, duration, 1/sampling_rate_others)
            spo2_valor = np.random.normal(98, 2, len(t_spo2))

            t_temp = np.arange(0, duration, 1/sampling_rate_others)
            temp_valor = np.random.normal(37, 1.5, len(t_temp))

            t_pani = np.arange(0, duration, 1/sampling_rate_others)
            presion_sistolica = np.random.randint(110, 140, size=len(t_pani))
            presion_diastolica = np.random.randint(70, 90, size=len(t_pani))

            # Crear DataFrames individuales para cada señal
            df_ecg = pd.DataFrame({
                'Elapsed time': np.arange(0, duration, 1/sampling_rate_ecg),
                'ECG': ecg_signal
            })

            df_ppg = pd.DataFrame({
                'Elapsed time': np.arange(0, duration, 1/sampling_rate_others),
                'PPG': ppg_signal
            })

            df_resp = pd.DataFrame({
                'Elapsed time': np.arange(0, duration, 1/sampling_rate_others),
                'Resp': resp_signal
            })

            df_spo2 = pd.DataFrame({
                'Elapsed time': t_spo2,
                'Spo2': spo2_valor
            })

            df_temp = pd.DataFrame({
                'Elapsed time': t_temp,
                'temp': temp_valor
            })

            df_pani = pd.DataFrame({
                'Elapsed time': t_pani,
                'SIS': presion_sistolica,
                'DIA': presion_diastolica
            })

            # Crear un rango de tiempos comunes
            common_time = np.arange(0, duration, 1/sampling_rate_ecg)

            # Crear un DataFrame base con el tiempo común
            df_common_time = pd.DataFrame({'Elapsed time': common_time})

            # Hacer merge de todos los DataFrames en el tiempo común
            df = pd.merge(df_common_time, df_ecg, on='Elapsed time', how='left')
            df = pd.merge(df, df_ppg, on='Elapsed time', how='left')
            df = pd.merge(df, df_resp, on='Elapsed time', how='left')
            df = pd.merge(df, df_spo2, on='Elapsed time', how='left')
            df = pd.merge(df, df_temp, on='Elapsed time', how='left')
            df = pd.merge(df, df_pani, on='Elapsed time', how='left')

            # Rellenar NaNs con 0
            df = df.fillna(0)

            # Redondear las columnas numéricas a 3 decimales
            numeric_columns = ['Elapsed time', 'ECG', 'PPG', 'Resp', 'Spo2', 'temp', 'SIS', 'DIA']
            df[numeric_columns] = df[numeric_columns].round(3)

            # Generar la columna de hora y fecha aleatorias
            df['hora'] = generar_hora()
            df['fecha'] = generar_fecha()

            # Generar ID de equipo aleatorio
            df['ID equipo'] = equipo_id

            # Reorganizar las columnas
            df = df[['ID equipo', 'fecha', 'hora', 'Elapsed time', 'ECG', 'PPG', 'Resp', 'Spo2', 'temp', 'SIS', 'DIA']]

            # Añadir fila de unidades
            units = ['-', '-', '-', 'Elapsed time = s', 'ECG = mV', 'PPG = a.u.', 'Resp = L/min', 'Spo2 = %', 'temp = °C', 'SIS = mmHg', 'DIA = mmHg']
            df_units = pd.DataFrame([units], columns=df.columns)

            # Añadir fila de tasas de muestreo
            sampling_rates = ['-', '-', '-', '-', 'ECG = 1000 Hz', 'PPG = 100 Hz', 'Resp = 100 Hz', 'spo2 = 100 Hz', 'temp = 100 Hz', 'SIS = 100 Hz', 'DIA = 100 Hz']
            df_sampling_rates = pd.DataFrame([sampling_rates], columns=df.columns)

            # Concatenar las filas de unidades y tasas de muestreo con el DataFrame original
            df_final = pd.concat([df_units, df_sampling_rates, df])

            # Guardar a CSV con nombre único basado en el ID del paciente
            nombre_archivo = f'Paciente_{paciente_id}.csv'
            df_final.to_csv(nombre_archivo, index=False)

            # Escribir los parámetros utilizados en el archivo de texto
            file.write(f'Paciente ID: {paciente_id}\n')
            file.write(f'Fecha: {df["fecha"].iloc[0]}\n')
            file.write(f'Hora: {df["hora"].iloc[0]}\n')
            file.write(f'ID Equipo: {equipo_id}\n')
            file.write(f'ECG: valores_ecg:.2f\n')
            file.write(f'PPG: valores_ppg:.2f\n')
            file.write(f'Respiración: valores_resp:.2f\n')
            file.write(f'SpO2: mean = {df_spo2["Spo2"].mean():.2f}, std = {df_spo2["Spo2"].std():.2f}\n')
            file.write(f'Temperatura: mean = {df_temp["temp"].mean():.2f}, std = {df_temp["temp"].std():.2f}\n')
            file.write(f'Presión Sistólica: mean = {df_pani["SIS"].mean():.2f}, std = {df_pani["SIS"].std():.2f}\n')
            file.write(f'Presión Diastólica: mean = {df_pani["DIA"].mean():.2f}, std = {df_pani["DIA"].std():.2f}\n\n')
            print("Paciente ID "+str(paciente_id)+" generado")
# Ejecutar la función para simular y guardar los archivos
simular_y_guardar_archivos()
print("Proceso  de creación de archivos finalizado")

# #GRAFICAR SEÑALES
# import pandas as pd
# import matplotlib.pyplot as plt



# # Leer el archivo CSV especificando los tipos de datos
# dtype_dict = {
#     'ID equipo': 'str',
#     'fecha': 'str',
#     'hora': 'str',
#     'Elapsed time': 'float64',
#     'ECG': 'float64',
#     'PPG': 'float64',
#     'Resp': 'float64',
#     'Spo2': 'float64',
#     'temp': 'float64',
#     'SIS': 'float64',
#     'DIA': 'float64'
# }

# df_final = pd.read_csv('Paciente_17209500.csv')

# # Filtrar solo las filas de datos reales (omitir las primeras dos filas)
# df_data = df_final.iloc[2:].copy()
# df_data = df_data.astype(dtype_dict)

# # Convertir la columna 'hora' a un formato datetime para facilitar el graficado
# df_data['hora'] = pd.to_datetime(df_data['hora'], format='%H:%M:%S')

# # Configurar el tamaño de las figuras
# plt.figure(figsize=(15, 10))

# # Graficar ECG
# plt.subplot(3, 2, 1)
# plt.plot(df_data['Elapsed time'][:15000], df_data['ECG'][:15000], label='ECG')
# plt.title('ECG Signal')
# plt.xlabel('Hora')
# plt.ylabel('ECG')
# plt.legend()

# # Graficar PPG
# plt.subplot(3, 2, 2)
# plt.plot(df_data['Elapsed time'][:15000], df_data['PPG'][:15000], label='PPG', color='orange')
# plt.title('PPG Signal')
# plt.xlabel('Hora')
# plt.ylabel('PPG')
# plt.legend()

# # Graficar Respiración
# plt.subplot(3, 2, 3)
# plt.plot(df_data['Elapsed time'][:15000], df_data['Resp'][:15000], label='Respiración', color='green')
# plt.title('Respiración Signal')
# plt.xlabel('Hora')
# plt.ylabel('Resp')
# plt.legend()

# # Graficar SpO2
# plt.subplot(3, 2, 4)
# plt.plot(df_data['Elapsed time'][:15000], df_data['Spo2'][:15000], label='Spo2', color='red')
# plt.title('SpO2 Signal')
# plt.xlabel('Hora')
# plt.ylabel('SpO2')
# plt.legend()

# # Graficar Temperatura
# plt.subplot(3, 2, 5)
# plt.plot(df_data['Elapsed time'][:15000], df_data['temp'][:15000], label='Temperatura', color='purple')
# plt.title('Temperatura')
# plt.xlabel('Hora')
# plt.ylabel('Temp')
# plt.legend()

# # Graficar Presión Arterial
# plt.subplot(3, 2, 6)
# plt.plot(df_data['Elapsed time'][:15000], df_data['SIS'][:15000], label='Presión Sistólica', color='blue')
# plt.plot(df_data['Elapsed time'][:15000], df_data['DIA'][:15000], label='Presión Diastólica', color='cyan')
# plt.title('Presión Arterial')
# plt.xlabel('Hora')
# plt.ylabel('Presión')
# plt.legend()

# # Ajustar el layout y mostrar la gráfica
# plt.tight_layout()
# plt.show()
