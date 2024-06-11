from flask import render_template, flash, redirect, url_for, request, session, abort
from UniAgendaPasta import app, bcrypt
from UniAgendaPasta.models import User, predioslista, labslista, Agendamento
from UniAgendaPasta import db
from UniAgendaPasta.forms import FormLogin, FormCriarConta
from datetime import datetime
from flask_login import current_user, login_required

# Lista auxiliar para mapear nomes dos meses para números
meses_para_numero = {
    'Janeiro': '01',
    'Fevereiro': '02',
    'Março': '03',
    'Abril': '04',
    'Maio': '05',
    'Junho': '06',
    'Julho': '07',
    'Agosto': '08',
    'Setembro': '09',
    'Outubro': '10',
    'Novembro': '11',
    'Dezembro': '12'
}

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
        user = User.query.filter_by(email=email_usuario).first()
        if not user:
            return 'Usuário não encontrado', 404

        data_str = request.form.get('date')
        hora_inicio_str = request.form.get('startTime')
        hora_fim_str = request.form.get('endTime')
        predio = request.form.get('building')
        laboratorio = request.form.get('location')

        partes_data = data_str.split(' de ')
        dia = partes_data[0]
        mes = partes_data[1]
        ano = partes_data[2]

        mes_numero = meses_para_numero[mes]
        data_formatada = f'{ano}-{mes_numero}-{dia}'
        data = datetime.strptime(data_formatada, '%Y-%m-%d')

        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()

        # Verificar se há conflitos de horário
        agendamentos_dia = Agendamento.query.filter_by(data=data.date()).all()
        for agendamento in agendamentos_dia:
            agendamento_inicio = datetime.combine(data, agendamento.hora_inicio.time())
            agendamento_fim = datetime.combine(data, agendamento.hora_fim.time())
            novo_inicio = datetime.combine(data, hora_inicio)
            novo_fim = datetime.combine(data, hora_fim)
            if novo_inicio < agendamento_fim and novo_fim > agendamento_inicio:
                flash('O horário selecionado está indisponível.', 'error')
                return redirect('/')

        # Se não houver conflitos, prosseguir com o agendamento
        novo_agendamento = Agendamento(
            data=data,
            hora_inicio=datetime.combine(data, hora_inicio),
            hora_fim=datetime.combine(data, hora_fim),
            predio=predio,
            laboratorio=laboratorio,
            id_usuario=user.id
        )
        db.session.add(novo_agendamento)
        db.session.commit()

        flash('Agendamento realizado com sucesso!', 'success')
    except Exception as e:
        print(f"Erro ao agendar: {e}")
        flash('Erro ao agendar. Por favor, verifique os dados inseridos.', 'error')

    return redirect('/')

@app.route('/excluir/<int:agendamento_id>', methods=['POST'])
def excluir_agendamento(agendamento_id):
    if 'email' not in session:
        return redirect(url_for('login'))

    agendamento = Agendamento.query.get_or_404(agendamento_id)
    email_usuario = session['email']
    user = User.query.filter_by(email=email_usuario).first()

    if agendamento.id_usuario == user.id:
        db.session.delete(agendamento)
        db.session.commit()
        flash('Agendamento excluído com sucesso!', 'success')
        return redirect(url_for('homePage'))
    else:
        abort(403)


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

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def pagina_nao_existente(e):
    return render_template('404.html'), 404