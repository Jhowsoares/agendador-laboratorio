from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uniagenda.db'
app.config['SECRET_KEY'] = 'DonaFlorinda_AaaiChavinho_--save_foxtrot(e sim essa senha é assim para não acertarem)'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from UniAgendaPasta import routes
