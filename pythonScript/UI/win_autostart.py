import winreg
import os

def set_autostart(autostart=True):
    key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
    app_name = 'YourApp'
    app_path = os.path.abspath('sign-in-assistant.exe')

    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as reg:
        key = winreg.OpenKey(reg, key_path, 0, winreg.KEY_SET_VALUE)
        try:
            if autostart:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            else:
                winreg.DeleteValue(key, app_name)
        except FileNotFoundError:
            print("Executable not found:", app_path)
        finally:
            winreg.CloseKey(key)
