from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Ruta del archivo Excel en el sistema
EXCEL_FILE = "registro_personal.xlsx"

# Crear archivo Excel si no existe
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "APELLIDO PATERNO", "APELLIDO MATERNO", "NOMBRE(S)", "IDENTIFICACION",
        "FECHA ENTREVISTA", "TELEFONO", "PERFIL", "HV", "AREA", "SUBGRUPO",
        "ROL", "RIESGO"
    ])
    df.to_excel(EXCEL_FILE, index=False)

def read_excel():
    """Función para leer el archivo Excel."""
    return pd.read_excel(EXCEL_FILE)

def save_excel(df):
    """Función para guardar cambios en el archivo Excel."""
    df.to_excel(EXCEL_FILE, index=False)

# Ruta para mostrar el formulario y crear nuevos registros
@app.route("/", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        # Captura los datos del formulario y maneja campos opcionales
        data = {
            "APELLIDO PATERNO": request.form.get("APELLIDO PATERNO", ""),
            "APELLIDO MATERNO": request.form.get("APELLIDO MATERNO", ""),
            "NOMBRE(S)": request.form.get("NOMBRE(S)", ""),
            "IDENTIFICACION": request.form.get("IDENTIFICACION", ""),
            "FECHA ENTREVISTA": request.form.get("FECHA ENTREVISTA", ""),
            "TELEFONO": request.form.get("TELEFONO", ""),
            "PERFIL": request.form.get("PERFIL", ""),
            "HV": request.form.get("HV", ""),
            "AREA": request.form.get("AREA", ""),
            "SUBGRUPO": request.form.get("SUBGRUPO", ""),
            "ROL": request.form.get("ROL", ""),
            "RIESGO": request.form.get("RIESGO", "")
        }

        # Leer el archivo Excel y agregar el nuevo registro
        df = read_excel()
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        save_excel(df)

        return redirect(url_for("read"))
    return render_template("form.html")

# Ruta para mostrar todos los registros
@app.route("/read")
def read():
    df = read_excel()

    if df.empty:
        return render_template("read.html", data=None, message="No hay registros disponibles.")

    return render_template("read.html", data=df.to_dict(orient="records"))

# Ruta para actualizar un registro existente
@app.route("/update/<int:index>", methods=["GET", "POST"])
def update(index):
    df = read_excel()
    if request.method == "POST":
        for col in df.columns:
            df.at[index, col] = request.form.get(col, "")
        save_excel(df)
        return redirect(url_for("read"))

    record = df.iloc[index].to_dict()
    return render_template("update.html", record=record, index=index)

# Ruta para eliminar un registro
@app.route("/delete/<int:index>", methods=["GET", "POST"])
def delete(index):
    df = read_excel()
    if request.method == "POST":
        df = df.drop(index)
        save_excel(df)
        return redirect(url_for("read"))

    record = df.iloc[index].to_dict()
    return render_template("delete.html", record=record)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
