import typing
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidgetItem,
    QHeaderView,
)
from qfluentwidgets import (
    LineEdit,
    BodyLabel,
    CardWidget,
    TableWidget,
    SubtitleLabel,
    ScrollArea,
    PrimaryPushButton,
    StateToolTip,
    Flyout,
    InfoBarIcon,
)
from style import StyleSheet
from private_config import read_config, write_config


class FormItem(QWidget):
    """Form item"""

    def __init__(self, label, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.lineEdit = LineEdit(self)
        self.label = BodyLabel(label + ":", self)

        self.lineEdit.setClearButtonEnabled(True)
        self.hBoxLayout.addWidget(self.label)
        self.hBoxLayout.addWidget(self.lineEdit)
        self.setObjectName("formItem")


class CardWrapper(CardWidget):
    """Card wrapper"""

    def __init__(self, title=None, widgets=[], parent=None):
        super().__init__(parent=parent)
        self.setClickEnabled(False)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self.view)

        self.__initTitle(title)

        for _, widget in enumerate(widgets):
            self.hBoxLayout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignVCenter)
            self.hBoxLayout.setSpacing(24)

        self.vBoxLayout.setContentsMargins(24, 24, 24, 24)
        self.vBoxLayout.addWidget(self.view)

        self.setObjectName("cardWrapper")

    def __initTitle(self, title):
        if title != None:
            title = SubtitleLabel(title, self)
            self.vBoxLayout.addWidget(title)


class UserTable(CardWidget):
    """User table"""

    def __init__(self, header=[], list=[], parent=None):
        super().__init__(parent=parent)
        self.vBoxLayout = QHBoxLayout(self)
        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        self.table.setRowCount(len(list))
        self.table.setColumnCount(len(header))
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().hide()
        self.vBoxLayout.setContentsMargins(24, 24, 24, 24)

        # 添加表格数据
        self.setList(list)

        # 设置水平表头并隐藏垂直表头
        self.table.setHorizontalHeaderLabels(header)
        self.table.setFixedSize(self.width() + 48, 300)

        self.vBoxLayout.addWidget(self.table)
        self.setObjectName("userTable")

    def setList(self, list):
        self.table.clearContents()
        self.table.setRowCount(len(list))
        for i, list in enumerate(list):
            for j in range(len(list)):
                self.table.setItem(i, j, QTableWidgetItem(list[j]))


class SettingInterface(ScrollArea):
    """Setting interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        StyleSheet.HOME_INTERFACE.apply(self)

        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.userForm = FormItem("账号")
        self.passForm = FormItem("密码")
        self.addButton = PrimaryPushButton("添加")
        self.table = UserTable(header=["账号", "密码"], list=[])
        self.stateTooltip = None

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.userForm.lineEdit.text()
        self.addButton.clicked.connect(
            lambda: self.addListItem(
                self.userForm.lineEdit.text(), self.passForm.lineEdit.text()
            )
        )

        self.vBoxLayout.addWidget(CardWrapper(widgets=[FormItem("签到地址")]))
        self.vBoxLayout.addWidget(CardWrapper(widgets=[FormItem("上传接口")]))
        self.vBoxLayout.addWidget(CardWrapper(widgets=[FormItem("代理地址")]))
        self.vBoxLayout.addWidget(
            CardWrapper(
                title="新增账号",
                widgets=[self.userForm, self.passForm, self.addButton],
            )
        )
        self.vBoxLayout.addWidget(self.table)

        self.updateListItem()

        self.setObjectName("settingInterface")

    def updateListItem(self):
        config = read_config()
        userList = []
        for _, user in enumerate(config["USER_LIST"]):
            userList.append([user["username"], "*****"])
        self.table.setList(userList)

    def addListItem(self, username, password):
        config = read_config()
        if not username or not password:
            return self.showSimpleFlyout("请输入账号和密码")
        if (
            len([item for item in config["USER_LIST"] if item["username"] == username])
            > 0
        ):
            return self.showSimpleFlyout("该账号已存在")

        config["USER_LIST"].append({"username": username, "password": password})
        write_config(config)
        self.updateListItem()

    def removeListItem(self, username):
        config = read_config()
        config["USER_LIST"] = [
            item for item in config["USER_LIST"] if not item["username"] == username
        ]
        write_config(config)
    
    def showSimpleFlyout(self, message):
        Flyout.create(
            icon=InfoBarIcon.WARNING,
            title="提示",
            content=message,
            target=self.addButton,
            parent=self.window(),
        )
