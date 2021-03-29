# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 16:28:00 2021

@author: ZuroChang
"""

from bs4 import BeautifulSoup as bs
import requests
from fake_useragent import UserAgent
import json
import re
import os
from Config import FolderPath

FP=FolderPath(os.path.dirname(os.path.dirname(os.getcwd()))+'/')
ua = UserAgent() #以防同一個header抓太多次

class CrawlerStatement:
    raw_data=[]
    def __init__(self,Date):
        self.Date=Date
        self.yyyy=Date[:4]
        self.mmdd=Date[4:]
    
    def __SetSoup(self):
        page = requests.get(self.url,headers={'User-Agent': ua.random})
        self.soup = bs(page.content, 'html.parser')
        
    def __SetFound(self):
        yyyy=int(self.yyyy)
        if yyyy<=2020 and yyyy>=2006:
            self.found = self.soup.findAll(class_='col-xs-12 col-sm-8 col-md-8')
        elif yyyy<=2005 and yyyy>=1996:
            self.found = self.soup.findAll('td')
        elif yyyy<=1995 and yyyy>=1994:
            self.found = self.soup.findAll('p')
    
    def __SetURL(self):
        yyyy=int(self.yyyy)
        if yyyy<=2020 and yyyy>=2006:
            self.url = 'https://www.federalreserve.gov/newsevents/pressreleases/monetary{yyyy}{mmdd}a.htm'.format(yyyy=self.yyyy,mmdd=self.mmdd)
        elif yyyy<=2005 and yyyy>=2003:
            self.url = 'https://www.federalreserve.gov/boarddocs/press/monetary/{yyyy}/{yyyy}{mmdd}'.format(yyyy=self.yyyy,mmdd=self.mmdd)
        elif yyyy<=2002 and yyyy>=1997:
            if yyyy==2002 and self.mmdd in ['0507','0626','0813','0924','1106','1210']:
                self.url = 'https://www.federalreserve.gov/boarddocs/press/monetary/{yyyy}/{yyyy}{mmdd}'.format(yyyy=self.yyyy,mmdd=self.mmdd)
            else:
                self.url = 'https://www.federalreserve.gov/boarddocs/press/general/{yyyy}/{yyyy}{mmdd}/'.format(yyyy=self.yyyy,mmdd=self.mmdd)
        elif yyyy==1996:
            self.url = 'https://www.federalreserve.gov/fomc/{yyyy}{mmdd}DEFAULT.htm'.format(yyyy=self.yyyy,mmdd=self.mmdd)
        elif yyyy<=1995 and yyyy>=1994:
            self.url = 'https://www.federalreserve.gov/fomc/{yyyy}{mmdd}default.htm'.format(yyyy=self.yyyy,mmdd=self.mmdd)
    
    def GetStatement(self):
        self.__SetURL()
        self.__SetSoup()
        self.__SetFound()
        try:
            for s in self.found:
                self.raw_data.append(s.text)
            return self.raw_data
        except:
            print('{} doesn"t have statement!'.format(self.Date))
            self.Error=self.Date
            return False


class ExtractFFRSentence:
    Empty={}
    Result={}
    def __init__(self):
        with open(FP.Parsed+'AllStatements.json', 'r') as f:
            self.file = json.load(f)
    
    def KeyPhrasesMatching(self):
        def CheckSentence(Sentence):
            KeyPhrases=['federal funds rate at','federal funds rate by',
                'federal funds rate to','federal funds rate in',
                'federal funds rate remains','federal funds rate of', 
                'target for the federal funds rate',
                'range for the federal funds rate at',
                'federal funds rate is expected to',
                'percent target range','discount rate'
            ]
            
            for phrase in KeyPhrases:
                if phrase in Sentence:
                    return(True)
            
            return(False)
        
        for name in self.file.keys():
            res={}
            empty=[]
            for entry in self.file[name]:
                Date=list(entry.keys())[0]
                res[Date]=[]
                for statement in entry.values():
                    for sentence in statement.split('.'):
                        if CheckSentence(sentence.lower()):
                            res[Date]=sentence
                            break
                if not res[Date]:empty.append(Date)
                        
            self.Result[name]=res
            self.Empty[name]=empty

    def Run(self):
        self.KeyPhrasesMatching()
        with open (FP.Parsed+'KeyStatementSentence.json','w') as f:
            json.dump(self.Result,f)


class ExtractFedFundRate:
    FFRCandidate={}
    FedFundRate={}
    
    def __init__(self):
        with open (FP.Parsed+'KeyStatementSentence.json','r') as f:
            self.file=json.load(f)

    def __SetFFRCandidate(self):
        FFRCandidate_date = {}
        for name in self.file:
        	self.FFRCandidate[name] = []
        	for date in self.file[name]:
        		FFRCandidate_date[date] = []
        		try:
        			for s in self.file[name][date].split():
        				if re.findall('[0-9]',s):
        					FFRCandidate_date[date].append(s)
        		except:pass
        	self.FFRCandidate[name].append(FFRCandidate_date)
        	FFRCandidate_date = {}
    
    def __SetFedFundRate(self):
        for Chairman in self.FFRCandidate:
            Content=self.FFRCandidate[Chairman][0]
            for date in Content:
                self.FedFundRate[str(date)] = []
                PossibleRates=Content[date]
                if len(PossibleRates) == 1:
                    PossibleRates[0] = PossibleRates[0].replace('-','+')
                    PossibleRates[0] = eval(PossibleRates[0])
                if len(PossibleRates) == 2: #1.11/2, 21/2問題, 2.內容錯誤譬如25,50,percentage
                    if PossibleRates[0] == '11/2':
                        PossibleRates[0] = '1-1/2'
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = PossibleRates[1].replace('-','+')
                        PossibleRates[1] = eval(PossibleRates[1])
                    elif PossibleRates[1] == '11/2':
                        PossibleRates[1] = '1-1/2'
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = PossibleRates[1].replace('-','+')
                        PossibleRates[1] = eval(PossibleRates[1])
                    elif PossibleRates[1] == '21/2':
                        PossibleRates[1] = '2-1/2'
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = PossibleRates[1].replace('-','+')
                        PossibleRates[1] = eval(PossibleRates[1])
                    elif date == '19970325':
                        PossibleRates.pop(0)
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                    elif date != '19970325' and eval(PossibleRates[0]) >= 15:
                        PossibleRates.pop(0)
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                    elif date == '19980929':
                        PossibleRates.pop(0)
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                    else:
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = PossibleRates[1].replace('-','+')
                        PossibleRates[1] = eval(PossibleRates[1])
                if len(PossibleRates) == 3: #可能會有奇怪的數字
                    if date == '20021106':
                        PossibleRates.pop(0)
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = eval(PossibleRates[1])
                        PossibleRates[0] += PossibleRates[1]
                        PossibleRates.pop(1)
                    elif date != '20021106' and eval(PossibleRates[0]) >= 10:
                        PossibleRates.pop(0)
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = PossibleRates[1].replace('-','+')
                        PossibleRates[1] = eval(PossibleRates[1])
                    elif date == '20200303':
                        PossibleRates.pop(0)
                        if PossibleRates[1] == '11/4':
                            PossibleRates[1] = '1-1/4'
                        PossibleRates[1] = PossibleRates[1].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = eval(PossibleRates[1])
                    else:
                        PossibleRates.pop(2)
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = eval(PossibleRates[1])
                if len(PossibleRates) == 4:
                    if date == '20200323' or date == '20191011': #有怪數字譬如年份
                        PossibleRates.pop(1)
                        PossibleRates.pop(0)
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = eval(PossibleRates[1])
                    elif date == '20200916': #包含失業率
                        PossibleRates.pop(-1)
                        PossibleRates.pop(-1)
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = eval(PossibleRates[1])
                    elif date == '19950201': #數字之間用空格表示所以要相加
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = eval(PossibleRates[1])
                        PossibleRates[2] = eval(PossibleRates[2])
                        PossibleRates[3] = eval(PossibleRates[3])
                        PossibleRates[0] = PossibleRates[0] + PossibleRates[1]
                        PossibleRates[1] = PossibleRates[2] + PossibleRates[3]
                        PossibleRates.pop()
                        PossibleRates.pop()
                    elif date[:4] == '2005' or date[:4] == '2004':
                        PossibleRates = [PossibleRates.pop(-1)]
                        PossibleRates[0] = PossibleRates[0].replace('-','+')
                        PossibleRates[0] = eval(PossibleRates[0])
                    else:
                        PossibleRates.pop()
                        PossibleRates.pop()
                        PossibleRates[0] = eval(PossibleRates[0])
                        PossibleRates[1] = eval(PossibleRates[1])
                self.FedFundRate[str(date)].append(PossibleRates)
    def Run(self):
        self.__SetFFRCandidate()
        self.__SetFedFundRate()
        
        with open(FP.Parsed+'FedFundRate.json', 'w') as f:
            json.dump(self.FedFundRate,f)
        


#StatementDate={
#    'Powell':{	
#    	'2020':['0129','0303','0315','0323','0429','0610','0729','0916'],
#    	'2019':['0130','0320','0501','0619','0731','0918','1011','1030','1211'],
#    	'2018':['0321','0502','0613','0801','0926','1108','1219']
#    },
#    'Yellen':{
#    	'2018':['0131'],
#    	'2017':['0201','0315','0503','0614','0726','0920','1101','1213'],
#    	'2016':['0127','0316','0427','0615','0727','0921','1102','1214'],
#    	'2015':['0128','0318','0429','0617','0729','0917','1028','1216'],
#    	'2014':['0319','0430','0618','0730','0917','1029','1217']
#    },
#    'Bernanke':{
#    	'2014':['0129'],
#    	'2013':['0130','0320','0501','0619','0731','0918','1030','1218'],
#    	'2012':['0125','0313','0425','0620','0801','0913','1024','1212'],
#    	'2011':['0126','0315','0427','0622','0809','0921','1102','1213'],
#    	'2010':['0127','0316','0428','0509','0623','0810','0921','1103','1214'],
#    	'2009':['0128','0318','0429','0624','0812','0923','1104','1216'],
#    	'2008':['0130','0318','0430','0625','0805','0916','1029','1216'],
#    	'2007':['0131','0321','0509','0618','0807','0918','1031','1211'],
#    	'2006':['0328','0510','0629','0808','0920','1025','1212']	
#    },
#    'Greenspan':{
#    	'2006':['0131'],
#    	'2005':['0202','0322','0503','0630','0809','0920','1101','1213'],
#    	'2004':['0128','0316','0504','0630','0810','0921','1110','1214'],
#    	'2003':['0129','0318','0506','0625','0812','0916','1028','1209'],
#    	'2002':['0130','0319','0507','0626','0813','0924','1106','1210'],
#    	'2001':['0103','0131','0320','0418','0515','0627','0821','0917','1002','1106','1211'],#0103, 0418, 0917,
#    	'2000':['0202','0321','0516','0628','0822','1003','1115','1219'],
#    	'1999':['0518','0630','0824','1005','1116','1221'],
#    	'1998':['0929','1015','1117'],#1015
#    	'1997':['0325'],
#    	'1996':['0131'],
#    	'1995':['0201'],
#    	'1994':['0204']
#    }
#}






