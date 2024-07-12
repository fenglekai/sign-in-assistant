import os
import sys
import time
from enum import Enum
import threading
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QTextEdit, QFrame, QVBoxLayout
from qfluentwidgets import (
    PrimaryToolButton,
    SmoothScrollArea,
    StyleSheetBase,
    Theme,
    FluentIcon,
)
import fetch_sign_in
from ws_client import connection


class ConsoleRedirect(QObject):
    outputSignal = pyqtSignal(str)

    def write(self, message):
        self.outputSignal.emit(message)

    def flush(self):
        pass


class StyleSheet(StyleSheetBase, Enum):
    """Style sheet"""

    LINK_CARD = "link_card"
    SAMPLE_CARD = "sample_card"
    HOME_INTERFACE = "home_interface"
    ICON_INTERFACE = "icon_interface"
    VIEW_INTERFACE = "view_interface"
    SETTING_INTERFACE = "setting_interface"
    GALLERY_INTERFACE = "gallery_interface"
    NAVIGATION_VIEW_INTERFACE = "navigation_view_interface"

    def path(self, theme=Theme.AUTO):
        current_path = os.path.abspath(__file__)
        local_path = os.path.dirname(current_path)
        return f"{local_path}/resource/qss/{self.value}.qss"


class HomeInterface(QWidget):
    """Home interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QFrame(self)
        self.scrollArea = SmoothScrollArea(self.view)
        self.scrollFlag = False
        self.scrollWidget = QWidget(self.scrollArea)
        self.textEdit = QTextEdit()

        self.consoleRedirect = ConsoleRedirect()
        self.consoleRedirect.outputSignal.connect(self.handleConsole)
        sys.stdout = self.consoleRedirect

        self.vBoxLayout = QVBoxLayout(self)
        self.textLayout = QVBoxLayout(self.scrollWidget)

        self.sendBtn = PrimaryToolButton(FluentIcon.SEND)

        self.__initLayout()
        self.__initWidget()

        self.setObjectName("basicInputInterface")
        self.scrollArea.setObjectName("scrollArea")
        self.scrollWidget.setObjectName("scrollWidget")
        StyleSheet.HOME_INTERFACE.apply(self)

        self.wsConnection()

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

        self.sendBtn.clicked.connect(self.handleSendBtn)

        self.setTextEdit()
        self.vBoxLayout.addWidget(self.sendBtn)
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

    def wsConnection(self):
        try:
            connectionThread = threading.Thread(
                target=connection, daemon=True, args=(self.consoleRedirect,)
            )
            connectionThread.start()
            print("websocket 连接开始")
        except Exception as e:
            print("连接失败: ", e)
            time.sleep(5)

    def handleConsole(self, message):
        self.textEdit.append(message)

    def handleSendBtn(self):
        thread = threading.Thread(target=fetch_sign_in.today_sign_in_list, daemon=True)
        thread.start()
