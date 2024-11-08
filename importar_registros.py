import pandas as pd
import psycopg2
from psycopg2 import sql
import numpy as np

# Configuración de la conexión
conexion = psycopg2.connect(
    host="localhost",
    database="alcaldia_datos",
    user="postgres",
    password="1234"  # Asegúrate de colocar tu contraseña
)
conexion.autocommit = True

# Leer el archivo Excel
archivo_excel = "Listado_Base.xlsx"
df = pd.read_excel(archivo_excel)

# Renombrar columnas y reemplazar valores NaN por None
df = df.rename(columns=lambda x: x.strip())
df = df.replace({np.nan: None})

# Definir una consulta de inserción parametrizada
consulta_insercion = sql.SQL("""
    INSERT INTO registro_personal (
        apellido_paterno, apellido_materno, nombres, identificacion, fecha_entrevista,
        telefono, perfil, hv, area, subgrupo, rol, riesgo
    ) VALUES (
        %(apellido_paterno)s, %(apellido_materno)s, %(nombres)s, %(identificacion)s,
        %(fecha_entrevista)s, %(telefono)s, %(perfil)s, %(hv)s, %(area)s, %(subgrupo)s,
        %(rol)s, %(riesgo)s
    )
""")

# Consulta para verificar duplicados
consulta_verificar = sql.SQL("SELECT 1 FROM registro_personal WHERE identificacion = %s")

# Truncar valores para que encajen en el límite de las columnas
def truncar(valor, limite):
    if isinstance(valor, str) and len(valor) > limite:
        return valor[:limite]
    return valor

# Convertir a fecha si es posible; de lo contrario, devolver None
def convertir_fecha(fecha):
    try:
        fecha_convertida = pd.to_datetime(fecha, errors='coerce')
        if pd.isnull(fecha_convertida):
            return None
        return fecha_convertida.date()
    except Exception:
        return None

# Procesar cada fila
with conexion:
    with conexion.cursor() as cursor:
        for _, fila in df.iterrows():
            identificacion = str(truncar(fila.get('IDENTIFICACION', None), 50))  # Convertir a str

            # Verificar si el registro ya existe
            cursor.execute(consulta_verificar, (identificacion,))
            existe = cursor.fetchone()

            if existe:
                print(f"Registro con identificacion {identificacion} ya existe, omitiendo.")
                continue

            # Preparar datos para insertar
            datos = {
                'apellido_paterno': truncar(fila.get('APELLIDO PATERNO', None), 80),
                'apellido_materno': truncar(fila.get('APELLIDO MATERNO', None), 80),
                'nombres': truncar(fila.get('NOMBRE(S)', None), 120),
                'identificacion': identificacion,  # Valor convertido a cadena
                'fecha_entrevista': convertir_fecha(fila.get('FECHA ENTREVISTA', None)),  # Convertir a fecha
                'telefono': truncar(fila.get('TELEFONO', None), 20),
                'perfil': truncar(fila.get('PERFIL', None), 120),
                'hv': truncar(fila.get('HV', None), 255),
                'area': None,  # Campo desplegable
                'subgrupo': None,  # Campo desplegable
                'rol': None,  # Campo desplegable
                'riesgo': None  # Campo desplegable
            }

            try:
                cursor.execute(consulta_insercion, datos)
                print("Registro insertado correctamente.")
            except Exception as e:
                print(f"Error al insertar registro: {e}")

conexion.close()
