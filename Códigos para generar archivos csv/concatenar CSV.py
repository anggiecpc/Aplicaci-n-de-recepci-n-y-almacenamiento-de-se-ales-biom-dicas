import pandas as pd
import glob
import os

# Ruta donde están ubicados tus archivos CSV
file_path_pattern = "C:\\Users\\anggi\\OneDrive\\Escritorio\\PIB\\Nuevos datos\\concatenar asincronica eq 1\\*csv"

# Obtener la lista de todos los archivos CSV que coinciden con el patrón
csv_files = glob.glob(file_path_pattern)

if not csv_files:
    raise FileNotFoundError("No se encontraron archivos CSV que coincidan con el patrón especificado.")

# Leer el primer archivo CSV y añadirlo a la lista
df_combined = pd.read_csv(csv_files[0])

# Procesar el resto de los archivos CSV
for csv_file in csv_files[1:]:
    df_temp = pd.read_csv(csv_file)
    # Eliminar las filas de unidades y tasas de muestreo
    df_temp = df_temp.iloc[2:]
    # Concatenar el DataFrame temporal al DataFrame combinado
    df_combined = pd.concat([df_combined, df_temp], ignore_index=True)

# Ruta donde deseas guardar el archivo combinado
save_path = "C:\\Users\\anggi\\OneDrive\\Escritorio\\PIB\\Nuevos datos\\concatenar asincronica eq 1\\combined_file_asincronico.csv"

# Crear el directorio si no existe
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Guardar el DataFrame combinado en un nuevo archivo CSV
df_combined.to_csv(save_path, index=False)

print("Archivos CSV concatenados exitosamente y guardados en:", save_path)
