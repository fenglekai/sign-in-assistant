import os
import sys
import threading
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QTextEdit, QFrame, QVBoxLayout
from qfluentwidgets import (
    SmoothScrollArea,
    FluentIcon,
    CommandBar,
    Action,
)
import fetch_sign_in
from ws_client import connection, disconnection
from style import StyleSheet


class ConsoleRedirect(QObject):
    outputSignal = pyqtSignal(str)

    def write(self, message):
        self.outputSignal.emit(message)

    def flush(self):
        pass


class HomeInterface(QWidget):
    """Home interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QFrame(self)
        self.scrollArea = SmoothScrollArea(self.view)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollFlag = False
        self.textEdit = QTextEdit()

        self.consoleRedirect = ConsoleRedirect()
        self.consoleRedirect.outputSignal.connect(self.handleConsole)
        sys.stdout = self.consoleRedirect

        self.vBoxLayout = QVBoxLayout(self)
        self.textLayout = QVBoxLayout(self.scrollWidget)

        self.commandBar = CommandBar(self)

        self.action = Action(
            FluentIcon.PLAY,
            "连接启动",
            checkable=True,
            toggled=lambda: self.handleActionCheck(),
        )
        self.action.setChecked(True)

        self.__initLayout()
        self.__initWidget()

        self.setObjectName("homeInterface")
        self.scrollArea.setObjectName("scrollArea")
        self.scrollWidget.setObjectName("scrollWidget")
        StyleSheet.HOME_INTERFACE.apply(self)

        # self.wsConnection()

    def __initLayout(self):
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.textLayout.setAlignment(self.textEdit, Qt.AlignmentFlag.AlignTop)
        self.textLayout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMaximumSize)

    def __initWidget(self):
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setViewportMargins(0, 5, 0, 5)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.verticalScrollBar().rangeChanged.connect(
            self.handleScrollChanged
        )

        self.commandBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.commandBar.addAction(
            Action(FluentIcon.SEND, "执行任务", triggered=lambda: self.handleSendBtn())
        )
        self.commandBar.addSeparator()
        self.commandBar.addActions(
            [
                self.action,
            ]
        )

        self.setTextEdit()
        self.vBoxLayout.addWidget(self.commandBar)
        self.vBoxLayout.addWidget(self.scrollArea)

    def handleScrollChanged(self, minValue, maxValue):
        if self.scrollFlag:
            self.scrollArea.verticalScrollBar().setValue(maxValue)
            self.scrollFlag = False

    def setTextEdit(self):
        self.textEdit.setReadOnly(True)
        self.textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.textEdit.textChanged.connect(self.handleTextChanged)

        self.textEdit.setObjectName("textEdit")
        self.textLayout.addWidget(self.textEdit)

    def handleTextChanged(self):
        height = int(self.textEdit.document().size().height() * 1)
        self.textEdit.setMinimumHeight(height)
        self.scrollFlag = True

    def handleActionCheck(self):
        if self.action.isChecked():
            self.wsConnection()
        else:
            self.wsDisconnection()

    def wsConnection(self):
        connection(self.consoleRedirect)
        print("websocket 连接开始")


    def wsDisconnection(self):
        disconnection()
        print("websocket 连接中止")

    def handleConsole(self, message):
        self.textEdit.append(message)

    def handleSendBtn(self):
        thread = threading.Thread(target=fetch_sign_in.today_sign_in_list, daemon=True)
        thread.start()
