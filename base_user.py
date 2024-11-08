from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Configuración de la aplicación con PostgreSQL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:tu_contrasena@localhost/alcaldia_datos'  # Cambia "tu_contrasena" por la contraseña de PostgreSQL
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

# Inicialización de la base de datos y los usuarios
def inicializar_base_datos():
    with app.app_context():
        db.drop_all()  # Eliminar la tabla antes de recrearla para aplicar el cambio
        db.create_all()
        usuarios = [
            {'username': 'admin', 'password': 'admin123', 'email': 'admin@ejemplo.com', 'role': 'admin'},
            {'username': 'user1', 'password': 'user123', 'email': 'user1@ejemplo.com', 'role': 'usuario'},
            {'username': 'user2', 'password': 'user123', 'email': 'user2@ejemplo.com', 'role': 'usuario'}
        ]

        for u in usuarios:
            if not Usuario.query.filter_by(username=u['username']).first():
                usuario = Usuario(username=u['username'], email=u['email'], role=u['role'])
                usuario.set_password(u['password'])
                db.session.add(usuario)

        db.session.commit()
        print("Base de datos creada y usuarios iniciales agregados.")

if __name__ == '__main__':
    inicializar_base_datos()
