from flask import render_template, flash, redirect, url_for, request, session
from UniAgendaPasta import app, bcrypt
from UniAgendaPasta.models import User, predioslista, labslista
from UniAgendaPasta import db
from UniAgendaPasta.forms import FormLogin, FormCriarConta

@app.route('/')
def homePage(url_for=url_for):
    if 'email' in session:
        try:
            return render_template('home2.html', session=session['nome'], labs=labslista, predios=predioslista)
        except Exception as e:
            print(e)
            return render_template('home2.html', session=session['nome'], url_for=url_for, labs=labslista, predios=predioslista)
    else:
        return redirect('/login')

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
        if user and user.checar_Senha(senha):
            session['nome'] = user.nome
            session['email'] = user.email
            session['senha'] = user.senha

            return redirect('/')
        else:
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
