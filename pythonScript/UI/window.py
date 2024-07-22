# coding:utf-8
import sys

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices, QAction
from PyQt6.QtWidgets import QApplication, QFrame, QHBoxLayout, QMenu, QSystemTrayIcon
from qfluentwidgets import (
    NavigationItemPosition,
    MSFluentWindow,
    SubtitleLabel,
    setFont,
)
from qfluentwidgets import FluentIcon as FIF
from home import HomeInterface
from setting import SettingInterface


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

        # create sub interface
        self.homeInterface = HomeInterface(self)
        # self.settingInterface = Widget("待开发中", self)
        self.settingInterface = SettingInterface(self)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayMenu = QMenu(self)
        self.quitAction = QAction("退出", self)

        self.initNavigation()
        self.initWindow()
        self.initTrayMenu()

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
        self.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.setWindowTitle("签到小助手")

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def initTrayMenu(self):
        
        self.trayIcon.setIcon(QIcon(":/qfluentwidgets/images/logo.png"))
        self.quitAction.triggered.connect(app.quit)
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

    def handleTrayClick(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden():
                self.showNormal()
                self.raise_()


if __name__ == "__main__":
    # create application
    app = QApplication(sys.argv)

    # create main window
    w = Window(app)
    w.show()

    app.exec()
