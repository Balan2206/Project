from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

class User(db.Model,UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150), nullable=False)
