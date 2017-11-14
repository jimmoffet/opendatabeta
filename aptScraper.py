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

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.binary_location = "/Users/jim/drivers/chromedriver"
driver = webdriver.Chrome("/Users/jim/drivers/chromedriver")
driver.get('https://www.apartmentrentalexperts.com/MA/EasySearch/4/15/Bedroom/1/MinPrice/0/MaxPrice/2100/ApartmentsForRent')

driver.set_window_position(0, 0)
driver.set_window_size(1024, 768)

time.sleep(3)
gobutton = driver.find_element_by_id('ctl00_btnSubmitForm').click()
time.sleep(3)

bigList = []
go = True
cnt = 2
while(go):
	html = driver.page_source
	soup = BeautifulSoup(html,"lxml")
	tables = soup.find_all('table')
	innertable = tables[0].find_all('table')
	stuff = innertable[0].find_all('tr')

	bigList.extend(getRows(stuff))

	#print('cnt is',cnt)
	html = driver.page_source
	soup = BeautifulSoup(html,"lxml")
	pagenum = str(cnt)
	nextpage = "Page$" + pagenum
	for a in soup.findAll('a', href=re.compile('javascript')):
		chk = a['href']
		if nextpage in chk:
			print('Moving to results page: ', pagenum)

	variable = "javascript:__doPostBack('ctl00$Body$grdListings','"+nextpage+"')"
	#print('variable is ', variable)
	try:
		gobutton = driver.find_element_by_xpath('//a[@href="'+variable+'"]').click()
		time.sleep(3)
	except:
		go = False
		continue
	
	cnt+=1

# for row in bigList:
# 	print(row)

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

# Read nums from first col to list and then compare

row = 2
for small in bigList:
	print('Writing row ', row)
	col = 1

	for cell in small:
		# print('row is ', row)
		# print('col is ', col)
		sheet.update_cell( int(row), int(col), str(cell) )
		col+=1
	if small[0] in numList:
		sheet.update_cell( int(row), 11, 'old' )
	else:
		sheet.update_cell( int(row), 11, 'new' )
	row+=1
sheet.update_cell( int(row), 1, 'STOP HERE' )

print('Done!')
