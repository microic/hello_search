import json
from repo_lib import *
from neo_lib import *
from flask import Flask, request 
app = Flask(__name__)

er = EsRepo()
nr = NeoRepo()

def get(k):
	v = None
	try: v = request.args.get(k)
	except: pass
	try: v = request.form[k]
	except: pass
	return v

@app.route("/suggest")
def suggest():
	r = get('r')
	callback = get('callback')
	if r is None: return ""

	repos = nr.suggest(r)

	jstr = ""
	if callback is not None:
		jstr += "if(window." + callback + ")" + callback + "(";
	jstr += json.dumps(repos)
	if callback is not None:
		jstr += ")"

	return jstr

@app.route("/search")
def search():
	q = get('q')
	callback = get('callback')

	if q is None: return ""

	# hits = None
	# global er
	# try:
	# 	hits = er.search(q)
	# except:
	# 	er = EsRepo()

	hits = er.search(q)

	jstr = ""
	if callback is not None:
		jstr += "if(window." + callback + ")" + callback + "(";
	jstr += json.dumps(hits)
	if callback is not None:
		jstr += ")"

	return jstr

@app.route("/")
def index():
    return "Hi"