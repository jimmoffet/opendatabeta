from flask import Flask, request, redirect, jsonify, render_template
from flask_cors import CORS, cross_origin
from twilio.twiml.messaging_response import MessagingResponse
from scrape import scrape, ping, people, pLayer, extendToken
import random
import threading
import datetime
import re
from twilio.rest import Client
from string import punctuation
import os

account_sid = os.environ.get('TWILIO_SID', None)
auth_token = os.environ.get('TWILIO_TOKEN', None)


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Find these values at https://twilio.com/user/account
# account_sid = 'XXXXXXXXXXX" # PUT YOUR TWILIO ACCOUNT_SID IN twilio_creds.py FILE
# auth_token = 'XXXXXXXXXXX" # PUT YOUR TWILIO_AUTH TOKEN IN twilio_creds.py FILE
client = Client(account_sid, auth_token)

# print(account_sid)

textfriend = False
friendnumber = '+17733541500'
friendmessage = 'Default friend message'

@app.route("/")
def hello():
	out = ''
	try:
		page_name = 'newnetwork'
		return render_template('%s.html' % page_name)
	except:
		out = ' FIX MEEEEEEEEEEEEEEEEEEEEEE!!!!.'
		return out

@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)

@app.route("/commit/<string:shorttoken>", methods=["POST", "GET"])
def getLongToken(shorttoken):

    resp = extendToken(shorttoken)
    longtoken = resp['access_token']
    print(longtoken)
    
    ### save longtoken to db along with uid and whatever else

    return jsonify(resp)

@app.route("/api")
def serve_schedule():
	schedule = scrape('http://cambridgema.iqm2.com/Citizens/Detail_LegalNotice.aspx?ID=1008')
	return jsonify(schedule)

@app.route("/scrape/<string:start_command>/")
def scrape_current(start_command):
	if start_command != '':
		print('starting current')
		output = getCurrentPrice(start_command)
	return 'current process started'

@app.route("/show")
def show_current():
	path = "/static"
	tDict = {}
	for filename in os.listdir(path):
		if re.match("*prices.csv", filename):
			with open(os.path.join(path, filename), 'r') as f:
				cnt=0
				tDict[filename] = []
				for line in f:
					tDict[filename].append(line)
					cnt+=1
					if cnt > 3:
						f.close()
						break
	return jsonify(tDict)

@app.route("/monkey", methods=['GET', 'POST'])
def hello_monkey():
	"""Respond and greet the caller by name."""

	now = datetime.datetime.now()
	now = now.replace(second=0, microsecond=0)

	peoples = people()
	sheet = pLayer()

	count = len(peoples)

	#electionday = datetime.datetime.strptime("17-11-07 10:00:00","%Y-%m-%d %H:%M:%S")

	message = "VoteBot here! Want a little help from your friends remembering to vote next month? VoteBot users that promise to text a friend on election day are the most likely to follow through.\n\nIf you're down, say yes or friend! \n\nWant to keep the reminders between us? Say remind me!"
	# message = message + ' ' + 'I only do one thing, but I do it well. For a weekly reminder say "weekly", for monthly say "monthly" and to see only the very next meeting say "next". You can say "stop" or "unsubscribe" at any time.'



	pOutgoing = ''

	# this is a string
	incoming = request.values.get('Body', None)
	from_number = request.values.get('From', None)

	cnt = 0
	for key, val in peoples.items():
		cnt += 1
		if key == from_number:
			break

	capsincoming = incoming
	incoming = incoming.lower()
	pIncoming = incoming

	### Identify names and numbers, if they exist ###
	number = ''
	numbers = sum(c.isdigit() for c in incoming)
	name = ''.join([i for i in capsincoming if not i.isdigit()])

	if numbers > 9:
		number = number + re.sub('[^0-9]','', incoming)
		if len(number) < 11:
			number = '1'+number
	if ',' in capsincoming:
		name, tempnumber = capsincoming.split(",")
	else:
		name = ''.join(i for i in capsincoming if i not in punctuation)

	### DB Row belonging to user ###
	if from_number in peoples:
		userName = peoples[from_number][0]
		introduced = peoples[from_number][1]
		friendCommit = peoples[from_number][2]
		friendNumber = peoples[from_number][3]
		friendSent = peoples[from_number][4]
		votebotCommit = peoples[from_number][5]
		isFriend = peoples[from_number][6]

	### Reminder Dates
	sevenDayNotice = '10/31/2017 09:00:00'
	threeDayNotice = '11/04/2017 09:00:00'
	dayBeforeNotice = '11/06/2017 09:00:00'
	electionDay = '11/07/2017 09:00:00'

	### Delete this, go with canonical naming
	electionday = '11/07/2017 09:00:00'

	deactivateuser = False
	notifyfriendstop = False ### Do we actually want to do this?

	### Handle unsubscribers
	stopwords = ('stop', 'stopall', 'unsubscribe', 'cancel', 'end', 'quit')
	for stopword in stopwords:
		if stopword in incoming:
			deactivateuser = True
			sheet.update_cell(cnt+1, 17, 'yes') # unsubscribed
			if peoples[from_number][6] == 'yes':
				notifyfriendstop = True

	#######################
	### Begin Bot Logic ###
	#######################

	## If we have their bnumber and they've committed to text a friend
	if from_number in peoples and friendCommit == 'yes' and len(number) > 8:
		textfriend = True
		friendnumber = '+'+number

		if len(name) > 1:
			pOutgoing = message
			friendmessage = "Hi, I'm VoteBot. Your friend " + name + " wants you to help them make sure they vote on November 7th. They promise to send you a text from the poll.\n\nSay stop at any time to unsubscribe, or better yet...\n\nSay more to check out VoteBot or to use it yourself!"
		else:
			pOutgoing = message
			friendmessage = "Hi, I'm VoteBot. Your friend " + from_number + " wants you to help them make sure they vote on November 7th. They promise to send you a text from the poll.\n\nFeel free to say stop at any time to unsubscribe, or better yet...\n\nSay more to check out VoteBot or to use it yourself!"

		pOutgoingFriend = message
		message = "Great! I just sent a message to "+friendnumber+" letting them know to expect a text from you on election day.\n\nYou can say stop to unsubscribe you and your friend at any time.\n\nI'll remind you 3 days before and again on election day, 11/07/17.\n\nYou can say more for more reminders, or less if you want less.\n\nClick https://tr.im/votebot for more info."

		client.api.account.messages.create(
		    to=friendnumber,
		    from_="+16178509561",
		    body=friendmessage)

		### Update User's Row
		sheet.update_cell(cnt+1, 2, name) # mark friend number
		sheet.update_cell(cnt+1, 5, friendnumber) # mark friend number
		sheet.update_cell(cnt+1, 6, "yes") # mark friend sent
		sheet.update_cell(cnt+1, 12, pIncoming) # previous incoming
		sheet.update_cell(cnt+1, 13, pOutgoing) # previous outgoing
		sheet.update_cell(cnt+1, 14, now) # last sent message

		if friendnumber not in peoples:
			### Create Friend's Row
			sheet.update_cell(cnt+2, 1, friendnumber) # add friend as new user
			sheet.update_cell(cnt+2, 3, "yes") # intro
			sheet.update_cell(cnt+2, 13, pOutgoingFriend) # previous outgoing
			sheet.update_cell(cnt+2, 14, now) # last sent message
			sheet.update_cell(cnt+2, 16, electionday) # last sent message
		else:
			### Wrap this in a function!
			cnt2 = 0
			for key, val in peoples.items():
				cnt2 += 1
				if key == friendnumber:
					break
			### Update Friend's Row
			sheet.update_cell(cnt2+1, 1, friendnumber) # add friend as new user
			sheet.update_cell(cnt2+1, 3, "yes") # intro
			sheet.update_cell(cnt2+1, 13, pOutgoingFriend) # previous outgoing
			sheet.update_cell(cnt2+1, 14, now) # last sent message
			sheet.update_cell(cnt2+1, 16, electionday) # last sent message

	elif from_number in peoples and peoples[from_number][4] == 'yes':
		message = "Great! I'll remind you 3 days before and again on election day, 11/07/17.\n\nClick https://tr.im/votebot for more info."

		pOutgoing = message
		sheet.update_cell(cnt+1, 12, pIncoming) # previous incoming
		sheet.update_cell(cnt+1, 13, pOutgoing) # previous outgoing
		sheet.update_cell(cnt+1, 14, now) # last sent message

	elif from_number in peoples and 'yes' in incoming or 'friend' in incoming:
		lastsent = now - datetime.timedelta(days=7)
		lastsent = lastsent.replace(second=0, microsecond=0)
		message = "Great! Text me your name (optional) and their number and I'll tell them to expect a text from you on election day. I'll also remind you :)\n\nText me like this: \nyour name, their number"
		pOutgoing = message

		sheet.update_cell(cnt+1, 4, "yes") # text their friend
		sheet.update_cell(cnt+1, 7, "no") # reminders only
		sheet.update_cell(cnt+1, 12, pIncoming) # previous incoming
		sheet.update_cell(cnt+1, 13, pOutgoing) # previous outgoing
		sheet.update_cell(cnt+1, 14, now) # last sent message

	elif from_number in peoples and 'remind' in incoming:
		lastsent = now - datetime.timedelta(days=7)
		lastsent = lastsent.replace(second=0, microsecond=0)
		message = "Great! I'll remind you 3 days before and again on election day, 11/07/17.\n\nClick https://tr.im/votebot for more info."

		pOutgoing = message
		sheet.update_cell(cnt+1, 4, "no") # text their friend
		sheet.update_cell(cnt+1, 7, "yes") # reminders only
		sheet.update_cell(cnt+1, 12, pIncoming) # previous incoming
		sheet.update_cell(cnt+1, 13, pOutgoing) # previous outgoing
		sheet.update_cell(cnt+1, 14, now) # last sent message

	else:
		if from_number in peoples:
			# write a cheeky message here cause they're trying to chat you up (or we have them on a member list)
			if 'more' in incoming:
				message = "VoteBot here! Want a little help from your friends remembering to vote next month? VoteBot users that promise to text a friend on election day are the most likely to follow through.\n\nIf you're down, say yes!\n\nWant to keep the reminders between us? Say remind me!"
				
				pOutgoing = message
				sheet.update_cell(cnt+1, 3, "yes") # intro
				sheet.update_cell(cnt+1, 12, pIncoming) # previous incoming
				sheet.update_cell(cnt+1, 13, pOutgoing) # previous outgoing
				sheet.update_cell(cnt+1, 14, now) # last sent message
			else:
				message = "Hi again! Do you want your friends to help you remember to vote? If so, say yes! Otherwise, say remind me to keep reminders between us"

				pOutgoing = message
				sheet.update_cell(cnt+1, 3, "yes") # intro
				sheet.update_cell(cnt+1, 12, pIncoming) # previous incoming
				sheet.update_cell(cnt+1, 13, pOutgoing) # previous outgoing
				sheet.update_cell(cnt+1, 14, now) # last sent message
		else:
			message = "VoteBot here! Want a little help from your friends remembering to vote next month? VoteBot users that promise to text a friend on election day are the most likely to follow through.\n\nIf you're down, say yes!\n\nWant to keep the reminders between us? Say remind me!"

			pOutgoing = message
			sheet.update_cell(count+2, 1, from_number) # caller
			sheet.update_cell(cnt+2, 3, "yes") # intro
			sheet.update_cell(cnt+2, 12, pIncoming) # previous incoming
			sheet.update_cell(cnt+2, 13, pOutgoing) # previous outgoing
			sheet.update_cell(cnt+2, 14, now) # last sent message
			sheet.update_cell(cnt+2, 16, electionday) # last sent message

		

	############################
	### End Bot Logic ##########
	############################

	### Use twilio message verb to send message from same number it was sent to
	resp = MessagingResponse()
	resp.message(message)

	### returned string isn't used for anything
	return str(resp)


if __name__ == "__main__":
	app.run(debug=False)
