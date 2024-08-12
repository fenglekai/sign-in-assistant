# -*- coding: UTF-8 -*-
import base64
import json
import threading
import zlib
import websocket
import time
import fetch_sign_in
import private_config
from logger import logger

console_redirect = None
config = None
current_user = ""


def get_config():
    global config
    config = private_config.read_config()
    global HTTP_PROXY
    global USER_LIST
    HTTP_PROXY = config["HTTP_PROXY"]
    USER_LIST = config["USER_LIST"]


PY_KEY = "[python]"
TASK_END = "任务结束"


def send_msg(msg, ws=None):
    global current_user
    print(msg)
    logger.info(msg)
    if ws:
        if msg == "[python]::":
            ws.send(msg)
            return
        compressed_data = zlib.compress(msg.encode("utf-8"))
        encoded_data = base64.b64encode(compressed_data).decode("utf-8")
        post_msg = {"data": f"{PY_KEY}_{encoded_data}", "userId": current_user}
        ws.send(str(post_msg))


def on_message(ws, message):
    global current_user
    web_json = json.loads(message)
    data = web_json["data"]
    send_msg(f"{PY_KEY} message: {data}")
    current_user = web_json["currentUser"]["userId"]
    # TODO 获取用户添加到页面
    # 处理查询信息
    get_config()
    user_list = config["USER_LIST"]
    msg_split = data.split(" ")
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
        if console_redirect:
            connection(console_redirect)
        else:
            run()


def on_open(ws):
    send_msg(f"{PY_KEY} 连接成功")
    send_msg(f"{PY_KEY}::", ws)


ws = websocket.WebSocketApp(
    "wss://foxconn.devkai.site/api",
    # "ws://localhost:8003/api",
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
