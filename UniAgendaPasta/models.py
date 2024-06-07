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


predioslista = ['Sede', 'G5', 'Centro']
labslista = ['Sala 1', 'Sala 2', 'Sala 3', 'Sala 4', 'Sala 5', 'Lab 1', 'Lab 2', 'Lab 3', 'Lab 4', 'Lab 5']

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data= db.Column(db.DateTime, nullable=False)
    hora_inicio = db.Column(db.DateTime, nullable=False)
    hora_fim = db.Column(db.DateTime, nullable=False)
    predio = db.Column(db.String(100), nullable=False)
    laboratorio = db.Column(db.String(100), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
