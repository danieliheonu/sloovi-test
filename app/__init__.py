import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://danieliheonu:QjWwd3n38hErGIMw@cluster0.nl5pe.mongodb.net/sloovi"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

from app import routes