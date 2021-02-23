# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 15:06:44 2020

@author: ZuroChang
"""


#import os
from app import create_app
# from app.models import User,Role
# from flask_migrate import Migrate

config_name='default'
app=create_app(config_name)


if __name__=='__main__':
    app.run()

    