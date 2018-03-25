import json
from repo_lib import *
from flask import Flask, request 
app = Flask(__name__)

er = EsRepo()

def get(k):
	v = None
	try: v = request.args.get(k)
	except: pass
	try: v = request.form[k]
	except: pass
	return v

@app.route("/search")
def search():
	q = get('q')
	callback = get('callback')

	if q is None: return ""
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