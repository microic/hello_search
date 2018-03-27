import sys, time, re
import urllib
from py2neo import Graph,Node,Relationship
from repo_lib import query_url

def get_user_list(addr):
	user_list = []
	for page in range(1, 10):
		url = 'https://github.com/%s/stargazers' % (addr)
		if page > 1: url += "?page=" + str(page)
		html = query_url(url)
		if html is None: 
			print(page)
			break

		for r in re.finditer(r'alt="@([\S]+?)" data-hovercard-user-id', html):
			if r is not None: 
				user_list.append(r.group(1))
			else: break

		# r = re.search(r'alt="@([\S]+?)" data-hovercard-user-id', html)
		# if r is not None: user = r.group(1)
		# 'alt="@gurusura" data-hovercard-user-id'

	return user_list
	# print(user_list, len(user_list))

# get_user_list("microic/niy")
# sys.exit()

class NeoRepo():
	def __init__(self):
		self._host = "140.82.17.30"
		self.g = Graph(
					"http://140.82.17.30", 
					username="neo4j", 
					password="123456"
				  )

	def add_user(self, user):
		n = Node("User", name=user)
		self.g.merge(n)

	def add_repo(self, repo):
		n = Node("Repo", name=repo)
		self.g.merge(n)

	def get_user(self, user):
		n = self.g.find_one("User", property_key='name', property_value=user)
		return n

	def get_repo(self, repo):
		n = self.g.find_one("Repo", property_key='name', property_value=repo)
		return n

	def add_rel(self, user, repo, rel_type):
		user = Node("User", name=user)
		repo = Node("Repo", name=repo)
		rel = Relationship(user, rel_type, repo)
		self.g.merge(rel)

	def match_user(self, user, rel_type='star'):
		if isinstance(user, str): user = self.get_user(user)
		match = self.g.match(start_node=user,bidirectional=False,rel_type=rel_type)
		return match

	def match_repo(self, repo, rel_type='star'):
		if isinstance(repo, str): repo = self.get_repo(repo)
		match = self.g.match(end_node=repo,bidirectional=False,rel_type=rel_type)
		return match

	def match_one(self, user, repo, rel_type='star'):
		if isinstance(user, str): user = self.get_user(user)
		if isinstance(repo, str): repo = self.get_repo(repo)
		match = self.g.match_one(start_node=user,end_node=repo,bidirectional=False,rel_type=rel_type)
		return match

	def suggest(self, repo):
		match_repo = self.match_repo(repo)
		count = {}
		for item_repo in match_repo:
			user = item_repo.start_node()
			# count[user['name']] = 0

			match_user = self.match_user(user)

			for item_user in match_user:
				repo_suggest = item_user.end_node()
				if repo_suggest['name'] in count:
					count[repo_suggest['name']] += 1
				else: count[repo_suggest['name']] = 1
		return (sorted(count.items(), key=lambda item:item[1], reverse=True))[1:51]

			# repos 
			# print(item.start_node(), item.end_node())

if __name__ == '__main__':
	nr = NeoRepo()
	suggest = nr.suggest("tensorflow/tensorflow")
	print(suggest)
	# nr.g.delete_all()

	# nr.add_user("microic")
	# nr.add_user("microic1")

	# nr.add_repo("niy")

	# nr.add_rel("microic", 'microic/niy', 'open')
	# nr.add_rel("microic", 'microic/niy2', 'open')
	# nr.add_rel("microic", 'tensorflow/tensorflow', 'star')

	# find = nr.g.find(label="Repo")
	# for item in find:
	# 	print(item)

	# user = nr.get_user("microic")
	# # print(user)
	# repo = nr.get_repo("niy")
	# match = nr.g.match(start_node=user,bidirectional=True,rel_type=None)
	# for item in match:
	# 	# print(item)
	# 	print(item.start_node(), item.end_node())

	# match = nr.match_repo('microic/niy')
	# for item in match:
	# 	print(item.start_node(), item.end_node())

	# match = nr.match_one("youyingyin", 'microic/niy')
	# print(match.start_node())
