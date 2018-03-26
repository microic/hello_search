#!/bin/sh

# export FLASK_APP=repo_server.py 
# nohup flask run --host=0.0.0.0 1>/dev/null 2>/dev/null &

nohup /root/anaconda3/bin/python repo_server_wsgi.py 1>/dev/null 2>/dev/null &