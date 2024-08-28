# coding:utf-8
import sys

from PyQt6.QtCore import Qt, QUrl, QEventLoop, QTimer, QSize
from PyQt6.QtGui import QIcon, QDesktopServices, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMenu,
    QSystemTrayIcon,
)
import psutil
from qfluentwidgets import (
    NavigationItemPosition,
    MSFluentWindow,
    SubtitleLabel,
    setFont,
)
from qfluentwidgets import FluentIcon as FIF, SplashScreen, Dialog
from home import HomeInterface
from setting import SettingInterface
from check_window import check_window, remove_file, set_window
from use_path import local_path


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(text.replace(" ", "-"))


class Window(MSFluentWindow):

    def __init__(self, app):
        super().__init__()
        # self.icon = QIcon(":/qfluentwidgets/images/logo.png")
        self.icon = QIcon(f"{local_path}/resource/static/logo.jpeg")

        self.splashScreen = SplashScreen(self.icon, self)
        self.splashScreen.setIconSize(QSize(102, 102))

        self.initWindow()
        self.show()
        self.createSubInterface()
        self.splashScreen.finish()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)
        # self.settingInterface = Widget("待开发中", self)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayMenu = QMenu(self)
        self.showAction = QAction("打开主页", self)
        self.quitAction = QAction("退出", self)

        self.initNavigation()
        self.initTrayMenu(app)

    def initNavigation(self):

        self.addSubInterface(
            self.homeInterface,
            FIF.HOME,
            "主页",
            FIF.HOME_FILL,
        )
        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置")

        self.navigationInterface.addItem(
            routeKey="Github",
            icon=FIF.GITHUB,
            text="Github",
            onClick=self.onLink,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.homeInterface.objectName())

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(self.icon)
        self.setWindowTitle("签到小助手")

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def initTrayMenu(self, app):

        self.trayIcon.setIcon(self.icon)
        self.showAction.triggered.connect(self.showWindow)
        self.quitAction.triggered.connect(lambda: self.handleClose(app))
        self.trayMenu.addAction(self.showAction)
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(self.quitAction)
        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.activated.connect(self.handleTrayClick)
        self.trayIcon.show()

    def onLink(self):
        QDesktopServices.openUrl(QUrl("https://github.com/fenglekai/sign-in-assistant"))

    def closeEvent(self, event):
        # 重写窗口关闭事件，实现最小化到托盘
        event.ignore()
        self.hide()

    def showWindow(self):
        if self.isHidden():
            self.showNormal()
            self.raise_()

    def handleTrayClick(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showWindow()

    def handleClose(self, app):
        remove_file()
        app.quit()

    def createSubInterface(self):
        loop = QEventLoop(self)
        
        QTimer.singleShot(1000, loop.quit)
        loop.exec()


class SingletonApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.instance = None

    def createInstance(self):
        self.instance = Window(self)
        set_window(self.instance)
        


def setupWindow():
    # create application
    check_window()
    app = SingletonApp(sys.argv)

    app.createInstance()

    def handleGlobalException(excType, excValue, excTraceback):
        if excType == psutil.ZombieProcess or excType == psutil.NoSuchProcess or psutil.AccessDenied:
            return
        w = Dialog(
            "错误",
            f"应用运行出错:\nErrorType: {excType}\n{excValue}",
            app.instance,
        )
        w.yesButton.setText("确认")
        w.cancelButton.hide()
        if w.exec():
            remove_file()
            sys.exit(1)

    sys.excepthook = handleGlobalException
    sys.exit(app.exec())


if __name__ == "__main__":
    setupWindow()
