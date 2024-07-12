# -*- coding: UTF-8 -*-
import os
import websocket
import time
import fetch_sign_in
import json

current_path = os.path.abspath(__file__)
path = os.path.dirname(current_path) + "/resource"

with open("%s/static/privateConfig.json" % path) as json_file:
    config = json.load(json_file)
    USER_LIST = config["USER_LIST"]

PY_KEY = "[python]"
TASK_END = "任务结束"


def sendMsg(msg, ws=None):
    print(msg)
    if ws:
        ws.send(msg)


def on_message(ws, message):
    print(f"{PY_KEY} message: {message}")
    if "historyStart" in message:
        # msg_split = message.split("historyStart", 1)
        # username = msg_split[1]
        # user_list = [user for user in USER_LIST if user['username'] == username]
        # if len(user_list) == 0:
        #     ws.send("python: The query user list does not exist")
        #     ws.send("python: Task end")
        #     return
        # ws.send("python: Task start")
        # # 创建一个临时文件对象
        # temp_stdout = io.StringIO()
        # # 将标准输出重定向到临时文件对象
        # sys.stdout = temp_stdout
        # fetchSignIn.history_sig_in_list(username)
        # # 恢复标准输出
        # sys.stdout = sys.__stdout__
        # # 从临时文件对象中读取内容
        # output = temp_stdout.getvalue()
        # print(output)
        # ws.send("python: " + output)
        # ws.send("python: %s" % TASK_END)
        sendMsg(f"{PY_KEY} TODO", ws)
    if "queryStart" in message:
        msg_split = message.split("queryStart")
        username = str(msg_split[1]).replace(" ", "")
        sendMsg(f"{PY_KEY} 当前查询用户: {username}", ws)
        user_list = [user for user in USER_LIST if user["username"] == username]
        if len(user_list) == 0:
            sendMsg(f"{PY_KEY} 需要查询的用户不存在后台，请联系管理员添加", ws)
            sendMsg(f"{PY_KEY} {TASK_END}", ws)
            return
        sendMsg(f"{PY_KEY} 任务开始", ws)
        # temp_stdout = io.StringIO()
        # sys.stdout = temp_stdout
        fetch_sign_in.today_sign_in_list(user_list, ws)
        # if console_redirect != None:
        #     sys.stdout = console_redirect
        # else:
        #     sys.stdout = sys.__stdout__
        # output = temp_stdout.getvalue()
        # sendMsg(f"{PY_KEY}\n{output}", ws)
        sendMsg(f"{PY_KEY} {TASK_END}", ws)


def on_error(ws, error):
    sendMsg(f"{PY_KEY} Error: {error}", ws)
    sendMsg(f"{PY_KEY} {TASK_END}", ws)


def on_close(ws, close_status_code, close_msg):
    sendMsg(f"{PY_KEY} 连接关闭, 尝试重新连接")
    time.sleep(3)
    connection(console_redirect)


def on_open(ws):
    sendMsg(f"{PY_KEY} 连接成功", ws)


def connection(consoleRedirect=None):
    global console_redirect
    console_redirect = consoleRedirect
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        "wss://foxconn.devkai.site/api",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    proxy = config["HTTP_PROXY"].split("http://")[1]
    if "@" in proxy:
        user_add = proxy.split("@")
        if ":" in user_add[0]:
            usr_pas = user_add[0].split(":")
            username = usr_pas[0]
            password = usr_pas[1]
        proxy = user_add[1]
        if ":" in user_add[1]:
            ip_port = proxy.split(":")
            ip = ip_port[0]
            port = ip_port[1]

    ws.run_forever(
        reconnect=5,
        proxy_type="http",
        http_proxy_host=ip,
        http_proxy_port=port,
        http_proxy_auth=(username, password),
    )


if __name__ == "__main__":
    connection(console_redirect)
