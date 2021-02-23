# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 15:35:41 2020

@author: ZuroChang
"""

from flask import render_template
from flask_mail import Mail
from flask_mail import Message

class Email:
    def __init__(self,app,Subject='',
            Recipients=['zurochang@gmail.com'],
            Cc=['zurochang.milvus@gmail.com']):
        self.msg=Message(Subject,sender='abc@gmail.com',
            recipients=Recipients,cc=Cc)
        self.app=app
        self.mail=Mail()
        
    def Content(self,Body='',htmlFlag=False,**kwargs):
        if htmlFlag:
            self.msg.html=render_template(Body,**kwargs)
        else:
            self.msg.body=Body
           
    def AttachAttachment(self,SourceFolder,File):
        with self.app.open_resource(SourceFolder+File) as fp:
            self.msg.attach(filename=File,
                content_type='application/octet-stream',
                data=fp.read())
    
    def Send(self):
        self.mail.send(self.msg)

