from flask import Flask, request, redirect, jsonify, render_template
from twilio.twiml.messaging_response import MessagingResponse
from scrape import scrape, ping, people, pLayer
import random
import threading
import datetime

app = Flask(__name__)

@app.route("/")
def hello():
	out = ''
	try:
		sheet = people()
		out = ' Gspread connection was successful.'
	except:
		out = ' FIX MEEEEEEEEEEEEEEEEEEEEEE!!!!.'
	out = "Hello World!" + out
	return out

@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)

@app.route("/api")
def serve_schedule():
	schedule = scrape('http://cambridgema.iqm2.com/Citizens/Detail_LegalNotice.aspx?ID=1008')
	return jsonify(schedule)

@app.route("/monkey2", methods=['GET', 'POST'])
def hello_monkey2():
	"""Respond and greet the caller by name."""

	now = datetime.datetime.now()
	now = now.replace(second=0, microsecond=0)
	
	# test = scrape('http://cambridgema.iqm2.com/Citizens/Detail_LegalNotice.aspx?ID=1008')
	# nextmtg = test[0]

	# peoples = people()
	# sheet = pLayer()

	# count = len(peoples)

	message = "Hi Beta Tester, I'm EngagementBot."
	message = message + ' ' + "I can send you reminders about stuff you want to remember. Right now, I can offer two sets of reminders." + ' For bicycle advocacy, say bikes, and for affordable housing, say housing. You can say stop or unsubscribe at any time.'

	intro = 'no'
	sub = 'no'
	resub  = 'no'
	unsub = 'no'
	monthly = 'no'
	weekly = 'no'
	pIncoming = ''
	pOutgoing = ''

	# GET ROW NUMBER OF IDENTIFIED PERSON

	# this is a string
	incoming = request.values.get('Body', None)
	from_number = request.values.get('From', None)

	cnt = 0
	# for key, val in peoples.items():
	# 	cnt += 1
	# 	if key == from_number:
	# 		break

	incoming = incoming.lower()
	pIncoming = incoming

	bikeevents = ["MassBike is hosting EnMass - A 1 Day Kick-Off Ride for the Cycle Massachusetts State Bike Tour on Saturday, August 05, 2017 at 08:00 AM at Stoneleigh Burnham School in Greenfield, MA. Here's the description: The 2nd Annual EnMass ride will be held Saturday August 5, 2017. The event is held in partnership with Cycle Massachusetts, a seven-day bicycle odyssey that continues on for the rest of the... http://www.massbike.org/calendar","Boston Cyclists Union is hosting Dorchester Bike & Brew 2017 on Wednesday, September 13th at 5pm at Peabody Square Ashmont, Dorchester Center. Here's the description: The Dorchester Bike & Brew 2017 is a family friendly community festival designed to showcase the growing cycling community in #Dorchester and the burgeoning Boston brewery scene, along with food trucks, live music, DIY bike repair, giveaways, etc. The event is held on Peabody Square West Plaza, and a small portion of Talbot Ave (between Dorchester and Welles Ave) closed to vehicular traffic for the duration of the festival. It is free to attend, with food and beverages available for individual purchase. Music: We will again feature a fun for all ages opening act, followed by two sets with a local band to help us get our groove on. Details TBD. Interested in the gig? Contact us! Food Trucks: We plan to... See More https://www.facebook.com/bostoncyclistsunion/"]
	bikecounter = 0
	nextbike = bikeevents[bikecounter]

	houseevents = ["A Better Cambridge is hosting ABC July Meeting: Volpe Redevelopment & North South Rail Link on Monday, July 17th, 6:30pm at Ray and Maria Stata Center, 32 Vassar Street, Cambridge, Massachusetts 02139. Here's the description: This week MIT submitted a zoning petition for their major redevelopment of the Volpe site in Kendall Square. Their proposal includes up to 1,400 housing units, a focus on locally-owned retail, and potentially the tallest residential building in Cambridge. We invite you to hear from and ask questions of MIT representatives about their proposed development at the next ABC General Meeting. https://www.facebook.com/ABetterCambridge/","Cambridge City Council is hosting Ordinance Committee Meeting on 42949.625 at Sullivan Chamber. Here's the description: The Ordinance Committee will conduct a public hearing to discuss a zoning petition by the Massachusetts Institute of Technology to create a new Planned Unit Development Overlay District (PUD-7) over the area known as the Volpe National Transportation Systems Center site in Kendall Square. https://cambridgema.iqm2.com/Citizens/Calendar.aspx?From=1/1/2017&To=12/31/2017"]
	housecounter = 0
	nexthouse = houseevents[housecounter]

	if 'bikes' in incoming:
		message = "Great! I'll send you a reminder a couple days before each events. To scroll through upcoming events, say next."
		intro = '1'

	elif 'bicycle' in incoming:
		message = "Great! I'll send you a reminder a couple days before each events. To scroll through upcoming events, say next."
		intro = '1'

	elif 'housing' in incoming:
		message = "Great! I'll send you a reminder a couple days before each events. To scroll through upcoming events, say next."
		intro = '1'

	elif 'next' in incoming:
		preface = "Sure thing! Here's the next event: "
		meeting = houseevents[housecounter]
		message = preface+meeting
		housecounter+=1
		if housecounter > 1:
			housecounter = 0

	else:
		message = "Hi Beta Tester, I'm EngagementBot."
		message = message + ' ' +  "I can send you reminders about stuff you want to remember. Right now, I can offer two sets of reminders." + ' For bicycle advocacy, say bikes, and for affordable housing, say housing. You can say stop or unsubscribe at any time.'
		# # ADD NEW LINE TO SHEET
		# pOutgoing = message
		# #intro = 'yes'
		# #newline = [str(from_number),'unknown','unknown',intro,sub,resub,unsub,monthly,weekly,pIncoming,pOutgoing]
		# #sheet.insert_row(newline, count+2)
		# sheet.update_cell(count+2, 1, from_number)
		# sheet.update_cell(count+2, 4, "yes")
		# #sheet.update_cell(cnt+1, 9, "yes")
		# sheet.update_cell(count+2, 10, pIncoming)
		# sheet.update_cell(count+2, 11, pOutgoing)

		
	resp = MessagingResponse()
	resp.message(message)

	return str(resp)

@app.route("/monkey", methods=['GET', 'POST'])
def hello_monkey():
	"""Respond and greet the caller by name."""

	now = datetime.datetime.now()
	now = now.replace(second=0, microsecond=0)
	
	test = scrape('http://cambridgema.iqm2.com/Citizens/Detail_LegalNotice.aspx?ID=1008')
	nextmtg = test[0]

	peoples = people()
	sheet = pLayer()

	count = len(peoples)

	message = "Hi Beta Tester, I'm the City Council MeetingBot."
	message = message + ' ' + 'I only do one thing, but I do it well. For a weekly reminder say "weekly", for monthly say "monthly" and to see only the very next meeting say "next". You can say "stop" or "unsubscribe" at any time.'

	intro = 'no'
	sub = 'no'
	resub  = 'no'
	unsub = 'no'
	monthly = 'no'
	weekly = 'no'
	pIncoming = ''
	pOutgoing = ''

	# GET ROW NUMBER OF IDENTIFIED PERSON

	# this is a string
	incoming = request.values.get('Body', None)
	from_number = request.values.get('From', None)

	cnt = 0
	for key, val in peoples.items():
		cnt += 1
		if key == from_number:
			break

	incoming = incoming.lower()
	pIncoming = incoming

	if 'start' in incoming:
		message = "Welcome back! MeetingBot here, you may remember me. If not, here's my deal. I only do one thing, but I do it well. For a weekly reminder of City Council meetings say weekly, for monthly say monthly, and to see the very next meeting say next. You can say stop or unsubscribe at any time."
		intro = '1'

	elif 'weekly' in incoming:
		lastsent = now - datetime.timedelta(days=7)
		lastsent = lastsent.replace(second=0, microsecond=0)
		message = "I'm on it. I'll send you a text once a week with details for the next two meetings. You can switch to monthly or stop getting alerts at any time, just say monthly or stop."
		weekly = 'yes'
		intro = 'yes'
		pOutgoing = message
		if from_number in peoples:
			sheet.update_cell(cnt+1, 5, "yes")
			sheet.update_cell(cnt+1, 8, "no")
			sheet.update_cell(cnt+1, 9, "yes")
			sheet.update_cell(cnt+1, 10, pIncoming)
			sheet.update_cell(cnt+1, 11, pOutgoing)
			sheet.update_cell(cnt+1, 13, lastsent)
		else:
			sheet.update_cell(count+2, 1, from_number)
			sheet.update_cell(count+2, 4, "yes")
			sheet.update_cell(count+2, 5, "yes")
			sheet.update_cell(count+2, 8, "no")
			sheet.update_cell(count+2, 9, "yes")
			sheet.update_cell(count+2, 10, pIncoming)
			sheet.update_cell(count+2, 11, pOutgoing)
			sheet.update_cell(count+2, 13, lastsent)

	elif 'monthly' in incoming:
		try:
			lastsent = now - datetime.timedelta(days=365/12)
			lastsent = lastsent.replace(second=0, microsecond=0)
		except:
			print('Setting lasttime to one month prior has failed')
			lastsent = now - datetime.timedelta(days=30)
			lastsent = lastsent.replace(second=0, microsecond=0)
		message = "I'm on it. I'll send you a text the day before the first meeting of each month with details for all of that month's meetings. You can switch to weekly or stop getting alerts at any time, just say weekly or stop."
		monthly = 'yes'
		intro = 'yes'
		pOutgoing = message
		if from_number in peoples:
			sheet.update_cell(cnt+1, 5, "yes")
			sheet.update_cell(cnt+1, 8, "yes")
			sheet.update_cell(cnt+1, 9, "no")
			sheet.update_cell(cnt+1, 10, pIncoming)
			sheet.update_cell(cnt+1, 11, pOutgoing)
			sheet.update_cell(cnt+1, 12, lastsent)
		else:
			sheet.update_cell(count+2, 1, from_number)
			sheet.update_cell(count+2, 4, "yes")
			sheet.update_cell(count+2, 5, "yes")
			sheet.update_cell(count+2, 8, "yes")
			sheet.update_cell(count+2, 9, "no")
			sheet.update_cell(count+2, 10, pIncoming)
			sheet.update_cell(count+2, 11, pOutgoing)
			sheet.update_cell(count+2, 12, lastsent)

	elif 'next' in incoming:
		preface = "Sure thing! Here's the next meeting: "
		meeting = nextmtg['date']+" "+nextmtg['time']+" "+nextmtg['agenda']
		message = preface + meeting
		intro = 'yes'
		pOutgoing = message
		if from_number in peoples:
			sheet.update_cell(cnt+1, 4, intro)
			sheet.update_cell(cnt+1, 10, pIncoming)
			sheet.update_cell(cnt+1, 11, pOutgoing)
		else:
			sheet.update_cell(count+2, 1, from_number)
			sheet.update_cell(count+2, 4, "yes")
			sheet.update_cell(count+2, 10, pIncoming)
			sheet.update_cell(count+2, 11, pOutgoing)

	else:
		if from_number in peoples:
			# write a cheeky message here cause they're trying to chat you up (or we have them on a member list)
			if peoples[from_number][2] == 'yes':
				message = "Hey " + peoples[from_number][1] + '... Are you trying to chat me up? I told you that I only do meeting alerts :) Say weekly or monthly for reminders, or next, to see the next meeting. Say stop to unsubscribe immediately.'
				intro = 'yes'
				pOutgoing = message
				sheet.update_cell(cnt+1, 4, intro)
				sheet.update_cell(cnt+1, 10, pIncoming)
				sheet.update_cell(cnt+1, 11, pOutgoing)
			else:
				message = "Hi " + peoples[from_number][1] + ", I'm the City Council MeetingBot. Is it creepy that I know who you are?"
				message = message + ' ' + 'I only do one thing, but I do it well. For a weekly reminder say "weekly", for monthly say "monthly" and to see only the very next meeting say "next". You can say "stop" or "unsubscribe" at any time.'
				intro = 'yes'
				pOutgoing = message
				sheet.update_cell(cnt+1, 4, intro)
				sheet.update_cell(cnt+1, 10, pIncoming)
				sheet.update_cell(cnt+1, 11, pOutgoing)
		else:
			message = "Hi Beta Tester, I'm the City Council MeetingBot."
			message = message + ' ' + 'I only do one thing, but I do it well. For a weekly reminder say "weekly", for monthly say "monthly" and to see only the very next meeting say "next". You can say "stop" or "unsubscribe" at any time.'
			# ADD NEW LINE TO SHEET
			pOutgoing = message
			#intro = 'yes'
			#newline = [str(from_number),'unknown','unknown',intro,sub,resub,unsub,monthly,weekly,pIncoming,pOutgoing]
			#sheet.insert_row(newline, count+2)
			sheet.update_cell(count+2, 1, from_number)
			sheet.update_cell(count+2, 4, "yes")
			#sheet.update_cell(cnt+1, 9, "yes")
			sheet.update_cell(count+2, 10, pIncoming)
			sheet.update_cell(count+2, 11, pOutgoing)

		
	resp = MessagingResponse()
	resp.message(message)

	return str(resp)


if __name__ == "__main__":
	app.run(debug=False)
