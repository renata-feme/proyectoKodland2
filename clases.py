
# tooodo para las bases de datos

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime # Para poder usar la fecha y hora

db = SQLAlchemy()

# Define la tabla para guardar los datos de cada usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True) # ID único para cada usuario
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    contrasena = db.Column(db.String(120), nullable=False)

    # Relación: Le dice a SQLAlchemy que un Usuario puede tener muchos Consumos.
    consumos = db.relationship('Consumo', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

# Define la tabla para los resultados de cada cuestionario
class Consumo(db.Model):
    __tablename__ = 'consumo'
    id = db.Column(db.Integer, primary_key=True) # ID único para cada registro

    # Llave foránea: Conecta este consumo con un usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Guarda la fecha y hora local del sistema
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    # Columnas para guardar las respuestas
    agua = db.Column(db.Float, default=0)
    luz = db.Column(db.Float, default=0)
    gasolina = db.Column(db.Float, default=0)
    bano = db.Column(db.Float, default=0)
    aguaEmbot = db.Column(db.Float, default=0)
    reciclaje = db.Column(db.Integer, default=0)
    ropa = db.Column(db.Integer, default=0)
    consumoLocal = db.Column(db.Integer, default=0)
    puntaje = db.Column(db.Float, default=0)

    def __repr__(self):
        return f'<Consumo {self.id} de Usuario {self.usuario_id}>'
