from datetime import datetime
from UniAgendaPasta import db
from UniAgendaPasta import bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)
    agendamentos = db.relationship('Agendamento', backref='autor', lazy=True)

    def __init__(self, nome, email, senha) -> None:
        self.nome = nome
        self.email = email
        self.senha = bcrypt.generate_password_hash(senha).decode('utf-8')

    def checar_Senha(self, senha):
        return bcrypt.check_password_hash(self.senha, senha)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, nullable=False)
    laboratorio = db.Column(db.String(100), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
