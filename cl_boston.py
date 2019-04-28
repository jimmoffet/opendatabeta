from bs4 import BeautifulSoup
import requests
import requests.exceptions
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from craigslist import CraigslistHousing
from slackclient import SlackClient
from math import sin, cos, sqrt, atan2, radians
import sys
import time

app_id = "2024489881171070"
app_secret = "86339533a5793651f88deea4b2f254c0"
maps_key = "AIzaSyDtbzOO7z-9NcDCHTJoj9lJdI59kNKPxYo"

def getMovein(url):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser', from_encoding='utf-8')
    listitems = soup.find_all('span', class_="property_date")

    for item in listitems:
        numdate = ''
        if item["data-date"]:
            numdate = item["data-date"]
            print(numdate)
            return numdate
        item = item.getText()
        item = item.encode('ascii', 'ignore')
        item = item.decode('ascii', 'ignore')
        print(item)
        return item



def getWalkDist(lat, lon, zc):
    targetLat = 42.396680
    targetLon = -71.122021
    gonogo = True
    if zc == '02144':
        targetLat = 42.396680 # Davis T station
        targetLon = -71.122021 # Davis T station
        base = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&mode=walking&origins='+str(targetLat)+','+str(targetLon)
        destination = '&destinations='+str(lat)+','+str(lon)
        key = '&key=AIzaSyDtbzOO7z-9NcDCHTJoj9lJdI59kNKPxYo'
        u = base+destination+key
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        resp = requests.get(u)
        data = resp.json()
        d = data['rows'][0]['elements'][0]['duration']['value']
        d = float(d)/60
        print(str(int(d))+' minutes walk')
        if d > 12:
            gonogo = False
            return gonogo
        else:
            gonogo = True
            return gonogo

    elif zc == '02143':
        targetLat = 42.379843 # Union Square
        targetLon = -71.096191 # Union Square
        base = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&mode=walking&origins='+str(targetLat)+','+str(targetLon)
        destination = '&destinations='+str(lat)+','+str(lon)
        key = '&key=AIzaSyDtbzOO7z-9NcDCHTJoj9lJdI59kNKPxYo'
        u = base+destination+key
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        resp = requests.get(u)
        data = resp.json()
        d_union = data['rows'][0]['elements'][0]['duration']['value']
        d_union = float(d_union)/60
        print(str(int(d_union))+' minutes walk')

        targetLat = 42.382922 # Aeronaut
        targetLon = -71.105117 # Aeronaut
        base = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&mode=walking&origins='+str(targetLat)+','+str(targetLon)
        destination = '&destinations='+str(lat)+','+str(lon)
        key = '&key=AIzaSyDtbzOO7z-9NcDCHTJoj9lJdI59kNKPxYo'
        u = base+destination+key
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        resp = requests.get(u)
        data = resp.json()
        d_aero = data['rows'][0]['elements'][0]['duration']['value']
        d_aero = float(d_aero)/60
        print(str(int(d_aero))+' minutes walk')

        if min(d_union, d_aero) > 6:
            gonogo = False
            return gonogo
        else:
            gonogo = True
            return gonogo

    elif zc == '02139':
        gonogo = True
        return gonogo

    return gonogo

    # for item in data.items():
    #     print(item)

# getWalkDist(42.370666,-71.108800,'davis')
# sys.exit()


def clsf(zc):
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("cl_boston").sheet1
    sheetList = sheet.get_all_values()
    rlen = len(sheetList)
    clen = len(sheetList[0])
    ids = []
    for row in range(rlen):
        if row == 0:
            continue
        ids.append(sheetList[row][0])
    print(ids)

    row_cnt = rlen
    # davisLat = 42.396680
    # davisLon = -71.122021
    # jpLat = 42.313947
    # jpLon = -71.109671
    # targetLat = 0.0
    # targetLon = 0.0
    # d = 0.0
    # if zc == '02144':
    #     targetLat = davisLat
    #     targetLon = davisLon
    #     d_max = 13 # this is minutes now
    # elif zc == '02139'
    # else:
    #     targetLat = jpLat
    #     targetLon = jpLon
    #     d_max = 13 # this is minutes now
    try:
        cl = CraigslistHousing(site='boston', area='gbs', category='aap', filters={'max_price': 2600, 'min_price': 1700, 'min_bedrooms': 1, 'zip_code': zc, 'search_distance': 1, 'posted_today': True})
        results = cl.get_results(sort_by='newest', geotagged=True, limit=800)
    except Exception as e:
        print('sleeping on failure')
        raise e
        time.sleep(300)
    
    for result in results:
        col_cnt = 1
        cl_name = ''
        cl_url = ''
        cl_price = ''
        cl_where = ''
        cl_beds = ''
        cl_mdate = ''
        
        if result['id'] in ids:
            print('Found an old one: '+result['id'])
            continue

        if result['geotag']:
            loc = result['geotag']
            # d = getDist(loc[0],loc[1],targetLat,targetLon)
            keep = getWalkDist(loc[0],loc[1],zc)
            if keep != True:
                print('TOO FAR AWAY')
                continue
        if result['url']:
            cl_mdate = getMovein(result['url'])
            if cl_mdate != '2018-09-01':
                print("NOT SEPTEMBER: "+cl_mdate)
                continue
        else:
            continue

        print('Found a new one: '+result['id'])
        row_cnt += 1

        cl_name = result['name']
        cl_url = result['url']
        cl_price = result['price']
        cl_where = result['where']
        cl_beds = result['bedrooms']

        cl_row = []
        cl_row.append(str(result['id']))
        cl_row.append(str(result['repost_of']))
        cl_row.append(str(result['name']))
        cl_row.append(str(result['url']))
        cl_row.append(str(result['datetime']))
        cl_row.append(str(result['price']))
        cl_row.append(str(result['where']))
        cl_row.append(str(result['has_image']))
        cl_row.append(str(result['has_map']))
        cl_row.append(str(result['geotag']))
        cl_row.append(str(result['bedrooms']))
        cl_row.append(str(result['area']))
        cl_row.append(cl_mdate)
        # print(cl_row)

        try:
            sheet.insert_row(cl_row, row_cnt)
        except Exception as e:
            print('write to google sheet failed...')
            print(e)
        else:
            pass
        finally:
            pass

    return 'foo'

def getDist(latA,lonA,latB,lonB):
    R = 6373.0 # approximate radius of earth in km
    lat1 = radians(latA)
    lon1 = radians(lonA)
    lat2 = radians(latB)
    lon2 = radians(lonB)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

go = True
while(go):
    print('Now running Union')
    clsf('02143')
    print('waiting for five minutes')
    time.sleep(300) 
    print('Now running Central')
    clsf('02139')
    print('waiting for five minutes')
    time.sleep(300) 
    print('Now running Davis')
    clsf('02144')
    print('waiting for five minutes')
    time.sleep(300) 

