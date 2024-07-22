# #ELIMINAR TABLAS

import mysql.connector

# Configuración de la conexión a MySQL
mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": "Dolasso.2015",
    "database": "bdseñales1lineaporeq"
}

def obtener_tablas():
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tablas = [tabla[0] for tabla in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tablas

def eliminar_datos(tabla):
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {tabla}")
    conn.commit()
    cursor.close()
    conn.close()



def eliminar_datos_de_todas_las_tablas():
    tablas = obtener_tablas()
    for tabla in tablas:
        if tabla.lower() == 'paciente_mediciones':
            continue  # Saltar la tabla 'metadatos'
        if tabla.lower() == 'metadatos':
            continue  # Saltar la tabla 'metadatos'
        
        print(f"Eliminando datos de la tabla: {tabla}")
        eliminar_datos(tabla)
    print("Datos eliminados de todas las tablas excepto 'metadatos' y 'paciente_mediciones'.")

# Ejemplo de uso: eliminar todos los datos de todas las tablas excluyendo vistas
eliminar_datos_de_todas_las_tablas()