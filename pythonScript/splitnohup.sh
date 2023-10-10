#!/bin/bash
cp /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/logs/wsClient.log /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/logs/$(date +\%Y\%m\%d)ws.log
cat /dev/null > /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/logs/wsClient.log