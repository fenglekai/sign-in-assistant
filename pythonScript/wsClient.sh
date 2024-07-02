#!/bin/bash
#ps -ef | grep wsClient | awk '{print $2}' | xargs kill -9
CRTDIR=$(pwd)
nohup python -u $(CRTDIR)/wsClient.py > $(CRTDIR)/logs/wsClient.log 2>&1 &
exit