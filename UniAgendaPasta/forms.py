from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class FormCriarConta(FlaskForm):
    nome = StringField('Nome de Usuario', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    comfirmacao_email = StringField('Confirmação do E-mail', validators=[DataRequired(), Email(), EqualTo('email')])
    senha = PasswordField ('Senha', validators=[DataRequired(), Length(8,20)])
    comfirmacao_senha = PasswordField ('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botão_submit_criarconta = SubmitField('Criar Conta',)


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6,20)])
    manter_logado = BooleanField('Manter Logado')
    botão_submir_login = SubmitField('Entar')