#!/bin/bash

processes=$(ps x)
if echo ${processes} | grep -q "python server.py"; then
  echo "Already running."
  exit 0
fi

while true; do
  cd /home/pi/nebree82/nebree8
  date_today=$(date +%Y%m%d$)
  filepath="/home/pi/nebree82/nebree8/logs/server_${date_today}"
  python server.py &>> ${filepath}.stdout
  sleep 1.0
done
