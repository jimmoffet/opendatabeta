from __future__ import print_function
import requests
import requests.exceptions
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
from pprint import pprint
import time
import csv
import os.path
from copy import deepcopy
import sys
import datetime
import math

userhome = os.path.expanduser('~')
now = 1520998161 # current unix time in seconds, mar 13th 2018 at 11:31pm EDT, regular price is already in progress
todayStamp = datetime.date.today()
today = todayStamp.strftime('%d, %b %Y')
#now = 1511454297 # time.time keeps changing...

def getCoinIds():
    # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    try:
        u = 'https://min-api.cryptocompare.com/data/all/coinlist'
        r = requests.get(u)
        # print r
        resp = r.json()
        # print(resp)

        watchlist = [1182,7605,5038,24854,3807,3808,202330,5324,5031,20131] #

        coinids = {}
        data = resp['Data']
        for key, value in data.items():
            #print key, data[key]['Id']
            if value not in watchlist:
                coinids[key] = data[key]['Id'] # dictionary looks like {'BTC' : '1182', 'ETH' : '7605', etc... }
        info = coinids

        with open('coinids.json', 'w') as outfile:
            json.dump(coinids, outfile)
    except:
        foo = 'foo'

    return 'success'

# getCoinIds()
# sys.exit()

def getBirthsAndDeaths():
    birthsDeathsDict = {}
    with open('birthsanddeaths.csv', 'w') as outFile: 
        writer = csv.writer(outFile)
        with open('monthly_final_test.csv') as inFile:
            reader = csv.reader(inFile)
            cnt = 0
            monthsList = []

            for row in reader:
                if cnt == 0:
                    cnt+=1
                    for cell in row:
                        monthsList.append(cell)
                    continue
                cellcnt = 0
                deathMonth = monthsList[0]
                birthMonth = monthsList[len(monthsList)-1]
                for cell in row:
                    if cellcnt > 0:
                        if float(cell) > 0.0:
                            deathMonth = monthsList[cellcnt] # start at current work toward 2010
                            break
                    cellcnt+=1
                if deathMonth == monthsList[0]:
                    continue
                for i in range(len(row)-1, 0, -1):
                    if float(row[i]) > 0.0: # start at 2010 work toward present
                        break
                    birthMonth = monthsList[i]

                b = int(time.mktime(datetime.datetime.strptime(birthMonth,'%Y-%m-%d %H:%M:%S').timetuple())) # string to unix timestamp
                d = int(time.mktime(datetime.datetime.strptime(deathMonth,'%Y-%m-%d %H:%M:%S').timetuple())) # string to unix timestamp    
                writer.writerow([row[0],b,d])
                birthsDeathsDict[row[0]] = [b,d]
                cnt+=1
    return birthsDeathsDict


# getBirthsAndDeaths()

def getHourlyHistoPrice():
    # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    with open('birthsanddeaths.csv') as myFile:
            reader = csv.reader(myFile)
            cnt = 0
            cnt2 = 0
            onehour = 3600

            for row in reader:
                coin = row[0]
                birth = row[1]
                death = row[2]
                if row[2] == '1511454297': # coin was still alive when births and deaths were measured
                    death = str(now)
                current = int(death)
                while current > int(birth):
                    coinid = row[0]
                    try:            
                        u = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym=' + coinid + '&tsyms=BTC,USD,EUR&ts='+str(current)
                        r = requests.get(u)
                        resp = r.json()
                        tempList = [current, coinid]
                        for k,v in resp.items():
                            for k,v in v.items():
                                tempList.append(format(v,'.16f'))

                        with open(''+coinid+'_hourly.csv', 'a') as myFile: 
                            writer = csv.writer(myFile)
                            writer.writerow(tempList)

                    except:
                        with open(''+coinid+'_hourly.csv', 'a') as myFile:  
                            writer = csv.writer(myFile)
                            writer.writerow([current,coinid,'FAIL','FAIL','FAIL'])
                            print('fail')
                            print(resp)
                    myFile.close()

                    current -= onehour
                    #time.sleep(0.5)
                    cnt+=1
                    hourstogo = ( current - int(birth) ) / onehour
                    
                    if cnt % 13 == 0:
                        print('Scraping {}, currency {} of 1547, {} hourly prices remaining'.format(coinid, cnt2, hourstogo ) )
                        # print('time: {}'.format(int(time.time())))
                cnt2+=1
                if cnt2>5:
                    break

    return 'success'

#getHourlyHistoPrice()

def getWeeklyHistoPrice():
    # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # difsDict = json.load(open('difs.json')) # births and deaths
    outDict = {}
    currtime = now
    path = 'coinids.json'
    coinDict = json.load(open(path))
    prevtime = int(time.time())


    try:
        getCoinIds() # reenable this
        path = 'coinids.json'
        coinDict = json.load(open(path))
    except:
        foo = 'foo'

    for key, val in coinDict.items():
        coin = key # 'BTC'
        coinid = val # '1182'
        outDict[coin] = {}

    # onehour = 60*60
    oneweek = 60*60*24*7
    fourweeks = 60*60*24*7*4
    # if row[2] == '1511454297': # coin was still alive when births and deaths were measured
    
    cnt = 0
    cnt2 = 0
    go = True
    for key, val in coinDict.items():
        coin = key # 'BTC'
        coinid = val # '1182'
        cnt+=1
        death = str(now)
        current = int(death)
        
        while go:
            tempList = [current, 'FAIL', 'FAIL', 'FAIL', 'FAIL', 'FAIL', 'FAIL']
            cnt2+=1
            try:            
                # u = 'https://min-api.cryptocompare.com/data/histohour?fsym=' + coin + '&tsym=USD&limit=672&toTs='+str(current)
                # u = 'https://min-api.cryptocompare.com/data/histohour?fsym=SAGA&tsym=USD&limit=672&toTs='+str(current)
                u = 'https://min-api.cryptocompare.com/data/histohour?fsym=' + coin + '&tsym=USD&limit=672&toTs='+str(current)
                r = requests.get(u)
                resp = r.json()
                price = ''
                price = "FAIL"
                #print(resp['Data'][672]['high'])
                if resp['Data'][672]['high'] == 0:
                    print('no data, moving on to next coin')
                    break
                # print(resp)
                # sys.exit()
            except:
                print('api call failed')
                break
            
            try:
                for hour in resp['Data']:
                    Time = hour['time']
                    High = hour['high']
                    Low = hour['low']
                    Open = hour['open']
                    Close = hour['close']
                    VolumeFrom = hour['volumefrom']
                    VolumeTo = hour['volumeto']
                    tempList = [Time, High, Low, Open, Close, VolumeTo, VolumeFrom]
                    with open(''+coin+'_prices.csv', 'a') as myFile: 
                        writer = csv.writer(myFile)
                        writer.writerow(tempList)
                        myFile.close()


                    # if k == 'USD':
                    #     price = format(v,'.16f')

                
                # outDict[coin][current] = price
                # print(resp)
                # print(outDict[coin])
                
                # sys.exit()
                # if price == "FAIL":
                #     current = 1511450698 + 1
                # sys.exit()

                    # with open(''+coinid+'_weekly.csv', 'a') as myFile: 
                    #     writer = csv.writer(myFile)
                    #     writer.writerow(tempList)
            except Exception as e:
                print('resp parse failed')
                print(e)
                tempList = [current, 'FAIL', 'FAIL', 'FAIL', 'FAIL', 'FAIL', 'FAIL']
                with open(''+coin+'_prices.csv', 'a') as myFile: 
                    writer = csv.writer(myFile)
                    writer.writerow(tempList)
                    myFile.close()
                break

            current -= fourweeks
            # cnt+=1
            # fourweekstogo = ( current - 1511450697 ) / fourweeks


            if cnt2 % 10 == 0:
                print('Scraping {}, currency {} of {}, {} calls so far'.format(coin, cnt, len(coinDict), cnt2 ) )
                currtime = int(time.time())
                roundtime = currtime - prevtime
                # print('{} months to go'.format(fourweekstogo))
                print('Previous round of 10 months took {} seconds'.format(roundtime))
                # if roundtime - 72.5 <= 0.0:
                #     print('sleeping for {} seconds to stay under API cap'.format(math.fabs(roundtime - 72.5)))
                #     time.sleep(math.fabs(roundtime - 72.5))
                prevtime = currtime
        
    return 'success'

# getWeeklyHistoPrice()

def getCurrentPrice(foo):
    if foo == '':
        return 'getcurrentprice failed on blank input'
    # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # getCoinIds()
    path = 'coinids.json'
    data = json.load(open(path))
    go = True
    todayStamp = datetime.date.today()
    today = todayStamp.strftime('%d%b%Y')
    previous = today
    prevtime = int(time.time())
    # print(len(data))
    # sys.exit()

    while go:
        blocknow = int(time.time())
        cnt = 0
        try:
            getCoinIds() # reenable this
            path = 'coinids.json'
            data = json.load(open(path))
        except:
            foo = 'foo'

        todayStamp = datetime.date.today()
        today = todayStamp.strftime('%d%b%Y')

        if previous != today:
            foo = 'send previous file somewhere, or trigger it being pulled'

        printCnt = len(data) # make this len(data)
        for key, val in data.items():
            now = int(time.time())
            coinid = key
            try:            
                u = 'https://min-api.cryptocompare.com/data/price?fsym=' + coinid + '&tsyms=BTC,USD,EUR'
                r = requests.get(u)
                resp = r.json()
                #print(cnt)
                tempList = [blocknow, now, coinid]
                for k,v in resp.items():
                    if k == 'BTC' or 'USD' or 'EUR':
                        tempList.append(format(v,'.16f'))
                    else:
                        tempList.append('NA') 

                with open('static/'+today+'_prices.csv', 'a') as myFile: 
                    writer = csv.writer(myFile)
                    writer.writerow(tempList)
                    myFile.close()

            except Exception as e:
                # print(e)
                # foo = 'foo'
                with open('static/'+today+'_prices.csv', 'a') as myFile: 
                    writer = csv.writer(myFile)
                    writer.writerow([blocknow, now, coinid,'FAIL','FAIL','FAIL'])
                    #print('fail')
                    #print(resp)
                    myFile.close()

            #time.sleep(0.5)
            cnt+=1
            
            
            if cnt % 10 == 0:
                print('Scraping {}, currency {} of {}'.format(coinid, cnt, len(data) ) )
                currtime = int(time.time())
                roundtime = currtime - prevtime
                print('Previous round of {} coins took {} seconds'.format(printCnt, roundtime))
                # if roundtime - 72.5 <= 0.0:
                #     print('sleeping for {} seconds to stay under API cap'.format(math.fabs(roundtime - 72.5)))
                #     time.sleep(math.fabs(roundtime - 72.5))
                prevtime = currtime

        previous = today

    return 'success'

getCurrentPrice()

def formatMonthly():
    monthlyDict = {}
    rowList = ['Coin Name']
    cnt = 0
    with open('monthly.csv') as myFile:
        reader = csv.reader(myFile) 
        prevRow = ''
        for row in reader:
            if len(row) > 1:
                currRow = row[0]
                if currRow != prevRow:
                    datelabel = datetime.datetime.fromtimestamp(int(currRow)).strftime('%Y-%m-%d %H:%M:%S')
                    rowList.append(datelabel)

                monthlyDict[row[1]] = []
                cnt +=1
                prevRow = row[0]

    with open('monthly.csv') as myFile:
        reader = csv.reader(myFile)
        cnt = 0
        prevRow = ''
        for row in reader:
            if len(row) < 2:
                continue
            elif len(row) == 5:
                if row[3] == 'FAIL':
                    monthlyDict[row[1]].append('-1.0') 
                else:
                    monthlyDict[row[1]].append(row[3]) 
            elif len(row) == 3:
                monthlyDict[row[1]].append(row[2]) 
            else:
                print('FAILTOWN')
            cnt +=1

    with open('monthly_restructured.csv', 'a') as myFile: 
        writer = csv.writer(myFile)
        writer.writerow(rowList)
        for k, v in monthlyDict.items():
            temp = [k]
            for val in v:
                temp.append(val)
            writer.writerow(temp)
    return 'success'

#formatMonthly()

# def removeNulls():
#     monthlyDict = {}
#     rowList = ['Coin Name']
    
#     with open('monthly_final.csv', 'a') as outFile: 
#         writer = csv.writer(outFile)

#         with open('monthly_restructured.csv') as inFile:
#             reader = csv.reader(inFile) 
#             cnt = 0
#             for row in reader:
#                 if cnt == 0:
#                     writer.writerow(row)
#                     cnt += 1
#                     continue
#                 total = 0
#                 for i in range(1,95):
#                     total = total + float(row[i])
#                 if total == 0.0 or row[1] == '-1.0':
#                     foo = 'foo'
#                 else:
#                     writer.writerow(row)
#                 cnt += 1

# removeNulls()



#Read CSV File
def read_csv(infile, json_file, format):
    csv_rows = []
    with open(infile) as csvfile:
        reader = csv.DictReader(csvfile)
        title = reader.fieldnames
        for row in reader:
            csv_rows.extend([{title[i]:row[title[i]] for i in range(len(title))}])
        write_json(csv_rows, json_file, format)

#Convert csv data into json and write it
def write_json(data, json_file, format):
    with open(json_file, "w") as f:
        if format == "pretty":
            f.write(json.dumps(data, sort_keys=False, indent=4, separators=(',', ': '),encoding="utf-8",ensure_ascii=False))
        else:
            f.write(json.dumps(data))

def find_new_coins(first, second, format):
    getCoinIds()
    old = json.load(open(first)) # births and deaths
    new = json.load(open(second)) # current coinids
    oldCoinDict = {}
    newCoinDict = {}
    difDict = {}

    for d in old:
        for key, val in d.items():
            if key == 'LTD':
                oldCoinDict[val] = 'foo'

    for key, val in new.items():
            if key not in oldCoinDict:
                difDict[key] = val

    with open('difs.json', "w") as f:
        if format == "pretty":
            f.write(json.dumps(difDict, sort_keys=False, indent=4, separators=(',', ': '),encoding="utf-8",ensure_ascii=False))
        else:
            f.write(json.dumps(oldCoinDict))


# getCoinIds()
# read_csv('birthsanddeaths.csv', 'birthsanddeaths.json', "pretty") # creates birthanddeaths.json
# find_new_coins('birthsanddeaths.json', 'coinids.json', "pretty") # creates difs.json

# getWeeklyHistoPrice()

print('done')



