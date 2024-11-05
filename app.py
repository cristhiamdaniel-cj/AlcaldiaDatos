from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Ruta del archivo Excel en el sistema
EXCEL_FILE = "registro_personal.xlsx"

# Crear archivo Excel si no existe
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "No.", "NOMBRE COMPLETO", "IDENTIFICACION", "TELEFONO",
        "PERFIL", "HV", "AREA", "SUBGRUPO", "ROL",
        "FECHA ENTREVISTA", "ESTADO DEL PROCESO", "NOTAS", "TIPO DE MOVIMIENTO",
        "Fecha de vencimiento", "CDP", "CRP", "A CONTRATACION",
        "FECHA DE TERMINACIÓN CONTRATO", "FECHA DE INICIO", "FECHA DE TERMINACIÓN"
    ])
    df.to_excel(EXCEL_FILE, index=False)

def read_excel():
    """Función para leer el archivo Excel."""
    return pd.read_excel(EXCEL_FILE)

def save_excel(df):
    """Función para guardar cambios en el archivo Excel."""
    df.to_excel(EXCEL_FILE, index=False)

# Rutas CRUD

# Create: Ruta para mostrar el formulario y crear nuevos registros
@app.route("/", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        # Captura los datos del formulario
        data = {col: request.form[col] for col in read_excel().columns}

        # Leer el archivo Excel y agregar el nuevo registro
        df = read_excel()
        df = df.append(data, ignore_index=True)
        save_excel(df)

        return redirect(url_for("read"))
    return render_template("form.html")

# Read: Ruta para mostrar todos los registros
@app.route("/read")
def read():
    df = read_excel()

    # Verificamos si el DataFrame está vacío
    if df.empty:
        return render_template("read.html", data=None, message="No hay registros disponibles.")

    # Si hay datos, los convertimos en diccionario
    return render_template("read.html", data=df.to_dict(orient="records"))


# Update: Ruta para actualizar un registro existente
@app.route("/update/<int:index>", methods=["GET", "POST"])
def update(index):
    df = read_excel()
    if request.method == "POST":
        # Actualiza el registro en el índice específico
        for col in df.columns:
            df.at[index, col] = request.form[col]
        save_excel(df)
        return redirect(url_for("read"))

    # Obtener datos actuales del registro para mostrarlos en el formulario
    record = df.iloc[index].to_dict()
    return render_template("update.html", record=record, index=index)

# Delete: Ruta para eliminar un registro
@app.route("/delete/<int:index>", methods=["GET", "POST"])
def delete(index):
    df = read_excel()
    if request.method == "POST":
        # Eliminar el registro en el índice específico
        df = df.drop(index)
        save_excel(df)
        return redirect(url_for("read"))

    # Obtener datos del registro para confirmación de eliminación
    record = df.iloc[index].to_dict()
    return render_template("delete.html", record=record)

if __name__ == "__main__":
    app.run(debug=True)
