from flask import render_template, flash, redirect, url_for, request, session
from UniAgendaPasta import app, bcrypt
from UniAgendaPasta.models import User, predioslista, labslista, Agendamento
from UniAgendaPasta import db
from UniAgendaPasta.forms import FormLogin, FormCriarConta
from datetime import datetime

def buscar_agendamentos_usuario(usuario_id):
    try:
        agendamentos = Agendamento.query.filter_by(id_usuario=usuario_id).all()
        return agendamentos
    except Exception as e:
        print(e)
        return []
@app.route('/')
def homePage():
    if 'email' in session:
        try:
            email_usuario = session['email']
            user = User.query.filter_by(email=email_usuario).first()
            if user:
                agendamentos = buscar_agendamentos_usuario(user.id)
            else:
                agendamentos = []

            return render_template('home2.html', session=user.nome, labs=labslista, predios=predioslista, agendamentos=agendamentos)
        except Exception as e:
            print(e)
            return render_template('home2.html', session=session['nome'], labs=labslista, predios=predioslista, agendamentos=[])
    else:
        return redirect('/login')

@app.route('/agendar', methods=['POST'])
def agendar():
    if 'email' not in session:
        return redirect('/login')

    try:
        email_usuario = session['email']
        print(f"Email do usuário na sessão: {email_usuario}")  # Linha de debug

        user = User.query.filter_by(email=email_usuario).first()
        if user:
            print(f"Usuário encontrado: {user.nome}, {user.email}")  # Linha de debug
        if not user:
            print("Usuário não encontrado")  # Linha de debug
            return 'Usuário não encontrado', 404

        data_str = request.form.get('date')
        hora_inicio_str = request.form.get('start_time')
        hora_fim_str = request.form.get('end_time')
        predio = request.form.get('building')
        laboratorio = request.form.get('location')

        # Converta strings para objetos datetime
        data = datetime.strptime(data_str, '%Y-%m-%d')
        hora_inicio = datetime.strptime(f"{data_str} {hora_inicio_str}", '%Y-%m-%d %H:%M')
        hora_fim = datetime.strptime(f"{data_str} {hora_fim_str}", '%Y-%m-%d %H:%M')

        novo_agendamento = Agendamento(data=data, hora_inicio=hora_inicio, hora_fim=hora_fim, predio=predio, laboratorio=laboratorio, id_usuario=user.id)

        db.session.add(novo_agendamento)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao agendar: {e}")  # Linha de debug
        return f'Erro ao agendar: {e}'

    return redirect('/')

@app.route('/login')
def login(url_for=url_for):
    return render_template('login.html'), 200


@app.route('/logar', methods=['POST'])
def logar():
    try:
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not senha:
            raise ValueError("Senha não deve estar vazia")

        user = User.query.filter_by(email=email).first()
        if user:
            print(f"Usuário encontrado: {user.nome}, {user.email}")  # Linha de debug
        if user and user.checar_Senha(senha):
            session['nome'] = user.nome
            session['email'] = user.email
            session['senha'] = user.senha
            return redirect('/')
        else:
            print("Usuário não encontrado ou senha incorreta")  # Linha de debug
            return redirect('/login')
    except Exception as e:
        print(e)
        return render_template('login_redirect.html')


@app.route('/cadastro')
def cadastro(url_for=url_for):
    return render_template('cadastro.html'), 200

@app.route('/cadastrar', methods=['POST'])
def cadastrar(url_for=url_for):
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        novo_user = User(nome, email, senha)
        db.session.add(novo_user)
        db.session.commit()
    except Exception as e:
        return f'Erro ao criar a conta. Email pode já ter sido utilizado antes: {e}'
    return render_template('home_redirect.html')

@app.route('/registros', methods=['POST'])
def registros():
    return

@app.route('/enviar', methods=['GET', 'POST'])
def enviar():
    if request.method == 'GET':
        return redirect('/')

    lab = request.json['lab']
    data = request.json['data']

    print(request.json)
    print(data)
    return 'não deixo pala'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def pagina_nao_existente(e):
    return render_template('404.html')
