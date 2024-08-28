import asyncio
import errno
import os
import socket
import sys
import threading


port_file = f"app.pid"

HOST = "localhost"

def is_port_in_use(port, host=HOST):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError as e:
            return e.errno == errno.EADDRINUSE


async def worker_task(reader, writer, window):
    window.showNormal()
    window.raise_()


async def start_server(port: int, window):
    server = await asyncio.start_server(
        lambda r, w: worker_task(r, w, window), HOST, port
    )
    print(f"服务器启动,地址: {HOST}:{port}")
    async with server:
        await server.serve_forever()


async def start_client(port: int):
    reader, writer = await asyncio.open_connection(
        HOST, port)
    print(f'连接到 {HOST}:{port}')
    writer.close()

def threadFun(fn):
    asyncio.run(fn)

def check_window(window):
    if os.path.exists(port_file):
        with open(port_file, "r") as file:
            read_port = int(file.read().strip())
            threading.Thread(
                target=threadFun,
                daemon=True,
                args=(start_client(read_port),)
            ).start()
            sys.exit(1)  # 退出，因为进程已经存在
    else:
        port = 6000
        while True:
            if is_port_in_use(port):
                print(f"{port} port is already used.")
                port += 1
            else:
                break
        threading.Thread(
            target=threadFun,
            daemon=True,
            args=(start_server(port, window),)
        ).start()
        with open(port_file, "w") as file:
            file.write(str(port))
        return False


def remove_file():
    os.remove(port_file)
