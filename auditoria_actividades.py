import psycopg2
from datetime import datetime

# Configuración de la conexión a la base de datos
DB_HOST = "localhost"
DB_NAME = "alcaldia_datos"
DB_USER = "postgres"
DB_PASSWORD = "daniel"

# Ruta del archivo de salida
OUTPUT_FILE = "auditoria_actividades.txt"

def obtener_actividades():
    # Conectar a la base de datos
    conexion = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    # Configuración de la consulta SQL
    consulta = """
    SELECT 
        auditoria.id, 
        usuarios.username, 
        usuarios.email, 
        usuarios.role, 
        auditoria.accion, 
        auditoria.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/Bogota' AS timestamp_local
    FROM auditoria_actividades AS auditoria
    JOIN usuarios ON auditoria.usuario_id = usuarios.id
    ORDER BY auditoria.timestamp;
    """

    try:
        # Ejecutar la consulta
        with conexion.cursor() as cursor:
            cursor.execute(consulta)
            actividades = cursor.fetchall()

        # Escribir el resultado en un archivo de texto con formato mejorado
        with open(OUTPUT_FILE, "w") as archivo:
            archivo.write(" Registro de Actividades de Auditoría \n")
            archivo.write("="*90 + "\n")
            archivo.write(f"{'ID':<5} | {'Usuario':<15} | {'Email':<25} | {'Rol':<15} | {'Acción':<30} | {'Timestamp (Hora Local)'}\n")
            archivo.write("="*90 + "\n")

            for actividad in actividades:
                id, username, email, role, accion, timestamp_local = actividad
                archivo.write(f"{id:<5} | {username:<15} | {email:<25} | {role:<15} | {accion[:30]:<30} | {timestamp_local}\n")

            archivo.write("="*90 + "\n")

        print(f"Archivo '{OUTPUT_FILE}' generado correctamente con los registros de auditoría.")

    except Exception as e:
        print("Error al obtener actividades de auditoría:", e)

    finally:
        conexion.close()

if __name__ == "__main__":
    obtener_actividades()
