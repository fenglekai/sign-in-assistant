rm -rf ./build ./dist ./*.spec
pyinstaller -D -w ./UI/window.py -n sign-in-assistant --add-data "./UI/resource/:./resource/"