import sys, time, re

from datetime import datetime
from elasticsearch import Elasticsearch

from repo_lib import *

def get_repo_list():
	lines = None
	with open("repo_list.txt", "r") as file:
		lines = file.readlines()
	i = 0
	while i < len(lines):
		lines[i] = lines[i].strip()
		if lines[i] == "" or lines[i][0] == "#":
			del lines[i]
		else: 
			lines[i] = lines[i].replace(" ", "")
			i += 1
	return lines

repo_list = get_repo_list()
# LINChinaNN/light-CNN
# S6Regen/Black-Swan
# createamind/vid2vid

# repo_list = ["karpathy/convnetjs", "elastic/elasticsearch", "expressjs/express"]
# print(repo_list, len(repo_list))
# sys.exit()

er = EsRepo()
for item in repo_list:
	repo = RepoClass(addr=item)
	er.insert(repo)
