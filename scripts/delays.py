#!/usr/bin/env python
import stats
import csv
import sys
import pymongo
import os.path
import imp 
from pprint import pprint

if sys.argv[1] == "good":
  mapping_file = "data/mapping-good.csv"
  dest_file = "data/delays-good.csv"
elif sys.argv[1] == "pws":
  mapping_file = "data/mapping-pws.csv"
  dest_file = "data/delays-pws.csv"
elif sys.argv[1] == "bad":
  mapping_file = "data/mapping-bad.csv"
  dest_file = "data/delays-bad.csv"
else:
  raise Exception("Must specify good or bad file")

script_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
config = imp.load_source('config', os.path.join(root_dir, 'config.py'))

install_id_to_email_map = {}
for a_file in ('data/mail-hashes.txt', 'data/second-mail-hashes.txt', 'data/third-mail-hashes.txt'):
  with open(a_file, 'r') as h:
    for line in h.readlines():
      email, a_hash = line.strip().split(" ")
      install_id_to_email_map[a_hash] = email

email_to_sess_map = {}
email_to_pws_map = {}
h = open(mapping_file, 'r')
for line in h:
  email, install_id, num_pws = line.strip().split(" ")
  email_to_sess_map[email.lower()] = install_id
  email_to_pws_map[email.lower()] = num_pws

sess_to_group_map = {}
with open('data/install-mapping.txt', 'r') as h:
  for line in h:
    sess_id, group = line.strip().split(" ")
    sess_to_group_map[sess_id] = group

def group_for_install_id(install_id):
  email = install_id_to_email_map[install_id].lower()
  sess_id = email_to_sess_map[email]
  group = sess_to_group_map[sess_id]
  return group, email_to_pws_map[email]

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

csvfile = open(dest_file, 'w')

writer = csv.writer(csvfile)
writer.writerow(['install_id', 'group', 'userid delay', 'password delay', 'num pws'])

for a_hash in hashes:
  hashes_group, num_pws = group_for_install_id(a_hash)
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

  writer.writerow([a_hash, hashes_group, userid_diff, pass_diff, num_pws])
  continue

  if hashes_group not in groups:
    groups[hashes_group] = {"pass": [], "userid": []}

  if hash_userid_delay:
    groups[hashes_group]['userid'].append(userid_diff.microseconds / float(1000000)  + userid_diff.seconds)
  
  if hash_pass_delay:
    groups[hashes_group]['pass'].append(pass_diff.microseconds / float(1000000) + pass_diff.seconds)

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

