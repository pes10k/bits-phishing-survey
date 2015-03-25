#!/usr/bin/env python
import sys
import pymongo
import os.path
import imp 
from pprint import pprint

valid_args = ('load', 'pass', 'url-yes', 'url-no')
if len(sys.argv) != 2 or sys.argv[1] not in valid_args:
  print("Usage: {0} <{1}>".format(sys.argv[0], "|".join(valid_args)))
  sys.exit()

script_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
config = imp.load_source('config', os.path.join(root_dir, 'config.py'))

token_to_email_map = {}
for a_file in ('data/mail-hashes.txt', 'data/second-mail-hashes.txt', 'data/third-mail-hashes.txt'):
  with open(a_file, 'r') as h:
    for line in h.readlines():
      email, a_hash = line.strip().split(" ")
      token_to_email_map[a_hash] = email

email_to_sess_map = {}
h = open('data/mappings.csv', 'r')
for line in h:
  try:
    email, token = line.strip().split(" ")
  except:
    continue
  email_to_sess_map[email] = token

sess_to_group_map = {}
with open('data/install-mapping.txt', 'r') as h:
  for line in h:
    try:
      sess_id, group = line.strip().split(" ")
      sess_to_group_map[sess_id] = group
    except:
      continue

def group_for_token(token):
  email = token_to_email_map[token]
  sess_id = email_to_sess_map[email]
  group = sess_to_group_map[sess_id]
  return group

mongo_params = config.mongo_params
mongo_client = pymongo.MongoClient(mongo_params['host'], mongo_params['port'])
db = mongo_client[config.mongo_database]

if sys.argv[1] == "load":
  hashes = set(db.command({'distinct': "events", 'key': "token", "query": {"event": "loaded", "page": "userid"}})['values'])
elif sys.argv[1] == "pass":
  hashes = set(db.command({'distinct': "events", 'key': "token", "query": {"event": "password form submitted"}})['values'])
elif sys.argv[1] == "url-no":
  hashes = [str(r['token']) for r in db.events.find({"event": "submitted", "page": "survey", "did_note_url": "No"}, {'token': 1})]
elif sys.argv[1] == "url-yes":
  hashes = [str(r['token']) for r in db.events.find({"event": "submitted", "page": "survey", "did_note_url": "Yes"}, {'token': 1})]
else:
  sys.exit("Unexpected group")

for a_hash in hashes:
  try:
    print(a_hash, group_for_token(a_hash))
  except KeyError:
    continue


