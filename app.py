from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

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

def login_required(roles=None):
    """
    Decorador para requerir autenticación y roles específicos para acceder a una ruta.
    :param roles: Lista de roles permitidos para acceder a la ruta
    :return: Función de envoltura para verificar la autenticación y los roles
    """
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


@app.route('/')
def index():
    """
    Ruta principal que redirige al login si no hay una sesión activa, o al menú principal si el usuario
    ya está autenticado.
    :return: Redirección a la página de inicio de sesión o al menú principal
    """
    if 'user_id' not in session:
        print("Redirigiendo a login desde index()")
        return redirect(url_for('login'))
    print("Usuario autenticado, redirigiendo a home desde index()")
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta para iniciar sesión en la aplicación.
    :return: Página de inicio de sesión o redirección al menú principal si la autenticación es exitosa
    """
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


@app.route('/home')
@login_required()
def home():
    """
    Ruta para mostrar el menú principal para el usuario autenticado.
    :return: Página de inicio con el menú principal
    """
    print("Mostrando el menú principal para el usuario autenticado")
    return render_template('home.html')


@app.route('/logout')
def logout():
    """
    Ruta para cerrar la sesión del usuario y redirigir al inicio de sesión.
    :return: Redirección a la página de inicio de sesión
    """
    session.clear()
    print("Sesión cerrada")
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))


@app.route('/ver_registros')
@login_required(roles=["viewer", "editor", "administrador", "superadmin"])
def ver_registros():
    """
    Ruta para ver los registros de personal almacenados en la base de datos.
    :return: Página con la lista de registros de personal
    """
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


@app.route('/consultar', methods=['GET', 'POST'])
@login_required(roles=["viewer", "editor", "administrador", "superadmin"])
def consultar_registro():
    """
    Ruta para consultar un registro de personal por su identificación.
    :return: Página para consultar un registro o respuesta JSON con el registro encontrado
    """
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

        if registro:
            columnas = ["id", "apellido_paterno", "apellido_materno", "nombres", "identificacion",
                        "fecha_entrevista", "telefono", "perfil", "hv", "area", "subgrupo", "rol", "riesgo"]
            registro_dict = dict(zip(columnas, registro))
            return jsonify({"success": True, "registro": registro_dict})
        else:
            return jsonify({"success": False, "message": "No se encontró ningún registro con esa identificación"}), 404

    return render_template('consultar.html')


@app.route('/crear', methods=['GET', 'POST'])
@login_required(roles=["editor", "administrador", "superadmin"])
def crear_registro():
    """
    Ruta para crear un nuevo registro de personal en la base de datos.
    :return: Página para crear un registro o respuesta JSON con el resultado de la operación
    """
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
            INSERT INTO registro_personal (apellido_paterno, apellido_materno, nombres, identificacion, 
            fecha_entrevista, telefono, perfil, hv, area, subgrupo, rol, riesgo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(consulta, (apellido_paterno, apellido_materno, nombres, identificacion,
                                      fecha_entrevista, telefono, perfil, hv, area, subgrupo, rol, riesgo))
            conexion.commit()
            conexion.close()
            return jsonify(success=True)  # Respuesta JSON para éxito
        except Exception as e:
            print("Error al crear registro:", e)
            return jsonify(success=False), 500  # Respuesta JSON para error

    return render_template('crear.html')


@app.route('/actualizar', methods=['GET', 'POST'])
@login_required(roles=["administrador", "superadmin"])
def actualizar_registro():
    """
    Ruta para actualizar un registro de personal en la base de datos.
    :return: Página para actualizar un registro o respuesta JSON con el resultado de la operación
    """
    if request.method == 'POST':
        identificacion = request.form['identificacion']
        campo = request.form['campo']
        nuevo_valor = request.form['nuevo_valor']

        try:
            # Conexión a la base de datos
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

            # Enviar respuesta JSON de éxito
            return jsonify({"success": True, "message": "Registro actualizado exitosamente."})
        except Exception as e:
            print("Error al actualizar registro:", e)
            return jsonify({"success": False, "message": "Ocurrió un error al actualizar el registro."}), 500

    return render_template('actualizar.html')


@app.route('/eliminar', methods=['GET', 'POST'])
@login_required(roles=["superadmin"])
def eliminar_registro():
    """
    Ruta para eliminar un registro de personal en la base de datos.
    :return: Página para eliminar un registro o respuesta JSON con el resultado de la operación
    """
    if request.method == 'POST':
        identificacion = request.form['identificacion']

        # Conectar a la base de datos
        conexion = psycopg2.connect(
            host="localhost",
            database="alcaldia_datos",
            user="postgres",
            password="daniel"
        )
        cursor = conexion.cursor()
        # Buscar el registro para confirmar su existencia antes de eliminarlo
        cursor.execute("SELECT apellido_paterno, apellido_materno, nombres FROM registro_personal "
                       "WHERE identificacion = %s", (identificacion,))
        registro = cursor.fetchone()

        if not registro:
            # Si no se encuentra el registro, devolver un mensaje de error
            conexion.close()
            return jsonify({"success": False, "message": "No se encontró ningún registro con esa identificación"}), 404

        # Eliminar el registro si existe
        cursor.execute("DELETE FROM registro_personal WHERE identificacion = %s", (identificacion,))
        conexion.commit()
        conexion.close()

        nombre_completo = f"{registro[0]} {registro[1]} {registro[2]}"
        return jsonify({"success": True, "message": f"Registro de {nombre_completo} eliminado exitosamente."})

    # Renderizar el formulario de eliminación en la solicitud GET
    return render_template('eliminar.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
