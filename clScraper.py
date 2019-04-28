from bs4 import BeautifulSoup
import requests
import requests.exceptions
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import sys
# import re
# from selenium import webdriver
# import time

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
		

url = 'https://boston.craigslist.org/gbs/fee/d/avabed-1-bath-all-util-incl/6580432779.html'
mdate = getMovein(url)
if mdate == '2018-09-01':
	print('WIN')
else:
	print('LOSE')