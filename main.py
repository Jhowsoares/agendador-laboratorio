from flask import Flask, url_for, render_template, redirect, request, session
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from forms import FormLogin, FormCriarConta

app = Flask(__name__)

app.config['SECRET_KEY'] = 'DonaFlorinda_AaaiChavinho_--save_foxtrot(e sim essa senha é assim para não acertarem)'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uniagenda.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)


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
    form_login = FormLogin()
    return render_template('login.html', form_login=form_login), 200


@app.route('/logar', methods=['POST'])
def logar():
    try:
        email = request.form.get('email')
        senha = request.form.get('senha')

        if not senha:
            raise ValueError("Senha n deve estar vazia")

        user = registros_professores.query.filter_by(email=email).first()

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
    formcriarconta = FormCriarConta()
    return render_template('cadastro.html', formcriarconta=formcriarconta), 200


@app.route('/cadastrar', methods=['POST'])
def cadastrar(url_for=url_for):
    try:
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        # print('debug 1')
        novo_usuario = registros_professores(nome, email, senha)
        # print('debug 2')
        db.session.add(novo_usuario)
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
    if not 'email' in session:
        print('debug 1mm')
        return 'tem que estar logado KRL!', 404
    from time import localtime
    data_atual = localtime()
    # ano_atual  = data_atual[0]
    # mes_atual  = data_atual[1]
    # dia_atual  = data_atual[2]
    # print(time.localtime())
    data_atualis = f'{data_atual[0]}-{data_atual[1]}-{data_atual[2]}'
    # print(ano_atual , mes_atual , dia_atual)
    cursor = bd.cursor()
    # print('debug 2')
    cursor.execute(
        f'SELECT lab , data FROM agendamentos WHERE email = "{session['email']}" AND data >= "{data_atualis}"')
    # print('debug 3')
    results1 = cursor.fetchall()
    resultados1 = [(lab, data.strftime('%Y-%m-%d')) for lab, data in results1]
    # print('debug 4')
    print(resultados1)
    cursor.execute(
        f'SELECT lab , data FROM agendamentos WHERE email != "{session['email']}" AND data >= "{data_atualis}"')
    # print('debug 5')
    results2 = cursor.fetchall()
    resultados2 = [(lab, data.strftime('%Y-%m-%d')) for lab, data in results2]
    # print(results1)
    cursor.close()
    return {'seus_agendamentos': resultados1, 'outros_agendamentos': resultados2}


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
    try:
        from time import localtime
        data_atual = localtime()
        data_atualis = f'{data_atual[0]}-{data_atual[1]}-{data_atual[2]}'
        cursor = bd.cursor()
        # agendamento = agendamentos(data=f'{dia}/{mes}/{ano}')
        cursor.execute(f'''SELECT lab , data FROM agendamentos2 WHERE lab = "{lab}" AND data = "{data}"''')
        bacana = cursor.fetchall()
        # bacana = [(lab, data.strftime('%Y-%m-%d')) for lab, data in bacana]
        if len(bacana) == 0:
            cursor.execute(
                f'''INSERT INTO agendamentos2 (email , lab , data) VALUES ("{session['email']}" , "{lab}" , "{data}")''')
            bd.commit()
        else:
            print('ja existe este lab e esta data la')
        cursor.close()
    except Exception as e:
        print(e)
    return 'não deixo pala'


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.errorhandler(404)
def pagina_nao_existente(e):
    return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True)