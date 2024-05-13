from main import database
from datetime import datetime

class Usuario(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    agendamentos = database.relationship('Agendamento', backref='autor', lazy=True)

class Agendamento(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    data_hora = database.Column(database.DateTime, nullable=False)
    laboratorio = database.Column(database.String, nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)