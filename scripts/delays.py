#!/usr/bin/env python
import stats
import csv
import sys
import pymongo
import os.path
import imp 
from pprint import pprint

script_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
config = imp.load_source('config', os.path.join(root_dir, 'config.py'))

token_to_email_map = {}
for a_file in ('mail-hashes.txt', 'second-mail-hashes.txt', 'third-mail-hashes.txt'):
  with open(a_file, 'r') as h:
    for line in h.readlines():
      email, a_hash = line.strip().split(" ")
      token_to_email_map[a_hash] = email

email_to_sess_map = {}
h = open('email-to-install-mapping.txt', 'r')
for line in h:
  try:
    email, time, token = line.strip().split(" ")
  except:
    continue
  email_to_sess_map[email] = token

sess_to_group_map = {}
with open('install-mapping.txt', 'r') as h:
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

def closest_diff(starts, ends):
  if len(starts) == 0 or len(ends) == 0:
    return None
  start_ts = [s['timestamp'] for s in starts]
  ends_ts = [e['timestamp'] for e in ends]
  max_end = max(ends_ts)
  true_start = max([s for s in start_ts if s < max_end])
  return max_end - true_start

def userid_delay(a_hash):
  starts = list(db.events.find({"token": a_hash, "page": "userid", "event": "loaded"}, {"timestamp": 1}))
  ends = list(db.events.find({"token": a_hash, "page": "userid", "event": "userid entered"}, {"timestamp": 1}))
  return starts, ends 

def pass_delay(a_hash):
  starts = list(db.events.find({"token": a_hash, "page": "password", "event": "loaded"}, {"timestamp": 1}))
  ends = list(db.events.find({"token": a_hash, "page": "password", "event": "password entered"}, {"timestamp": 1}))
  return starts, ends

hashes = set(db.command({'distinct': "events", 'key': "token", "query": {"event": "loaded", "page": "userid"}})['values'])

groups = {}

# with open('data.csv', 'w') as csvfile:
# 
#   writer = csv.writer(csvfile)
#   writer.writerow(['token', 'group', 'userid delay', 'password delay'])

for a_hash in hashes:
  hashes_group = group_for_token(a_hash)
  if hashes_group not in ('control', 'reauth'):
    continue

  hash_userid_delay = userid_delay(a_hash)
  hash_pass_delay = pass_delay(a_hash)

  userid_starts, userid_ends = hash_userid_delay
  pass_starts, pass_ends = hash_pass_delay

  userid_diff = closest_diff(*hash_userid_delay)
  pass_diff = closest_diff(*hash_pass_delay)

  if not userid_diff or not pass_diff:
    continue

  # writer.writerow([a_hash, hashes_group, userid_diff, pass_diff])
  # continue

  if hashes_group not in groups:
    groups[hashes_group] = {"pass": [], "userid": []}

  if hash_userid_delay:
    groups[hashes_group]['userid'].append(userid_diff.microseconds / float(1000000)  + userid_diff.seconds)
  
  if hash_pass_delay:
    groups[hashes_group]['pass'].append(pass_diff.microseconds / float(1000000) + pass_diff.seconds)
  # sys.exit()
measures = (("Mean", stats.mean), ("Min", min), ("Max", max),
            ("St Dev", stats.stdev), ("Sum", sum),
            ("Count", len))


for g, vals in groups.items():
  if g not in ("control", "reauth"):
    continue
  print(g)
  print("===")
  print("")
  userid_vals = [v for v in vals['userid'] if v < 600]
  pass_vals = [v for v in vals['pass'] if v < 600]

  for title, values in (("User ID", userid_vals), ("Password", pass_vals)):
    print(title)
    print("---")
    print("")
    for measure_name, measure_func in measures:
      print(" * {}: {}".format(measure_name, measure_func(values)))
    print("")
  print("\n")

