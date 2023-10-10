## quick start
conda activate signinpy

pipenv shell

pipenv run python fetchSignIn.py

/usr/bin/chromedriver

sudo nano /etc/crontab

/home/allen/.local/share/virtualenvs/pythonScript-2zlRQx9n/bin/python
/home/allen/anaconda3/envs/signinpy/bin/python

## 离线包下载与安装
pip freeze > requirements.txt

cd ./packages

pip wheel -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

cd ..

pip install --no-index --find-links=./packages -r requirements.txt

## 后台运行
$ nohup python -u ./wsClient.py > ./logs/wsClient.log 2>&1 &

$ ps aux|grep wsClient

$ ps -ef | grep wsClient | awk '{print $2}' | xargs kill -9

@reboot root cd /home/allen/Documents/flk-code/sign-in-assistant/pythonScript && nohup /home/allen/anaconda3/envs/signinpy/bin/python -u ./wsClient.py > ./logs/wsClient.log 2>&1

## 定时任务
*/10 7,8,9,10,17,18,19,20,21   * * 1-5   root    cd /home/allen/Documents/flk-code/sign-in-assistant/pythonScript && /home/allen/anaconda3/envs/signinpy/bin/python ./fetchSignIn.py >> /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/logs/$(date +\%Y\%m\%d)cron.log 2>&1

## 日志分割
0 0 * * * root /home/allen/Documents/flk-code/sign-in-assistant/pythonScript/splitnohup.sh