from flask import Flask, request, redirect, jsonify, render_template, send_from_directory
from flask_cors import CORS, cross_origin
from scrape import people, linkCheck
import random
import threading
import datetime
import re
import time
from string import punctuation
import os
import copy
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# account_sid = os.environ.get('TWILIO_SID', None)
# auth_token = os.environ.get('TWILIO_TOKEN', None)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Find these values at https://twilio.com/user/account
# account_sid = 'XXXXXXXXXXX" # PUT YOUR TWILIO ACCOUNT_SID IN twilio_creds.py FILE
# auth_token = 'XXXXXXXXXXX" # PUT YOUR TWILIO_AUTH TOKEN IN twilio_creds.py FILE
# client = Client(account_sid, auth_token)

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
gClient = gspread.authorize(creds)
gClient.login()  # refreshes the token
sheet = gClient.open("SLINGSHOTREFERRALS").sheet1

# sheet = gClient.open("SLINGSHOTREFERRALS").sheet1
sheetList = sheet.get_all_values()
rlen = len(sheetList)

def tryName(name, rlen, sheetList):
    new = True
    link = 'https://www.slingshotchallenge.com/'+name
        
    for row in range(rlen):
        if row == 0:
            continue
        if sheetList[row][2] == link:
            new = False
    return new, link

def people(passClient, fullname, email, ref = ''):

    sheet = passClient.open("SLINGSHOTREFERRALS").sheet1
    sheetList = sheet.get_all_values()
    rlen = len(sheetList)
    names = fullname.split()
    link = 'https://www.slingshotchallenge.com/'
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

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def hello():
	out = ''
	try:
		ref_name = ''
		return render_template('index.html', ref_name=ref_name)
	except:
		out = '404: Please contact your system administrator.'
		return out

@app.route('/<string:ref_name>/')
def render_static_referral(ref_name):
	ref_code = copy.copy(ref_name)
	for row in range(rlen):
		if row == 0:
			continue
	if sheetList[row][2].replace('https://www.slingshotchallenge.com/','') == ref_name:
		ref_name = sheetList[row][0]
	return render_template('index.html', ref_name=ref_name, ref_code=ref_code)

@app.route('/slingshot/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)

@app.route("/submit", methods=["POST"])
def submit():
	if request.method == "POST":
		resp = request.get_json()
		name = resp['name']
		email = resp['email']
		ref = resp['ref']
		outname, outemail, outlink, outref = people(gClient, name, email, ref)
	return jsonify({"type":"success", "data":outlink})

@app.route("/softSubmit", methods=["POST"])
def softSubmit():
	if request.method == "POST":
		resp = request.get_json()
		name = resp['name']
		outname, outemail, outlink, outteam = linkCheck(gClient, name)
	return jsonify({"type":"success", "data":outlink})

if __name__ == "__main__":
	app.run(debug=False)
