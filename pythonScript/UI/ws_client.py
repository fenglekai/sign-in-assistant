# -*- coding: UTF-8 -*-
import threading
import websocket
import time
import fetch_sign_in
import private_config
from logger import logger


def get_config():
    config = private_config.read_config()
    global HTTP_PROXY
    global USER_LIST
    HTTP_PROXY = config["HTTP_PROXY"]
    USER_LIST = config["USER_LIST"]


PY_KEY = "[python]"
TASK_END = "任务结束"


def send_msg(msg, ws=None):
    print(msg)
    logger.info(msg)
    if ws:
        ws.send(msg)


def on_message(ws, message):
    print(f"{PY_KEY} message: {message}")
    config = private_config.read_config()
    user_list = config["USER_LIST"]
    msg_split = message.split(" ")
    print(msg_split)
    username = msg_split[1]
    date_range = []
    if len(msg_split) == 3:
        date = msg_split[2].split("-")
        date_range = [date[0], date[1]]
    send_msg(f"{PY_KEY} 当前查询用户: {username}", ws)
    user_list = [user for user in USER_LIST if user["username"] == username]
    if len(user_list) == 0:
        send_msg(f"{PY_KEY} 需要查询的用户不存在后台，请联系管理员添加", ws)
        send_msg(f"{PY_KEY} {TASK_END}", ws)
        return
    send_msg(f"{PY_KEY} 任务开始", ws)
    fetch_sign_in.fetch_sign_in_list(user_list, ws, date_range)
    send_msg(f"{PY_KEY} {TASK_END}", ws)


def on_error(ws, error):
    send_msg(f"{PY_KEY} Error: {error}", ws)
    send_msg(f"{PY_KEY} {TASK_END}", ws)


def on_close(ws, close_status_code, close_msg):
    send_msg(f"{PY_KEY} 连接关闭")
    if manual_close != True:
        send_msg(f"{PY_KEY} 尝试重新连接")
        time.sleep(3)
        connection(console_redirect)


def on_open(ws):
    send_msg(f"{PY_KEY} 连接成功", ws)


ws = websocket.WebSocketApp(
    "wss://foxconn.devkai.site/api",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
# websocket.enableTrace(True)


manual_close = False


def run():
    get_config()
    proxy = HTTP_PROXY.split("http://")[1]
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
        proxy_type="http",
        http_proxy_host=ip,
        http_proxy_port=port,
        http_proxy_auth=(username, password),
    )


def connection(consoleRedirect=None):
    global console_redirect
    console_redirect = consoleRedirect
    global connectionThread
    connectionThread = threading.Thread(target=run, daemon=True)
    connectionThread.start()


def disconnection():
    global manual_close
    manual_close = True
    ws.keep_running = False
    ws.close()
    send_msg(f"{PY_KEY} 连接关闭")
    # connectionThread.join()


if __name__ == "__main__":
    run()
