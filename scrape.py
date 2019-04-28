from bs4 import BeautifulSoup
import requests
import requests.exceptions
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from craigslist import CraigslistHousing
from slackclient import SlackClient
import sys
import time

app_id = "2024489881171070"
app_secret = "86339533a5793651f88deea4b2f254c0"
templongtoken = 'EAAcxQ0g39H4BAGqdPiKfXEGP6El4udrFPszciNHu5fEqDtX0hqkcUZBxrTAD6EHBBMajiIotWfdmfKyGRZAnjauiLc6JZBb5kp9dFz3yvPq6ezmMCHA1xn5DeZAylIOjWSmOZB47UItXBMaPAw3xinET8LJLDPbYZD'
tempshorttoken = 'EAAcxQ0g39H4BAPSaeJY0psdqoTdh4WZBSGCLk6iRwzsZApBXYWNjQiTtEIXUYE8sP4uyg5DTc9ZCifIvkkV9jTQBs8Ytxk48EP1ElamrZAH1WrBFzovYHKUZBNGFSDe8qHLtx0qjGe9TbYdryXp9n3Rp5GJMcJTwU1xSQpUVRBLZBIMJdfEPjZADZCKj24SLSgSk9DoyKH2ZBewZDZD'
SLACK_TOKEN = 'xoxp-305793099746-305700136803-362401453012-cfc0f39180930a00169d75ca2f8711ef'
SLACK_CHANNEL = "#housing"
sc = SlackClient(SLACK_TOKEN)

# scope = ['https://spreadsheets.google.com/feeds']
# creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
# client = gspread.authorize(creds)

def ping(u):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    page = requests.get(u)
    return page

def extendToken(short_token):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # app_id = ''
    # app_secret = ''
    u = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&' + 'client_id=' + app_id + '&client_secret=' + app_secret + '&fb_exchange_token=' + short_token
    r = requests.get(u)
    resp = r.json()
    return resp  

def scrape(u):
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    page = requests.get(u)
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding='utf-8')
    paragraphs = soup.find_all("p")

    bigList = []

    for para in paragraphs:
        para = para.getText()
        para = para.encode('ascii', 'ignore')
        para = para.decode('ascii', 'ignore')
        bigList.append(para)

    culledList = []

    cnt = 0

    week = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    while(True):
        cnt += 1
        if cnt < 4:
            continue

        mtg = {}

        if cnt+6 > len(bigList):
            break

        for day in week:
            if day in bigList[cnt]:
                mtg['date'] = bigList[cnt]
                mtg['time'] = bigList[cnt+1]
                mtg['agenda'] = bigList[cnt+2]
                mtg['location'] = bigList[cnt+5].replace('(',"").replace(')',"")
                culledList.append(mtg)
                cnt += 5

    return culledList

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

# fullname, email, link, team = people(client, 'John','asdf@asdf.com','team@team.com')
# print('done')
# print(peoples)
# print('Done!')

def clsf():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("clsf").sheet1
    sheetList = sheet.get_all_values()
    rlen = len(sheetList)
    clen = len(sheetList[0])
    ids = []
    for row in range(rlen):
        if row == 0:
            continue
        ids.append(sheetList[row][0])
    print(ids)
    areas = ['sfc','pen','sby']

    row_cnt = rlen
    
    for area in areas:
        print("area is "+area)
        cl = CraigslistHousing(site='sfbay', area=area, category='sub', filters={'max_price': 8000, 'min_price': 4800, 'min_bedrooms': 3, 'is_furnished': True})
        results = cl.get_results(sort_by='newest', geotagged=True, limit=50)

        
        for result in results:
            col_cnt = 0
            row_cnt += 1
            if result['id'] in ids:
                print('Found one: '+result['id'])
                continue
            print('Found a new one: '+result['id'])
            cl_name = ''
            cl_url = ''
            cl_price = ''
            cl_where = ''
            cl_beds = ''
            for k,v in result.items():
                col_cnt+=1
                # print(result['name'])
                # print(row_cnt)
                # temp = sheetList[0][0]
                # print(temp)
                cl_name = result['name']
                cl_url = result['url']
                cl_price = result['price']
                cl_where = result['where']
                cl_beds = result['bedrooms']
                sheet.update_cell(row_cnt, col_cnt, v)
            desc = "{0} | {1} | {2} | {3} | <{4}>".format(cl_where, cl_price, cl_name, cl_beds+' beds', cl_url)
            sc.api_call(
                "chat.postMessage", channel=SLACK_CHANNEL, text=desc,
                username='pybot', icon_emoji=':robot_face:'
            )

    return 'foo'

# while(go):
#     clsf()
#     time.sleep(5) 

