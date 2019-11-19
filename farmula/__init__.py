from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'farmula'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:ahmed@12345@localhost/farmula"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from farmula import routes