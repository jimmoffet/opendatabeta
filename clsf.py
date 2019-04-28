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
SLACK_TOKEN = 'xoxp-305793099746-305700136803-362401453012-cfc0f39180930a00169d75ca2f8711ef'
SLACK_CHANNEL = "#housing"
sc = SlackClient(SLACK_TOKEN)

def clsf():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
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
        results = cl.get_results(sort_by='newest', geotagged=True, limit=200)
        
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
go = True
while(go):
    clsf()
    print('waiting for three minutes')
    time.sleep(180) 