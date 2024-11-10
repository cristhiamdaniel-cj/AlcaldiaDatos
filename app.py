import time
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os

# Configuración inicial de la aplicación Flask y base de datos
app = Flask(__name__)
app.secret_key = 'una_clave_secreta_para_sesiones'

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:daniel@localhost/alcaldia_datos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de datos para usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Decorador para verificar autenticación y permisos específicos de rol
def login_required(roles=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash("Por favor, inicia sesión.", "danger")
                print("Usuario no autenticado, redirigiendo a login")
                return redirect(url_for('login'))
            if roles and session.get('user_role') not in roles:
                flash("No tienes permiso para acceder a esta página.", "danger")
                print(f"Usuario autenticado pero sin permisos adecuados, redirigiendo a home")
                return redirect(url_for('home'))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

# Ruta principal que redirige al login o al menú
@app.route('/')
def index():
    if 'user_id' not in session:
        print("Redirigiendo a login desde index()")
        return redirect(url_for('login'))
    print("Usuario autenticado, redirigiendo a home desde index()")
    return redirect(url_for('home'))

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()  # Limpiar cualquier sesión previa al intentar iniciar sesión
    print("Sesión previa limpiada")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id
            session['user_role'] = usuario.role
            print(f"Inicio de sesión exitoso para el usuario: {username} con rol: {usuario.role}")
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('home'))
        else:
            print(f"Falló el inicio de sesión para el usuario: {username}")
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

# Ruta para el menú principal
@app.route('/home')
@login_required()
def home():
    print("Mostrando el menú principal para el usuario autenticado")
    return render_template('home.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    print("Sesión cerrada")
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

# Ruta para ver registros (accesible para viewer, editor, administrador, y superadmin)
@app.route('/ver_registros')
@login_required(roles=["viewer", "editor", "administrador", "superadmin"])
def ver_registros():
    count = request.args.get('count', '10')
    query = "SELECT * FROM registro_personal" if count == 'all' else f"SELECT * FROM registro_personal LIMIT {count}"

    conexion = psycopg2.connect(
        host="localhost",
        database="alcaldia_datos",
        user="postgres",
        password="daniel"
    )
    cursor = conexion.cursor()
    cursor.execute(query)
    registros = cursor.fetchall()
    conexion.close()

    return render_template('ver_registros.html', registros=registros, count=count)

# Ruta para consultar un registro por identificación (accesible para viewer, editor, administrador, y superadmin)
@app.route('/consultar', methods=['GET', 'POST'])
@login_required(roles=["viewer", "editor", "administrador", "superadmin"])
def consultar_registro():
    registro = None
    if request.method == 'POST':
        identificacion = request.form['identificacion']
        conexion = psycopg2.connect(
            host="localhost",
            database="alcaldia_datos",
            user="postgres",
            password="daniel"
        )
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM registro_personal WHERE identificacion = %s", (identificacion,))
        registro = cursor.fetchone()
        conexion.close()

        if not registro:
            flash('No se encontró ningún registro con esa identificación', 'warning')

    return render_template('consultar.html', registro=registro)

# Ruta para crear un nuevo registro (accesible para editor, administrador, y superadmin)
@app.route('/crear', methods=['GET', 'POST'])
@login_required(roles=["editor", "administrador", "superadmin"])
def crear_registro():
    if request.method == 'POST':
        # Extraer los datos del formulario
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        nombres = request.form['nombres']
        identificacion = request.form['identificacion']
        fecha_entrevista = request.form.get('fecha_entrevista') or None
        telefono = request.form['telefono']
        perfil = request.form['perfil']
        hv = request.form['hv']
        area = request.form['area']
        subgrupo = request.form['subgrupo']
        rol = request.form['rol']
        riesgo = request.form['riesgo']

        try:
            # Conectar a la base de datos
            conexion = psycopg2.connect(
                host="localhost",
                database="alcaldia_datos",
                user="postgres",
                password="daniel"
            )
            cursor = conexion.cursor()
            consulta = """
            INSERT INTO registro_personal (apellido_paterno, apellido_materno, nombres, identificacion, fecha_entrevista, telefono, perfil, hv, area, subgrupo, rol, riesgo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(consulta, (apellido_paterno, apellido_materno, nombres, identificacion, fecha_entrevista, telefono, perfil, hv, area, subgrupo, rol, riesgo))
            conexion.commit()
            conexion.close()
            return jsonify(success=True)  # Respuesta JSON para éxito
        except Exception as e:
            print("Error al crear registro:", e)
            return jsonify(success=False), 500  # Respuesta JSON para error

    return render_template('crear.html')


# Ruta para actualizar un registro (accesible para administrador y superadmin)
@app.route('/actualizar', methods=['GET', 'POST'])
@login_required(roles=["administrador", "superadmin"])
def actualizar_registro():
    if request.method == 'POST':
        identificacion = request.form['identificacion']
        campo = request.form['campo']
        nuevo_valor = request.form['nuevo_valor']

        conexion = psycopg2.connect(
            host="localhost",
            database="alcaldia_datos",
            user="postgres",
            password="daniel"
        )
        cursor = conexion.cursor()
        consulta = f"UPDATE registro_personal SET {campo} = %s WHERE identificacion = %s"
        cursor.execute(consulta, (nuevo_valor, identificacion))
        conexion.commit()
        conexion.close()

        flash('Registro actualizado exitosamente', 'success')
        return redirect(url_for('ver_registros'))
    return render_template('actualizar.html')

# Ruta para eliminar un registro (solo accesible para superadmin)
@app.route('/eliminar', methods=['GET', 'POST'])
@login_required(roles=["superadmin"])
def eliminar_registro():
    if request.method == 'POST':
        identificacion = request.form['identificacion']

        conexion = psycopg2.connect(
            host="localhost",
            database="alcaldia_datos",
            user="postgres",
            password="daniel"
        )
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM registro_personal WHERE identificacion = %s", (identificacion,))
        conexion.commit()
        conexion.close()

        flash('Registro eliminado exitosamente', 'success')
        return redirect(url_for('ver_registros'))

    return render_template('eliminar.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
