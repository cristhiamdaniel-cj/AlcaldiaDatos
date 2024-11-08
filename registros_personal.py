import pandas as pd
from sqlalchemy import create_engine, Table, MetaData, insert, exc
import pymysql

# Configuración de la conexión a la base de datos
db_user = "dev_user"
db_password = "1234"
db_host = "localhost"
db_name = "alcaldia_datos"

# Crear la conexión con SQLAlchemy
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
connection = engine.connect()

# Leer el archivo de Excel
file_path = "registro_personal.xlsx"
df = pd.read_excel(file_path)

# Seleccionar columnas específicas y renombrarlas según la tabla en la base de datos
df = df[['APELLIDO PATERNO', 'APELLIDO MATERNO', 'NOMBRE(S)', 'IDENTIFICACION',
         'FECHA ENTREVISTA', 'TELEFONO', 'PERFIL', 'HV', 'AREA', 'SUBGRUPO', 'ROL', 'RIESGO']]
df.columns = ['apellido_paterno', 'apellido_materno', 'nombres', 'identificacion',
              'fecha_entrevista', 'telefono', 'perfil', 'hv', 'area', 'subgrupo', 'rol', 'riesgo']

# Reemplazar valores vacíos con None (nulos)
df = df.where(pd.notnull(df), None)

# Preparar metadatos de SQLAlchemy para la tabla
metadata = MetaData()
metadata.reflect(bind=engine)
registro_personal = Table('registro_personal', metadata, autoload_with=engine)

# Insertar registros en la base de datos
try:
    with engine.begin() as conn:
        for _, row in df.iterrows():
            insert_stmt = insert(registro_personal).values(**row.to_dict())
            conn.execute(insert_stmt)
    print("Datos insertados correctamente en la tabla 'registro_personal'.")
except exc.SQLAlchemyError as e:
    print(f"Error al insertar datos: {e}")

# Cerrar la conexión
connection.close()
