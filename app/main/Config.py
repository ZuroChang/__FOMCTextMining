# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 14:37:50 2020

@author: ZuroChang
"""
import os

class FolderPath:
    def __init__(self,Root=os.getcwd()+'/'):
        self.Root=os.getcwd()+'/'
        self.app=Root+'app/'
        self.static=self.app+"static/"
        
        self.CSS=self.static+"CSS/"
        self.JSON=self.static+"JSON/"
        self.PDF=self.static+"PDF/"
    