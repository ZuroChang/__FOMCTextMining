# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 15:36:25 2020

@author: ZuroChang
"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db
from . import login_manager
from flask import url_for


Permission=[('ADMIN',1),('User',2)]
    
    

class Role(db.Model):
    __tablename__='roles'
    
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(3),unique=True,nullable=False)
    
    users=db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return(self.name)

class User(UserMixin,db.Model):
    __tablename__='users'
    
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True,index=True)
    email=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128),nullable=True)
    
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def verify_password(self,password):
        return(check_password_hash(self.password_hash,password))
    
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.name,
            'email':self.email,
            'pwd':self.password_hash,
            'role':self.role_id
        }
        return json_user
    
    def __repr__(self):
        return('<User %r>'%self.name)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))