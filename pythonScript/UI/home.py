from datetime import datetime
import os
import sys
import threading
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QUrl, QDate
from PyQt6.QtWidgets import QWidget, QTextEdit, QFrame, QVBoxLayout
from qfluentwidgets import (
    SmoothScrollArea,
    FluentIcon,
    CommandBar,
    Action,
    MessageBoxBase,
    SubtitleLabel,
    LineEdit,
    ComboBox,
    CalendarPicker,
    BodyLabel,
)
import fetch_sign_in
from ws_client import connection, disconnection
from private_config import read_config
from style import StyleSheet


class ConsoleRedirect(QObject):
    outputSignal = pyqtSignal(str)

    def write(self, message):
        self.outputSignal.emit(message)

    def flush(self):
        pass


class CustomMessageBox(MessageBoxBase):
    """Custom message box"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel(self.tr("执行查询签到任务"), self)

        self.userLabel = BodyLabel(self.tr("选择用户"), self)
        self.comboBox = ComboBox()

        self.startLabel = BodyLabel(self.tr("选择开始日期"), self)
        self.endLabel = BodyLabel(self.tr("选择结束日期"), self)
        self.startCalendar = CalendarPicker()
        self.endCalendar = CalendarPicker()
        current_date = datetime.today()
        self.startCalendar.setDate(
            QDate(current_date.year, current_date.month, current_date.day)
        )
        self.endCalendar.setDate(
            QDate(current_date.year, current_date.month, current_date.day)
        )

        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.userLabel)
        self.viewLayout.addWidget(self.comboBox)
        self.viewLayout.addWidget(self.startLabel)
        self.viewLayout.addWidget(self.startCalendar)
        self.viewLayout.addWidget(self.endLabel)
        self.viewLayout.addWidget(self.endCalendar)

        # change the text of button
        self.yesButton.setText(self.tr("确认"))
        self.cancelButton.setText(self.tr("取消"))

        self.widget.setMinimumWidth(360)

        self.initUserList()

    def initUserList(self):
        config = read_config()
        userList = []
        for _, user in enumerate(config["USER_LIST"]):
            userList.append(user["username"])
        self.comboBox.addItems(userList)


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

        self.playAction = Action(
            FluentIcon.PLAY,
            "连接启动",
            checkable=True,
        )

        self.__initLayout()
        self.__initWidget()

        self.setObjectName("homeInterface")
        self.scrollArea.setObjectName("scrollArea")
        self.scrollWidget.setObjectName("scrollWidget")
        StyleSheet.HOME_INTERFACE.apply(self)

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
        self.playAction.toggled.connect(self.handleActionCheck)
        self.playAction.setChecked(True)
        self.commandBar.addActions(
            [
                self.playAction,
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
        w = CustomMessageBox(self.window())
        if w.exec():
            selected = w.comboBox.currentText()
            config = read_config()
            userList = []
            for _, user in enumerate(config["USER_LIST"]):
                if selected == user["username"]:
                    userList.append(user)
                    break
            start = w.startCalendar.text().replace("-", "/")
            end = w.endCalendar.text().replace("-", "/")
            thread = threading.Thread(
                target=fetch_sign_in.fetch_sign_in_list,
                daemon=True,
                args=(
                    userList,
                    None,
                    [start, end],
                ),
            )
            thread.start()
