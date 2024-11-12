from sqlalchemy import create_engine
import pandas as pd

# Crear una conexión a la base de datos usando SQLAlchemy
engine = create_engine('postgresql://postgres:daniel@localhost/alcaldia_datos')

# Consulta para obtener todos los datos de la tabla 'registro_personal'
query = "SELECT * FROM registro_personal"

# Leer los datos de la tabla en un DataFrame de pandas usando SQLAlchemy
df = pd.read_sql_query(query, engine)

# Generar estadísticas de los datos nulos
estadisticas_nulos = df.isnull().sum()

# Guardar las estadísticas en un archivo de texto
with open("estadisticas_nulos.txt", "w") as file:
    file.write("Estadísticas de campos nulos en la tabla 'registro_personal'\n")
    file.write("=" * 50 + "\n")
    for columna, cantidad_nulos in estadisticas_nulos.items():
        file.write(f"{columna}: {cantidad_nulos} nulos\n")

print("Estadísticas generadas y guardadas en 'estadisticas_nulos.txt'")
