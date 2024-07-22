import subprocess
import time

# Lista de archivos Python que deseas ejecutar
files = [
    "Paciente_5603537.py", "Paciente_6162990.py", "Paciente_6646069.py", "Paciente_7532587.py"
]

def run_script(file):
    while True:
        try:
            process = subprocess.Popen(["python", file])
            process.wait()
            # Si el script termina sin excepción, salimos del bucle
            break
        except Exception as e:
            print(f"Se detectó una excepción en {file}: {e}. Reiniciando el script...")
            time.sleep(1)  # Espera un segundo antes de reiniciar el script

# Ejecuta cada archivo en paralelo
# Ejecuta cada archivo en paralelo
processes = []
for file in files:
    process = subprocess.Popen(["python", file])
    processes.append(process)

# Espera a que todos los procesos terminen
for process in processes:
    process.wait()
