from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'DonaFlorinda_AaaiChavinho_--save_foxtrot(e sim essa senha é assim para não acertarem)'

if os.getenv("DATABASE_URL"):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uniagenda.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from UniAgendaPasta import routes
