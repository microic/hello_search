import sys, time, re

from datetime import datetime
from elasticsearch import Elasticsearch

import urllib

def query_url(url, timeout=8):
	html = None
	try:
		with urllib.request.urlopen(url, timeout=timeout) as res:
			html = res.read().decode('utf-8') 
	except Exception as e:
		# print(url, e)
		pass
	return html

# 4 users are watching this repository
# 70 users starred this repository
# 15 users forked this repository

def parse_github(addr="", branch="master"):
	url = "https://github.com/%s/tree/%s" % (addr, branch)
	html = query_url(url)
	watch, star, fork, desc = None, None, None, None

	if html is None: 
		return (watch, star, fork, desc)
	# print(url)
	r = re.search(r"(\d{1,8}) [\S]+ [\S]+ watching this repository", html)
	if r is not None: watch = int(r.group(1))
	r = re.search(r"(\d{1,8}) [\S]+ starred this repository", html)
	if r is not None: star = int(r.group(1))
	r = re.search(r"(\d{1,8}) [\S]+ forked this repository", html)
	if r is not None: fork = int(r.group(1))
	r = re.search(r"itemprop=\"about\">[\s]*([^<]+)", html)
	if r is not None: desc = r.group(1)

	return (watch, star, fork, desc)

def parse_content(repo):
	url = "https://raw.githubusercontent.com/%s/%s/README.md" % (repo.addr, repo.branch)
	repo.content = query_url(url)

	if repo.content is None: 
		url = "https://raw.githubusercontent.com/%s/%s/readme.md" % (repo.addr, repo.branch)
		repo.content = query_url(url)

	if repo.content is None: 
		url = "https://raw.githubusercontent.com/%s/%s/Readme.md" % (repo.addr, repo.branch)
		repo.content = query_url(url)
	
	if repo.content is None: 
		url = "https://raw.githubusercontent.com/%s/%s/README.textile" % (repo.addr, repo.branch)
		repo.content = query_url(url)

	if repo.content is None: 
		url = "https://raw.githubusercontent.com/%s/%s/README.rst" % (repo.addr, repo.branch)
		repo.content = query_url(url)

	if repo.content is None: 
		url = "https://raw.githubusercontent.com/%s/%s/README" % (repo.addr, repo.branch)
		repo.content = query_url(url)

# parse_github("microic/niy")
# sys.exit()

class RepoClass():
	def __init__(self, addr="", branch="master", desc="", star=0, watch=0, fork=0, content=""):
		self.addr = addr
		self.branch = branch
		self.desc = desc
		self.star = star
		self.watch = watch
		self.fork = fork
		self.content = content
		self.timestamp = 0

class EsRepo():
	def __init__(self):
		self._host = "140.82.17.30"
		self._index = "index_repo"
		self._doc_type = "type_repo"
		self._client = Elasticsearch(host="140.82.17.30")
	
	def search(self, q, fields=["desc", "content"]):
		res = self._client.search(
			index=self._index,doc_type=self._doc_type,
			size=50,
			filter_path=['hits.hits._id', 'hits.hits._score', 'hits.hits._source.desc',
			'hits.hits._source.star'],
			body={"query": 
					{"multi_match": {
	              		"query": q,
	              		"fields": fields}
	              	}
	             })
		# print(res)
		# for hit in res['hits']['hits']:
		# 	print(hit['_id']) 
			# hit["_source"]['desc']
		return res

	def get(self, addr, branch="master"):
		id = addr + '->' + branch
		res = self._client.get(index=self._index, doc_type=self._doc_type, id=id, ignore=404)
		
		repo = RepoClass(addr, branch=branch)
		if res['found'] is not True: return repo

		repo.desc = res['_source']['desc']
		repo.star = res['_source']['star']
		repo.watch = res['_source']['watch']
		repo.fork = res['_source']['fork']
		repo.content = res['_source']['content']
		repo.timestamp = res['_source']['timestamp']

		return repo

	def delete(self, addr, branch="master"):
		id = addr + '->' + branch
		res = self._client.delete(index=self._index, doc_type=self._doc_type, id=id, ignore=404)
		
	def insert(self, repo):
		id = repo.addr + '->' + repo.branch

		if repo.timestamp == 0:
			parse_content(repo)

			if repo.content is None: 
				print(id, "error")
				return False

			repo.watch, repo.star, repo.fork, repo.desc = parse_github(repo.addr, repo.branch)
			if repo.watch is None or repo.star is None or repo.fork is None:
				# return False
				print("  ", id, (repo.watch, repo.star, repo.fork, repo.desc))
				return False
			else:
				if repo.desc is None: repo.desc = ""
				repo.desc = repo.desc.strip()

			# print(repo.content)
			# sys.exit()

			repo.timestamp = int(time.time())

			print(id, "ok")

		self._client.index(index=self._index, doc_type=self._doc_type, id=id, 
			body={
				"desc": repo.desc,
				"star": repo.star,
				"watch": repo.watch,
				"fork": repo.fork,
				"content": repo.content,
				"timestamp": repo.timestamp,
			})	

		return True

if __name__ == '__main__':
	er = EsRepo()
	repo = RepoClass(addr="microic/niy")
	er.insert(repo)
	# repo = er.get("microic/niy")
	# print(repo.__dict__)
	hits = er.search("tensorflow")
	print(hits)