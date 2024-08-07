from enum import Enum
import os
from qfluentwidgets import (
    StyleSheetBase,
    Theme,
)
from use_path import local_path

class StyleSheet(StyleSheetBase, Enum):
    """Style sheet"""

    HOME_INTERFACE = "home_interface"
    SETTING_INTERFACE = "setting_interface"


    def path(self, theme=Theme.AUTO):
        return f"{local_path}/resource/qss/{self.value}.qss"