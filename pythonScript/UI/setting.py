import typing
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from qfluentwidgets import (
    LineEdit,
    BodyLabel,
    CardWidget,
    TableWidget,
    TitleLabel,
    SubtitleLabel,
    ScrollArea,
    PrimaryPushButton,
    Flyout,
    InfoBarIcon,
    RoundMenu,
    Action,
    FluentIcon,
    MenuAnimationType,
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
        self.hBoxLayout.setSpacing(24)
        self.hBoxLayout.addWidget(self.label)
        self.hBoxLayout.addWidget(self.lineEdit)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 12)
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
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.vBoxLayout.setContentsMargins(24, 24, 24, 24)

        # 添加表格数据
        self.setList(list)

        # 设置水平表头并隐藏垂直表头
        self.table.setHorizontalHeaderLabels(header)
        self.table.setMinimumHeight(300)

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
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.title = TitleLabel("设置", self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.formWidget = QWidget()
        self.formLayout = QVBoxLayout(self.formWidget)
        self.signInUrl = FormItem("签到地址")
        self.updateUrl = FormItem("上传接口")
        self.proxyUrl = FormItem("代理地址")
        self.saveButton = PrimaryPushButton("保存")
        self.userForm = FormItem("账号")
        self.passForm = FormItem("密码")
        self.addButton = PrimaryPushButton("添加")
        self.userTable = UserTable(header=["账号", "密码"], list=[])
        self.stateTooltip = None
        self.config = None

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.vBoxLayout.setContentsMargins(36, 20, 36, 36)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.saveButton.setFixedWidth(120)
        self.saveButton.clicked.connect(lambda: self.updateConfig())
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.userForm.lineEdit.text()
        self.addButton.clicked.connect(
            lambda: self.addListItem(
                self.userForm.lineEdit.text(), self.passForm.lineEdit.text()
            )
        )
        self.userTable.table.cellClicked.connect(self.handleCell)

        self.vBoxLayout.addWidget(self.title)
        self.formLayout.addWidget(self.signInUrl)
        self.formLayout.addWidget(self.updateUrl)
        self.formLayout.addWidget(self.proxyUrl)
        self.formLayout.addWidget(
            self.saveButton, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.vBoxLayout.addWidget(CardWrapper(widgets=[self.formWidget]))
        self.vBoxLayout.addWidget(
            CardWrapper(
                title="新增账号",
                widgets=[self.userForm, self.passForm, self.addButton],
            )
        )
        self.vBoxLayout.addWidget(self.userTable)

        self.__initConfig()
        self.updateListItem()

        self.view.setObjectName("view")
        self.setObjectName("settingInterface")

    def __initConfig(self):
        self.config = read_config()
        self.signInUrl.lineEdit.setText(self.config["HRM_URL"])
        self.updateUrl.lineEdit.setText(self.config["BASE_URL"])
        self.proxyUrl.lineEdit.setText(self.config["HTTP_PROXY"])

    def updateConfig(self):
        self.config["HRM_URL"] = self.signInUrl.lineEdit.text()
        self.config["BASE_URL"] = self.updateUrl.lineEdit.text()
        self.config["HTTP_PROXY"] = self.proxyUrl.lineEdit.text()
        defaultConfig = read_config()
        defaultConfig.update(self.config)
        write_config(defaultConfig)

    def updateListItem(self):
        config = read_config()
        self.config = config
        userList = []
        for _, user in enumerate(config["USER_LIST"]):
            userList.append([user["username"], "*****"])
        self.userTable.setList(userList)

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
        self.userForm.lineEdit.clear()
        self.passForm.lineEdit.clear()

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

    def handleCell(self, row, col):
        username = self.config["USER_LIST"][row]['username']
        menu = RoundMenu(parent=self)
        action = Action(
            FluentIcon.REMOVE_FROM, f"是否删除当前行: {username}"
        )
        def handleTriggered():
            self.removeListItem(username)
            self.updateListItem()
        action.triggered.connect(lambda: handleTriggered())
        

        menu.addAction(action)
        menu.exec(QCursor.pos(), aniType=MenuAnimationType.DROP_DOWN)
