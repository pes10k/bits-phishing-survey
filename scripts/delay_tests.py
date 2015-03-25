#!/usr/bin/env python
from dateutil.parser import parse
import csv
import os
from pprint import pprint
from scipy import stats

pass_delays = []
userid_delays = []
all_pws = []
control = []
test = []

with open(os.path.join('data', 'delays-pws.csv'), 'r') as h:
  reader = csv.reader(h)
  is_first = False
  for row in reader:
    if not is_first:
      is_first = True
      continue
    token, group, userid_delay, password_delay, num_pws = row
    delay_val = password_delay.split(":")[-1]
    delay_ms = round(float(delay_val), 1)
    
    if group == "control":
      control.append(delay_ms)
    else:
      test.append(delay_ms)
    all_pws.append(float(num_pws))
    userid_delays.append(float(userid_delay.split(":")[-1]))
    pass_delays.append(float(password_delay.split(":")[-1]))
    


t, prob = stats.ttest_ind(control, test)
print("T-Test")
print("---")
print("t: {}".format(t))
print("prob: {}".format(prob))
print("")
test_k2, test_p = stats.normaltest(test)
control_k2, control_p = stats.normaltest(control)
print("Normality Tests\n---")
for label, p in (("test", test_p), ("control", control_p)):
  print("{}: {}".format(label, p))
print("")
print("Mann-Whitney U\n---")
print("u: {}\nprob: {}".format(*stats.mannwhitneyu(test, control, use_continuity=False)))

print("")
print("Regression (# pass vs user_id delay)\n---")
slope, intercept, r_value, p_value, std_err = stats.linregress(all_pws, userid_delays)
print("p: {}".format(p_value / 2))

print("")
print("Regression (# pass vs pass delay)\n---")
slope, intercept, r_value, p_value, std_err = stats.linregress(all_pws, pass_delays)
print("p: {}".format(p_value / 2))

