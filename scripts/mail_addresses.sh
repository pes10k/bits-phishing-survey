#!/bin/bash
if [[ -z $1 ]]; then
  echo "Usage $0 <path to addresses>"
  exit;
fi

for EMAIL in `cat $1`; do
  ./mail.py $EMAIL;
  sleep 1;
done
