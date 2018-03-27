#!/root/anaconda3/bin/python

import sys, time, re
import urllib
from neo_lib import *
from repo_lib import *

es = EsRepo()
nr = NeoRepo()
# nr.g.delete_all()

res = es.search_all()
hits = res['hits']['hits']

for hit in hits:
	if hit['_source']['star'] <= 0: continue
	
	_id = hit['_id'].split('->')
	print(_id[0], hit['_source']['star'])

	user_list = get_user_list(_id[0])
	print(len(user_list))

	for user in user_list:
		nr.add_rel(user, _id[0], "star")

	# sys.exit()


