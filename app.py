from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'una_clave_secreta_para_sesiones'

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/alcaldia_datos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de datos para usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Ruta principal que redirige al login o al menú
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

# Ruta para el menú principal
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

# Ruta para ver registros
@app.route('/ver_registros')
def ver_registros():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    count = request.args.get('count', '10')
    if count == 'all':
        query = "SELECT * FROM registro_personal"
    else:
        query = f"SELECT * FROM registro_personal LIMIT {count}"

    conexion = psycopg2.connect(
        host="localhost",
        database="alcaldia_datos",
        user="postgres",
        password="1234"
    )
    cursor = conexion.cursor()
    cursor.execute(query)
    registros = cursor.fetchall()
    conexion.close()

    return render_template('ver_registros.html', registros=registros, count=count)

# Ruta para consultar un registro por identificación
@app.route('/consultar', methods=['GET', 'POST'])
def consultar_registro():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    registro = None
    if request.method == 'POST':
        identificacion = request.form['identificacion']
        conexion = psycopg2.connect(
            host="localhost",
            database="alcaldia_datos",
            user="postgres",
            password="1234"
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM registro_personal WHERE identificacion = %s", (identificacion,))
        registro = cursor.fetchone()
        conexion.close()

        if not registro:
            flash('No se encontró ningún registro con esa identificación', 'warning')

    return render_template('consultar.html', registro=registro)

# Ruta para actualizar un registro
@app.route('/actualizar', methods=['GET', 'POST'])
def actualizar_registro():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        identificacion = request.form['identificacion']
        campo = request.form['campo']
        nuevo_valor = request.form['nuevo_valor']

        conexion = psycopg2.connect(
            host="localhost",
            database="alcaldia_datos",
            user="postgres",
            password="1234"
        )
        cursor = conexion.cursor()
        consulta = f"UPDATE registro_personal SET {campo} = %s WHERE identificacion = %s"
        cursor.execute(consulta, (nuevo_valor, identificacion))
        conexion.commit()
        conexion.close()

        flash('Registro actualizado exitosamente', 'success')
        return redirect(url_for('ver_registros'))

    return render_template('actualizar.html')

# Ruta para eliminar un registro
@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar_registro():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        identificacion = request.form['identificacion']

        conexion = psycopg2.connect(
            host="localhost",
            database="alcaldia_datos",
            user="postgres",
            password="1234"
        )
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM registro_personal WHERE identificacion = %s", (identificacion,))
        conexion.commit()
        conexion.close()

        flash('Registro eliminado exitosamente', 'success')
        return redirect(url_for('ver_registros'))

    return render_template('eliminar.html')

# Ruta para crear un nuevo registro
@app.route('/crear', methods=['GET', 'POST'])
def crear_registro():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        nombres = request.form['nombres']
        identificacion = request.form['identificacion']
        fecha_entrevista = request.form.get('fecha_entrevista') or None
        telefono = request.form['telefono']
        perfil = request.form['perfil']
        hv = request.form['hv']

        conexion = psycopg2.connect(
            host="localhost",
            database="alcaldia_datos",
            user="postgres",
            password="1234"
        )
        cursor = conexion.cursor()
        consulta = """
        INSERT INTO registro_personal (apellido_paterno, apellido_materno, nombres, identificacion, fecha_entrevista, telefono, perfil, hv)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(consulta, (apellido_paterno, apellido_materno, nombres, identificacion, fecha_entrevista, telefono, perfil, hv))
        conexion.commit()
        conexion.close()

        flash('Registro creado exitosamente', 'success')
        return redirect(url_for('ver_registros'))

    return render_template('crear.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
