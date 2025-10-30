from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from datetime import datetime, date, time
import os
import logging
from functools import wraps

# ==================== CONFIGURAÇÃO DO FLASK ====================
app = Flask(__name__)

app.config['SECRET_KEY'] = '6b5b4fbee397e63a7b27d1558e37f975fb0c51bade653fcdc33d94304e306e5d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uniagenda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ==================== INICIALIZAR EXTENSÕES ====================
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# ==================== CONFIGURAÇÃO DE LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# ==================== DECORATORS PERSONALIZADOS ====================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acesso negado. Permissão de administrador necessária.', 'error')
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function

# ==================== MODELOS DE DADOS ====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modo = db.Column(db.Integer, nullable=False, default=0)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    agendamentos = db.relationship('Agendamento', backref='autor', lazy=True)

    def set_senha(self, senha):
        self.senha = bcrypt.generate_password_hash(senha).decode('utf-8')

    def verificar_senha(self, senha):
        return bcrypt.check_password_hash(self.senha, senha)

    def is_admin(self):
        return self.modo == 1

    def __repr__(self):
        return f'<User {self.email}>'

# Listas de prédios e laboratórios
predioslista = ['Sede', 'G5', 'Centro']
labslista = ['Sala 1', 'Sala 2', 'Sala 3', 'Sala 4', 'Sala 5', 
             'Lab 1', 'Lab 2', 'Lab 3', 'Lab 4', 'Lab 5']

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.String(5), nullable=False)
    hora_fim = db.Column(db.String(5), nullable=False)
    predio = db.Column(db.String(100), nullable=False)
    laboratorio = db.Column(db.String(100), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Agendamento {self.data} {self.hora_inicio}-{self.hora_fim}>'

# ==================== FUNÇÕES AUXILIARES ====================
def parse_custom_date(date_str):
    """Converte string no formato '15 de Junho de 2024' para objeto date"""
    meses = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    try:
        partes = date_str.split(' de ')
        if len(partes) == 3:
            dia = int(partes[0])
            mes_nome = partes[1].lower()
            ano = int(partes[2])
            mes = meses.get(mes_nome)
            if mes:
                return date(ano, mes, dia)
    except (ValueError, AttributeError):
        pass
    
    return None

def validar_agendamento(data, hora_inicio, hora_fim, predio, laboratorio, usuario_id=None, agendamento_id=None):
    """Validações completas para agendamento"""
    
    if data < date.today():
        return False, "Não é possível agendar para datas passadas"
    
    if data.weekday() >= 5:
        return False, "Agendamentos apenas em dias úteis"
    
    try:
        hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M')
        hora_fim_dt = datetime.strptime(hora_fim, '%H:%M')
        
        if hora_inicio_dt.time() < time(7, 0) or hora_fim_dt.time() > time(22, 0):
            return False, "Horário fora do expediente (7h às 22h)"
        
        diferenca = hora_fim_dt - hora_inicio_dt
        if diferenca.total_seconds() < 1800:
            return False, "Duração mínima de 30 minutos"
        
        if diferenca.total_seconds() > 21600:
            return False, "Duração máxima de 6 horas"
            
    except ValueError:
        return False, "Formato de horário inválido"
    
    conflito_query = Agendamento.query.filter_by(
        data=data,
        predio=predio,
        laboratorio=laboratorio
    ).filter(
        Agendamento.hora_inicio < hora_fim,
        Agendamento.hora_fim > hora_inicio
    )
    
    if agendamento_id:
        conflito_query = conflito_query.filter(Agendamento.id != agendamento_id)
    
    conflito = conflito_query.first()
    
    if conflito:
        return False, f"Já existe um agendamento neste horário: {conflito.hora_inicio} - {conflito.hora_fim}"
    
    if usuario_id:
        agendamentos_dia = Agendamento.query.filter_by(
            id_usuario=usuario_id,
            data=data
        ).count()
        
        if agendamentos_dia >= 3:
            return False, "Limite de 3 agendamentos por dia atingido"
    
    return True, "Agendamento válido"

def get_estatisticas_usuario(usuario_id):
    """Retorna estatísticas do usuário"""
    hoje = date.today()
    
    agendamentos_hoje = Agendamento.query.filter_by(
        id_usuario=usuario_id,
        data=hoje
    ).count()
    
    inicio_semana = hoje
    while inicio_semana.weekday() != 0:
        inicio_semana = date.fromordinal(inicio_semana.toordinal() - 1)
    
    fim_semana = date.fromordinal(inicio_semana.toordinal() + 6)
    
    agendamentos_semana = Agendamento.query.filter(
        Agendamento.id_usuario == usuario_id,
        Agendamento.data >= inicio_semana,
        Agendamento.data <= fim_semana
    ).count()
    
    from sqlalchemy import func
    sala_mais_usada = db.session.query(
        Agendamento.laboratorio,
        func.count(Agendamento.id).label('total')
    ).filter(
        Agendamento.id_usuario == usuario_id
    ).group_by(
        Agendamento.laboratorio
    ).order_by(
        func.count(Agendamento.id).desc()
    ).first()
    
    return {
        'hoje': agendamentos_hoje,
        'semana': agendamentos_semana,
        'sala_mais_usada': sala_mais_usada[0] if sala_mais_usada else 'Nenhuma',
        'total_agendamentos': Agendamento.query.filter_by(id_usuario=usuario_id).count()
    }

# ==================== ROTAS PRINCIPAIS ====================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('Por favor, preencha todos os campos', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.verificar_senha(senha):
            login_user(user)
            flash(f'Bem-vindo(a), {user.nome}!', 'success')
            
            if user.is_admin():
                return redirect('/admin')
            return redirect('/dashboard')
        else:
            flash('Email ou senha incorretos', 'error')
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        confirm_email = request.form.get('confirm-email', '').strip().lower()
        senha = request.form.get('senha', '')
        confirm_senha = request.form.get('confirm-senha', '')
        
        erros = []
        
        if not all([nome, email, confirm_email, senha, confirm_senha]):
            erros.append('Por favor, preencha todos os campos')
        
        if email != confirm_email:
            erros.append('Os emails não coincidem')
        
        if senha != confirm_senha:
            erros.append('As senhas não coincidem')
        
        if len(senha) < 6:
            erros.append('A senha deve ter pelo menos 6 caracteres')
        
        if User.query.filter_by(email=email).first():
            erros.append('Este email já está cadastrado')
        
        if erros:
            for erro in erros:
                flash(erro, 'error')
            return render_template('cadastro.html')
        
        try:
            novo_user = User(
                nome=nome,
                email=email,
                modo=0
            )
            novo_user.set_senha(senha)
            
            db.session.add(novo_user)
            db.session.commit()
            
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect('/login')
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')
    
    return render_template('cadastro.html')

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        hoje = date.today()
        agendamentos = Agendamento.query.filter_by(id_usuario=current_user.id)\
            .filter(Agendamento.data >= hoje)\
            .order_by(Agendamento.data, Agendamento.hora_inicio)\
            .all()
        
        estatisticas = get_estatisticas_usuario(current_user.id)
        
        return render_template('dashboard.html', 
                             agendamentos=agendamentos,
                             predios=predioslista,
                             labs=labslista,
                             estatisticas=estatisticas)
    except Exception as e:
        flash('Erro ao carregar agendamentos', 'error')
        return render_template('dashboard.html', 
                             agendamentos=[],
                             predios=predioslista,
                             labs=labslista,
                             estatisticas={'hoje': 0, 'semana': 0, 'sala_mais_usada': 'Nenhuma', 'total_agendamentos': 0})

@app.route('/perfil')
@login_required
def perfil():
    estatisticas = get_estatisticas_usuario(current_user.id)
    return render_template('perfil.html', estatisticas=estatisticas)

@app.route('/agendar', methods=['POST'])
@login_required
def agendar():
    try:
        data_str = request.form.get('date')
        start_time = request.form.get('startTime')
        end_time = request.form.get('endTime')
        predio = request.form.get('building')
        laboratorio = request.form.get('location')
        
        if not all([data_str, start_time, end_time, predio, laboratorio]):
            flash('Por favor, preencha todos os campos', 'error')
            return redirect('/dashboard')
        
        data = parse_custom_date(data_str)
        if not data:
            flash('Data inválida. Use o formato: "15 de Junho de 2024"', 'error')
            return redirect('/dashboard')
        
        valido, mensagem = validar_agendamento(data, start_time, end_time, predio, laboratorio, current_user.id)
        if not valido:
            flash(mensagem, 'error')
            return redirect('/dashboard')
        
        novo_agendamento = Agendamento(
            data=data,
            hora_inicio=start_time,
            hora_fim=end_time,
            predio=predio,
            laboratorio=laboratorio,
            id_usuario=current_user.id
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        flash('Agendamento realizado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao realizar agendamento', 'error')
    
    return redirect('/dashboard')

@app.route('/excluir_agendamento/<int:agendamento_id>', methods=['POST'])
@login_required
def excluir_agendamento(agendamento_id):
    try:
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        
        if agendamento.id_usuario != current_user.id and not current_user.is_admin():
            flash('Você não tem permissão para cancelar este agendamento', 'error')
            return redirect('/dashboard')
        
        db.session.delete(agendamento)
        db.session.commit()
        
        flash('Agendamento cancelado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao cancelar agendamento', 'error')
    
    if current_user.is_admin():
        return redirect('/admin')
    return redirect('/dashboard')

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    try:
        agendamentos = db.session.query(Agendamento, User)\
            .join(User)\
            .order_by(Agendamento.data.desc(), Agendamento.hora_inicio)\
            .all()
        
        total_usuarios = User.query.count()
        total_agendamentos = Agendamento.query.count()
        agendamentos_hoje = Agendamento.query.filter_by(data=date.today()).count()
        
        return render_template('admin.html', 
                             agendamentos=agendamentos,
                             total_usuarios=total_usuarios,
                             total_agendamentos=total_agendamentos,
                             agendamentos_hoje=agendamentos_hoje)
    except Exception as e:
        flash('Erro ao carregar agendamentos', 'error')
        return render_template('admin.html', agendamentos=[])

@app.route('/admin/excluir_agendamento/<int:agendamento_id>', methods=['POST'])
@login_required
@admin_required
def excluir_agendamento_admin(agendamento_id):
    try:
        agendamento = Agendamento.query.get_or_404(agendamento_id)
        
        db.session.delete(agendamento)
        db.session.commit()
        
        flash('Agendamento cancelado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao cancelar agendamento', 'error')
    
    return redirect('/admin')

@app.route('/admin/relatorios')
@login_required
@admin_required
def relatorios_admin():
    from sqlalchemy import func
    
    total_usuarios = User.query.count()
    total_agendamentos = Agendamento.query.count()
    agendamentos_hoje = Agendamento.query.filter_by(data=date.today()).count()
    
    salas_populares = db.session.query(
        Agendamento.laboratorio,
        func.count(Agendamento.id).label('total')
    ).group_by(Agendamento.laboratorio)\
     .order_by(func.count(Agendamento.id).desc())\
     .limit(5).all()
    
    usuarios_ativos = db.session.query(
        User.nome,
        func.count(Agendamento.id).label('total')
    ).join(Agendamento)\
     .group_by(User.id, User.nome)\
     .order_by(func.count(Agendamento.id).desc())\
     .limit(5).all()
    
    return render_template('relatorios.html',
                         total_usuarios=total_usuarios,
                         total_agendamentos=total_agendamentos,
                         agendamentos_hoje=agendamentos_hoje,
                         salas_populares=salas_populares,
                         usuarios_ativos=usuarios_ativos)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta', 'info')
    return redirect('/')

# ==================== EXECUÇÃO ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@unifecaf.com').first():
            admin = User(
                nome='Administrador',
                email='admin@unifecaf.com',
                modo=1
            )
            admin.set_senha('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin criado: admin@unifecaf.com / admin123')
    app.run(debug=True)