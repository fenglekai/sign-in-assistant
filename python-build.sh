rm -rf ./build ./dist ./*.spec
pyinstaller -D -w pythonScript/UI/window.py -n sign-in-assistant --add-data "pythonScript/UI/resource/:./resource/" --icon=pythonScript/UI/resource/static/favicon.ico