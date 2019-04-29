import requests
import requests.exceptions
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import time

# scope = ['https://spreadsheets.google.com/feeds']
# creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
# client = gspread.authorize(creds)


# get persistent layer as list of lists
def pLayer():
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("SLINGSHOTREFERRALS").sheet1
    # Extract and print all of the values
    #list_of_vals = sheet.get_all_values()
    return sheet

def tryName(name, rlen, sheetList):
    new = True
    link = 'https://www.slingshotcontest.io/'+name
        
    for row in range(rlen):
        if row == 0:
            continue
        if sheetList[row][2] == link:
            new = False
    return new, link


def people(passClient, fullname, email, ref = ''):
    # use creds to create a client to interact with the Google Drive API
    
    sheet = passClient.open("SLINGSHOTREFERRALS").sheet1
    sheetList = sheet.get_all_values()
    rlen = len(sheetList)
    # clen = len(sheetList[0])

    names = fullname.split()

    link = 'https://www.slingshotcontest.io/'

    nameStr = ''
    cnt = 0
    num = 1
    go = True
    for name in names:
        new = True
        cnt+=1
        nameStr = nameStr+name
        new, link = tryName(nameStr, rlen, sheetList)

        if new == True:
            sheet.update_cell(rlen+1, 1, fullname) # record first name
            sheet.update_cell(rlen+1, 2, email) # record first name
            sheet.update_cell(rlen+1, 3, link) # record first name
            sheet.update_cell(rlen+1, 4, ref) # record first name
            return fullname, email, link, ref
    while(go):
        new = True
        new, link = tryName(fullname.replace(' ','')+str(num), rlen, sheetList)
        if new == True:
            sheet.update_cell(rlen+1, 1, fullname) # record first name
            sheet.update_cell(rlen+1, 2, email) # record first name
            sheet.update_cell(rlen+1, 3, link) # record first name
            sheet.update_cell(rlen+1, 4, ref) # record first name
            return fullname, email, link, ref
            go = False
            break

        num+=1

        if num > 100:
            go = False
            break
    return fullname, email, link, ref

def linkCheck(passClient, fullname, email = '', team = ''):
    # use creds to create a client to interact with the Google Drive API
    
    sheet = passClient.open("SLINGSHOTREFERRALS").sheet1
    sheetList = sheet.get_all_values()
    rlen = len(sheetList)
    # clen = len(sheetList[0])

    names = fullname.split()

    link = 'https://www.slingshotcontest.io/'

    nameStr = ''
    cnt = 0
    num = 1
    go = True
    for name in names:
        new = True
        cnt+=1
        nameStr = nameStr+name
        new, link = tryName(nameStr, rlen, sheetList)

        if new == True:
            return fullname, email, link, team
    while(go):
        new = True
        new, link = tryName(fullname.replace(' ','')+str(num), rlen, sheetList)
        if new == True:
            return fullname, email, link, team
            go = False
            break

        num+=1

        if num > 100:
            go = False
            break
    return fullname, email, link, team

