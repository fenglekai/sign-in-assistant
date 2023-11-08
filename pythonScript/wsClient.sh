#!/bin/bash
#ps -ef | grep wsClient | awk '{print $2}' | xargs kill -9
cd /home/allen/Documents/flk-code/sign-in-assistant/pythonScript
nohup /home/allen/anaconda3/envs/signinpy/bin/python -u /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/wsClient.py > /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/logs/wsClient.log 2>&1 &
exit