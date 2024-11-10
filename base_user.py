from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Configuración de la aplicación con PostgreSQL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:daniel@localhost/alcaldia_datos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definición de la tabla de usuarios
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)  # Cambiado a Text para mayor longitud
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

# Inicialización de la base de datos y los usuarios con nuevos roles
def inicializar_base_datos():
    with app.app_context():
        db.drop_all()  # Eliminar la tabla antes de recrearla para aplicar el cambio
        db.create_all()
        # Definición de usuarios con los roles especificados
        usuarios = [
            {'username': 'admin', 'password': 'admin123', 'email': 'admin@ejemplo.com', 'role': 'superadmin'},  # Acceso completo
            {'username': 'manager', 'password': 'manager123', 'email': 'manager@ejemplo.com', 'role': 'admin'},  # Todo menos eliminar
            {'username': 'editor', 'password': 'editor123', 'email': 'editor@ejemplo.com', 'role': 'editor'},    # Crear, ver y consultar
            {'username': 'viewer', 'password': 'viewer123', 'email': 'viewer@ejemplo.com', 'role': 'viewer'},    # Solo consulta
        ]

        # Insertar usuarios si no existen
        for u in usuarios:
            if not Usuario.query.filter_by(username=u['username']).first():
                usuario = Usuario(username=u['username'], email=u['email'], role=u['role'])
                usuario.password_hash = u['password']  # Guardar contraseña directamente como texto plano para pruebas
                db.session.add(usuario)

        db.session.commit()
        print("Base de datos creada y usuarios iniciales agregados con roles especificados.")

if __name__ == '__main__':
    inicializar_base_datos()
