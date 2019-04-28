<a href="https://opendatabeta.herokuapp.com/"><img src="https://jamesdavidmoffet.com/images/opendatabeta/newnetwork.jpg" /></a>
<a href="#"><img src="https://jamesdavidmoffet.com/images/opendatabeta/votebot.png" /></a>
<a href="#"><img src="/meetingbot.gif" width="100%"/></a>

## OpenDataBeta
As a civic tech fellow, with funding from the Harvard Graduate School of Design Community Service Fellowship, I developed a suite of software tools for strengthening municipal civic engagement in collaboration with City Councillor Nadeem Mazen and his design firm, Nimblebot. We did intensive user research with civil society organizations and ultimately created tools that allow them to easily pull data from government websites and deliver it to their constituencies via inexpensive, low-touch, high-engagement channels, such as SMS, with almost no technical volunteer labor.

Note: MeetingBot and VoteBot require an account at https://www.twilio.com. The cost as of the deployment of this project was $1/number (MeetingBot and VoteBot each require one number) and $0.0075/SMS. 

Note: You may want to delete the clientsecret.json file that controls access to your google sheet if you plan to publish a copy of this repository. Making that file public is equivalent to the sharing option: "Anyone with a link can edit."

Opendatabeta was designed to be easily adapted and deployed for free on heroku.

# Install and run project
    
    git clone https://github.com/jimmoffet/opendatabeta.git
    cd opendatabeta
    pip install -r requirements.txt
    python app.py # run on 127.0.0.1:5000

Check out the open campaign finance data viz: https://opendatabeta.herokuapp.com/
