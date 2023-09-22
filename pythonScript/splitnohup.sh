#!/bin/sh
date=`date -d "testerday" +%Y-%m-%d`
cp /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/logs/wsClient.log /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/logs/$date.log
cat /dev/null > /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/logs/wsClient.log