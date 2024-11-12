from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import random
import string

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
    password_hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


# Función para generar una contraseña aleatoria
def generar_contraseña_aleatoria(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


# Inicialización de la base de datos y los usuarios con roles especificados
def inicializar_base_datos():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Definición de usuarios iniciales y nuevos usuarios
        usuarios = [
            {'username': 'admin', 'password': 'admin123', 'email': 'admin@ejemplo.com', 'role': 'superadmin'},
            {'username': 'user1', 'password': 'manager123', 'email': 'manager@ejemplo.com', 'role': 'administrador'},
            {'username': 'user2', 'password': 'editor123', 'email': 'editor@ejemplo.com', 'role': 'editor'},
            {'username': 'user3', 'password': 'viewer123', 'email': 'viewer@ejemplo.com', 'role': 'viewer'},
            {'username': 'danielcampos', 'password': generar_contraseña_aleatoria(), 'email': 'cdaniel_cj@hotmail.com',
             'role': 'superadmin'},
            {'username': 'karlamarin', 'password': generar_contraseña_aleatoria(),
             'email': 'alcalde.kennedy@gobiernobogota.gov.co', 'role': 'superadmin'},
            {'username': 'danielamaz', 'password': generar_contraseña_aleatoria(), 'email': 'dannymgsj@gmail.com',
             'role': 'administrador'},
            {'username': 'anacortes', 'password': generar_contraseña_aleatoria(),
             'email': 'ana.cortes@gobiernobogota.gov.co', 'role': 'editor'},
            {'username': 'elsaneira', 'password': generar_contraseña_aleatoria(),
             'email': 'elsa.neira@gobiernobogota.gov.co', 'role': 'editor'},
            {'username': 'carocesp', 'password': generar_contraseña_aleatoria(),
             'email': 'juliet.cespedes@gobiernobogota.gov.co', 'role': 'viewer'}
        ]

        # Insertar usuarios con contraseñas hasheadas
        for u in usuarios:
            if not Usuario.query.filter_by(username=u['username']).first():
                usuario = Usuario(username=u['username'], email=u['email'], role=u['role'])
                usuario.set_password(u['password'])
                db.session.add(usuario)
                print(
                    f"Usuario {u['username']} creado con contraseña: {u['password']}")  # Muestra las contraseñas generadas para referencia

        db.session.commit()
        print("Base de datos creada y usuarios iniciales agregados con roles especificados.")


if __name__ == '__main__':
    inicializar_base_datos()
