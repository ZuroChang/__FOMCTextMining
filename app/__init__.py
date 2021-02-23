# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 15:08:41 2020

@author: ZuroChang
"""


from flask import Flask #,render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_login import LoginManager
# from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap=Bootstrap()
mail=Mail()
login_manager=LoginManager()
login_manager.login_view='authorization.login'
# moment=Moment()
db=SQLAlchemy()

def create_app(config_name='default'):
    app=Flask(__name__)
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    # moment.init_app(app)
    db.init_app(app)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .authorization import authorization as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/authorization')
    
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint,url_prefix='/api/v1')
    
    return app
    