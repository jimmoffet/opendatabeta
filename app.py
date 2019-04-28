from flask import Flask, request, redirect, jsonify, render_template
from flask_cors import CORS, cross_origin
from scrape import people, linkCheck
import random
import threading
import datetime
import re
import time
from string import punctuation
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

account_sid = os.environ.get('TWILIO_SID', None)
auth_token = os.environ.get('TWILIO_TOKEN', None)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Find these values at https://twilio.com/user/account
# account_sid = 'XXXXXXXXXXX" # PUT YOUR TWILIO ACCOUNT_SID IN twilio_creds.py FILE
# auth_token = 'XXXXXXXXXXX" # PUT YOUR TWILIO_AUTH TOKEN IN twilio_creds.py FILE
# client = Client(account_sid, auth_token)

scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
gClient = gspread.authorize(creds)

# print(account_sid)

@app.route("/")
def hello():
	out = ''
	try:
		ref_name = ''
		return render_template('index.html', ref_name=ref_name)
	except:
		out = ' FIX MEEEEEEEEEEEEEEEEEEEEEE!!!!.'
		return out

@app.route('/<string:ref_name>/')
def render_static_referral(ref_name):
    return render_template('index.html', ref_name=ref_name)

@app.route('/slingshot/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)

@app.route("/ref/<string:refcode>", methods=["POST", "GET"])
def renderLogin(refcode):
	refname=''
	random.seed( str(time.time()).replace('.','') )
	if refcode:
		refname = refcode
	else:
		refcode = random.randint(100000000, 999999999)
	print(refcode)
	return render_template('index.html', refcode=refcode, refname=refname)

@app.route("/submit", methods=["POST"])
def submit():
	if request.method == "POST":
		
		resp = request.get_json()
		name = resp['name']
		email = resp['email']
		ref = resp['ref']
		print('name is ', name)
		print('ref is ', ref)

		outname, outemail, outlink, outref = people(gClient, name, email, ref)

	return jsonify({"type":"success", "data":outlink})

@app.route("/softSubmit", methods=["POST"])
def softSubmit():
	if request.method == "POST":
		
		resp = request.get_json()
		name = resp['name']
		print('name is ', name)

		outname, outemail, outlink, outteam = linkCheck(gClient, name)

	return jsonify({"type":"success", "data":outlink})


if __name__ == "__main__":
	app.run(debug=False)
