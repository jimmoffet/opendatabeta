from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests
import requests.exceptions
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import re

def pLayer():
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Apt Experts").sheet1
    # Extract and print all of the values
    #list_of_vals = sheet.get_all_values()
    return sheet

def getRows(stuff):
	
	bigList = []
	cnt = 0
	stop = False
	for row in stuff:
		if cnt == 0:
			cnt += 1
			continue
		#print('row is ',cnt)
		smallList = []
		cells = row.find_all('td')
		cnt2 = 0
		if 'Cambridge' in cells[2].getText() or 'Somerville' in cells[2].getText() :
			#print('cells6 is ',cells[7].getText())
			money = cells[7].getText().replace('$','').replace(',','')
			money = int(money)
			if money < 1700:
				cnt+=1
				continue
			beds = cells[4].getText()
			if 'Studio' in beds:
				cnt+=1
				continue
			movein = cells[6].getText().split('/')
			movein = movein[0]
			if '10' in movein:
				cnt+=1
				continue
			for cell in cells:
				chk = cell.getText()
				if '1234' in chk:
					stop = True
					break
				else:
					if cnt2 == 0:
						link = cell.find('a', href=True)
						link = link['href']
						link = 'https://www.apartmentrentalexperts.com' + link
						try:
							num = link.split('https://www.apartmentrentalexperts.com/ApartmentForRent/Listing/')
							num = num[1]
							smallList.append(num)
						except:
							foo = 'foo'
						smallList.append(link)
					else:
						#print('cell is ', cnt2)
						#print(cell.getText())
						smallList.append(cell.getText())
				cnt2+=1
			if stop:
				break
			bigList.append(smallList)
			cnt += 1
		else:
			continue
			cnt += 1
	return bigList

# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument("--test-type")
# options.binary_location = "/Users/jim/drivers/chromedriver"
# driver = webdriver.Chrome("/Users/jim/drivers/chromedriver")

url = 'https://boston.craigslist.org/search/aap?availabilityMode=0&bundleDuplicates=1&hasPic=1&max_price=2100&min_bedrooms=1&min_price=1650&postal=02144&query=%28davis%20%7C%20porter%29%20-medford%20-ball%20-magoun%20-arlington%20-teele%20-%22West%20Somerville%22%20-malden&search_distance=2&sort=date'

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser', from_encoding='utf-8')

bigList = []
go = True
cnt = 2

# html = driver.page_source
# soup = BeautifulSoup(html,"lxml")
listitems = soup.find_all('li', class_="result-row duplicate-row")
for item in listitems:
	#print('next--------------------------')
	smallList = []
	item = item.getText()
	item = item.encode('ascii', 'ignore')
	item = item.decode('ascii', 'ignore')
	lines = item.splitlines()
	checks = ['favorite this post','restore this posting','map','restore','more like this]','hide this posting']
	for line in lines:
		c = False
		line = line.strip(' ')
		for check in checks:
			if check in line:
				c = True;
		if c or line == '':
			#print('continuing to the next line')
			continue
		else:
			smallList.append(line)

	tempList = []
	tempList.append(smallList[0])
	c = False
	for s in smallList:
		if s not in tempList:
			tempList.append(s)
	for t in tempList:
		if 'Ball' in t or 'Magoun' in t or 'Teele' in t or 'Medford' in t or 'Arlington' in t or 'West Somerville' in t:
			c = True
			break
	if c == False:
		bigList.append(tempList)

print('Length of results is ',len(bigList))
for b in bigList:
	print(b)
#print(bigList)
sys.exit()

sheet = pLayer()
totes = sheet.row_count

numList = []

for i in range(2,totes):
	#print(i)
	num = sheet.cell(i,1).value
	numList.append(num)
	if 'STOP' in num:
		print('Finished loading old nums')
		break

sheet.update_cell( int(row), 1, 'STOP HERE' )

print('Done!')
