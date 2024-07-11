import io
import sys
import time
from enum import Enum
import threading
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QFrame, QVBoxLayout
from qfluentwidgets import PushButton, SmoothScrollArea, StyleSheetBase, Theme
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
        return f"UI/resource/qss/{self.value}.qss"


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

        self.hBoxLayout = QHBoxLayout(self)
        self.textLayout = QVBoxLayout(self.scrollWidget)

        self.__initLayout()
        self.__initWidget()

        self.setObjectName("basicInputInterface")
        self.scrollArea.setObjectName("scrollArea")
        self.scrollWidget.setObjectName("scrollWidget")
        StyleSheet.HOME_INTERFACE.apply(self)

        self.wsConnection()

    def __initLayout(self):
        self.hBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.textLayout.setAlignment(self.textEdit, Qt.AlignmentFlag.AlignTop)
        self.textLayout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMaximumSize)

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

        self.setTextEdit()
        self.hBoxLayout.addWidget(self.scrollArea)

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
            self.connectionThread = threading.Thread(target=connection, daemon=True, args=(self.consoleRedirect,))
            self.connectionThread.start()
            print("websocket 连接开始")
        except Exception as e:
            print("连接失败: ", e)
            time.sleep(5)

    def handleConsole(self, message):
        self.textEdit.append(message)
