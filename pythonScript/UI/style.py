from enum import Enum
import os
from qfluentwidgets import (
    StyleSheetBase,
    Theme,
)

class StyleSheet(StyleSheetBase, Enum):
    """Style sheet"""

    HOME_INTERFACE = "home_interface"
    SETTING_INTERFACE = "setting_interface"


    def path(self, theme=Theme.AUTO):
        current_path = os.path.abspath(__file__)
        local_path = os.path.dirname(current_path)
        return f"{local_path}/resource/qss/{self.value}.qss"