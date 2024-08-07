import os
import sys
from qfluentwidgets import Dialog


pid_file = f"app.pid"


def check_window(window):
    if os.path.exists(pid_file):
        with open(pid_file, "r") as file:
            pid = int(file.read().strip())
            try:
                os.kill(pid, 0)
            except OSError:
                pass
            else:
                print(f"进程已存在, PID: {pid}")
                w = Dialog("提示", "应用已启动", window)
                w.yesButton.setText("退出")
                w.cancelButton.hide()
                if w.exec():
                    sys.exit(1)  # 退出，因为进程已经存在
    else:
        with open(pid_file, "w") as file:
            file.write(str(os.getpid()))
        return False


def remove_file():
    os.remove(pid_file)