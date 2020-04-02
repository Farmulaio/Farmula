from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__, static_folder = 'static', template_folder='templates')
app.config['SECRET_KEY'] = 'farmula'
socket_location = "/var/run/mysqld/mysqld.sock"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/farmula"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:ahmed@12345@159.203.0.249/farmula"
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:ahmed@12345@134.209.177.113/farmula"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:ahmed@12345@localhost/farmula"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from farmula import routes