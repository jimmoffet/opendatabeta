@app.route("/ref/<string:refcode>", methods=["POST", "GET"])
def renderLogin(refcode):
	refname=''
	random.seed( str(time.time()).replace('.','') )
	if refcode:
		refname = refcode
	else:
		refcode = random.randint(100000000, 999999999)
	return render_template('index.html', refcode=refcode, refname=refname)