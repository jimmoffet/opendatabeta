# /usr/bin/env python
# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import Client
from twilio_creds import account_sid, auth_token
from scrape import scrape, ping, people, pLayer
import sys
import datetime

# Find these values at https://twilio.com/user/account
# Find these values at https://twilio.com/user/account
# account_sid = 'XXXXXXXXXXX" # PUT YOUR TWILIO ACCOUNT_SID IN twilio_creds.py FILE
# auth_token = 'XXXXXXXXXXX" # PUT YOUR TWILIO_AUTH TOKEN IN twilio_creds.py FILE


### google drive api freaked out trying to read back microseconds from the sheet ###
now = datetime.datetime.now()
now = now.replace(second=0, microsecond=0)
lastsent = now - datetime.timedelta(days=7)
lastsent = lastsent.replace(second=0, microsecond=0)



go = True
row = 1
sheet = pLayer()
subscriber_list = []

while go:
	subscriber = []
	num = sheet.cell(row, 1).value
	monthly = sheet.cell(row, 8).value 
	weekly = sheet.cell(row, 9).value
	monthly_last = sheet.cell(row, 12).value 
	weekly_last = sheet.cell(row, 13).value 

	if len(num) < 2:
		break
	else:
		if weekly == 'yes' or monthly == 'yes':
			subscriber = [num,weekly,monthly,weekly_last,monthly_last,row]
			subscriber_list.append(subscriber)
			# sheet.update_cell(row, 12, lastsent)
			# sheet.update_cell(row, 13, lastsent)
		row += 1


### check persistent layer for last sent date, if more than 7 days, send and update last sent date ###

### Currently the send time/day is set when you subscribe and will send every 7 days after that ###

test = scrape('http://cambridgema.iqm2.com/Citizens/Detail_LegalNotice.aspx?ID=1008')
nextmtg = test[0]

preface = "MeetingBot here with your weekly reminder. The next council meeting is "
meeting = nextmtg['date']+" at "+nextmtg['time']+". Here are the details: "+nextmtg['agenda']
reminder = preface + meeting

#print('send_sms ran without sending')
### Iterate through subscribers ###
cnt = 0
for subscriber in subscriber_list:
	from_num = '+'+subscriber[0]
	now = datetime.datetime.now()
	now = now.replace(second=0, microsecond=0)
	if len(subscriber[3]) < 2:
		lastsent = now - datetime.timedelta(days=7)
		lastsent = lastsent.replace(second=0, microsecond=0)

	test = datetime.datetime.strptime(subscriber[3],"%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=7)
	print('Found +17733541500')
	print(from_num)
	if test < now:
		message = client.api.account.messages.create(to=from_num, from_="+16172497881", body=reminder)

		### need to add row to subscriber list so we can update the correct row

		sheet.update_cell(subscriber[5], 12, now)
		sheet.update_cell(subscriber[5], 13, now)
		cnt += 1


print('send_sms sent "'+ str(reminder) +'" to '+ str(cnt) + ' numbers')

# check for next date to send, if today send, then change date to send 
# Loop through numbers that need to recieve the message