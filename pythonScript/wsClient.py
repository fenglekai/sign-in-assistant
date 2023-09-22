import websocket
import asyncio
import time
import fetchSignIn
import io
import sys
from interval import Interval
import base64

def on_message(ws, message):
    print(message)
    if "pythonStart" in message:
        ws.send("python: task start")
        # 创建一个临时文件对象
        temp_stdout = io.StringIO()
        # 将标准输出重定向到临时文件对象
        sys.stdout = temp_stdout
        fetchSignIn.main()
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        # 从临时文件对象中读取内容
        output = temp_stdout.getvalue()
        print(output)
        # 当前时间
        now_localtime = time.strftime("%Y%m%d", time.localtime())
        # 当前时间（以时间区间的方式表示）
        now_time = Interval(now_localtime, now_localtime)
        ws.send("python: " + output)

def on_error(ws, error):
    ws.send("python: %s" % error)
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
    ws.send("python: Opened connection")

def connection():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://foxconn.devkai.site/api",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(reconnect=5, proxy_type="http", http_proxy_host="10.191.131.156", http_proxy_port="3128", http_proxy_auth=("24598", "b7ShqAYp"))


if __name__ == "__main__":
    try:
        print("wsClient start")
        connection()
    except Exception as e:
        print("连接失败: ",e)
        time.sleep(5)
