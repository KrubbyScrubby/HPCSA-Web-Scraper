# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 22:37:28 2023

@author: halke
"""
import requests
import sys
import re
from lxml import html
from bs4 import BeautifulSoup
import pandas


class Member:
    def __init__(self, code):
        try: 
           #Takes inputted code and formats it to be 0-9 values only
           self.code=code[2:].replace(' ', '')
           self.prefix = code[:2]
           test = int(self.code)
           #Checks to confirm resultant value is 7 characters long, else stop program
           if len(str(self.code)) !=7  :
               raise ValueError('Invalid Code Entered')
        except ValueError:
            sys.exit('Invalid Code Entered')

    def grab_html(self):
        try:
            code = self.code
            prefix = self.prefix
            #Grabs the html from the HPCSA registry website
            self.check = requests.get(f"https://hpcsaonline.custhelp.com/app/iregister_details/reg_number/{prefix}%20%20%20{code}")
            
        except requests.RequestException:
            print("Request Failure")
            
        
            
    def commit_to_dic(self):   
        code = self.code
        check = self.check

        finder = BeautifulSoup(check.content, 'html.parser')
        profile_dic = {}
                
        profile = html.fromstring(check.content)
        city = profile.xpath('//*[@id="CITY"]/text()')
        name = profile.xpath('//*[@id="NAME"]/text()')
        province = profile.xpath('//*[@id="PROVINCE"]/text()')
        postcode = profile.xpath('//*[@id="POSTCODE"]/text()')
        
        try:
            qualification = re.search(r'OBTAINED([a-zA-Z\(\)]+)', finder.get_text().replace('\t', '').replace('\n', '').partition(code)[2])
            qualdate = re.search(r'([0-9]{2} [A-Za-z]{3} [0-9]{4})', finder.get_text().replace('\t', '').replace('\n', '').partition(qualification.groups()[0])[2])
            qualification2 = re.search(r' [0-9]{4} ([a-zA-Z\(\)]+)', finder.get_text().replace('\t', '').replace('\n', ''))
            qualdate2 = re.search(r'([0-9]{2} [A-Za-z]{3} [0-9]{4})', finder.get_text().replace('\t', '').replace('\n', '').partition(qualification2.groups()[0])[2])

            
        except:
            pass

        try:
            profile_dic['dp_code'] = f"DP{code}"
            profile_dic["name"] = name[0].removeprefix('\n\t\t\t').removesuffix('\t\t').title()
            profile_dic["city"] = city[0].title()
            profile_dic["province"] = province[0].title()
            profile_dic["postcode"] = postcode[0]
            profile_dic["qual"] = qualification.groups()[0]
            profile_dic["qualdate"] = qualdate.groups()[0]
            profile_dic["qual2"] = qualification2.groups()[0]
            profile_dic["qualdate2"] = qualdate2.groups()[0]

        except:
            pass
            
        self.profile_dic = profile_dic
        return profile_dic
    
    def commit_to_CSV(self):
        profile_dic=self.profile_dic
        try:
            with open('tracked.txt') as t:
                if profile_dic['name'] not in t.read():
                    df = pandas.DataFrame(profile_dic, index=[1])
                    with pandas.ExcelWriter('checked_dentists.xlsx', mode='a', if_sheet_exists='overlay') as f:
                        df.to_excel(f, sheet_name='Sheet1',startrow=f.sheets['Sheet1'].max_row, index=False,header = False)
                    with open('tracked.txt','a') as t:
                        t.write(profile_dic['name'])
                else:
                    print('Doctor already recorded')
        except PermissionError('Please close output file and try again')():
            sys.exit('Please close output file and try again')


DP = Member(input("Enter doctor's code: "))
DP.grab_html()
print(DP.commit_to_dic().values())
DP.commit_to_CSV()





