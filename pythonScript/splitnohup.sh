#!/bin/bash
ps -ef | grep wsClient | awk '{print $2}' | xargs kill -9
CRTDIR=$(pwd)
cp $(CRTDIR)/logs/wsClient.log $(CRTDIR)/logs/$(date +\%Y\%m\%d)ws.log
cat /dev/null > $(CRTDIR)/logs/wsClient.log
nohup /home/allen/anaconda3/envs/signinpy/bin/python -u $(CRTDIR)/wsClient.py > $(CRTDIR)/logs/wsClient.log 2>&1 &
exit