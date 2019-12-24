from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'farmula'
socket_location = "/var/run/mysqld/mysqld.sock"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:ahmed@12345@localhost/farmula?unix_socket=" + socket_location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from farmula import routes