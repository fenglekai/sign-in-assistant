ps aux | grep 'resource/static/chrome/chrome' | awk '{print $2}' | xargs kill -9
ps aux | grep 'chromedriver' | awk '{print $2}' | xargs kill -9
ps aux | grep ':30725' | awk '{print $2}' | xargs kill -9
ps aux | grep ':30726' | awk '{print $2}' | xargs kill -9