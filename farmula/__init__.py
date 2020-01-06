from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'farmula'
socket_location = "/var/run/mysqld/mysqld.sock"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:ahmed@12345@localhost/farmula?unix_socket=" + socket_location
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:ahmed@12345@159.203.0.249/farmula"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from farmula import routes