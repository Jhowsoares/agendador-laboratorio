from flask import render_template, flash, redirect, url_for, request, session
from UniAgendaPasta import app, bcrypt
from UniAgendaPasta.models import User
from UniAgendaPasta import db

@app.route('/')
def homePage(url_for=url_for):
    print('etapa zer0')
    # print(session)
    print('etapa 1')
    # print(request.remote_addr)

    if 'email' in session:
        print('etapa 2')
        try:
            # cursor = bd.cursor()
            # print(session['email'])
            # cursor.execute(f'SELECT * FROM agendamentos where email = "{session['email']}"')
            # agendamentos = cursor.fetchall()
            # print(agendamentos)

            return render_template('home2.html', session=session['nome'])
        except Exception as e:
            print(e)
            return render_template('home2.html', session=session['nome'], url_for=url_for)

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
            raise ValueError("Senha n deve estar vazia")

        User = User.query.filter_by(email=email).first()
        print('log')
        a = User.query.all()
        for c in a:
            print(c)
        if User and User.checar_Senha(senha):
            session['nome'] = User.nome
            session['email'] = User.email
            session['senha'] = User.senha

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
        # print('debug 1')
        novo_User = User(nome, email, senha)
        # print('debug 2')
        db.session.add(novo_User)
        # print('debug 3')
        db.session.commit()
        # print('debug 4')

        # cursor = db.cursor()
        # cursor.execute(f'''INSERT INTO registros_professores (nome , email , senha) VALUES ('{nome}' , '{email}' , '{senha}')''')
        # db.commit()
        # cursor.close()
    except Exception as e:
        return f'erro ao criar a conta. email pode ja ter sido utilizado antes: {e}'
    # return f'ai sim porra <a href = {url_for('login')}> pagina de login </a>' , 200
    return render_template('home_redirect.html')


# @app.route('/registros')
# def ver_Registros():
#     cursor = db.cursor()

#     cursor.execute(f'''SELECT * FROM registros_professores''')
#     resultados = cursor.fetchall()
#     cursor.close()

#     return resultados , 200

@app.route('/registros', methods=['POST'])
def registros():
    return


@app.route('/enviar', methods=['GET', 'POST'])
def enviar():
    if request.method == 'GET':
        return redirect('/')

    # dia   = request.json['dia']
    # mes   = request.json['mes']
    # ano   = request.json['ano']

    lab = request.json['lab']
    data = request.json['data']

    print(request.json)

    # email = session['email']

    # print(f'{dia}/{mes}/{ano}')
    print(data)
    return 'não deixo pala'


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.errorhandler(404)
def pagina_nao_existente(e):
    return render_template('404.html')