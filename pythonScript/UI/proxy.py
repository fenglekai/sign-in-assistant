# coding: utf-8
# proxy.py
# Selenium Chrome设置带用户名密码的proxy代理
import os
import re
import zipfile
from use_path import static_path
# Chrome代理模板插件地址: https://github.com/revotu/selenium-chrome-auth-proxy
CHROME_PROXY_HELPER_DIR = os.path.join(static_path, "chrome-proxy-helper")
# 存储自定义Chrome代理扩展文件的目录
CUSTOM_CHROME_PROXY_EXTENSIONS_DIR = os.path.join(static_path, "chrome-proxy-extensions")
def get_chrome_proxy_extension(proxy):
    """获取一个Chrome代理扩展,里面配置有指定的代理(带用户名密码认证)
    proxy - 指定的代理,格式: username:password@ip:port
    """
    m = re.compile('([^:]+):([^\@]+)\@([\d\.]+):(\d+)').search(proxy)
    if m:
        # 提取代理的各项参数
        username = m.groups()[0]
        password = m.groups()[1]
        ip = m.groups()[2]
        port = m.groups()[3]
        # 创建一个定制Chrome代理扩展(zip文件)
        if not os.path.exists(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR):
            os.mkdir(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR)
        extension_file_path = os.path.join(CUSTOM_CHROME_PROXY_EXTENSIONS_DIR, '{}.zip'.format(proxy.replace(':', '_')))
        if not os.path.exists(extension_file_path):
            # 扩展文件不存在，创建
            zf = zipfile.ZipFile(extension_file_path, mode='w')
            zf.write(os.path.join(CHROME_PROXY_HELPER_DIR, 'manifest.json'), 'manifest.json')
            # 替换模板中的代理参数
            background_content = open(os.path.join(CHROME_PROXY_HELPER_DIR, 'background.js')).read()
            background_content = background_content.replace('%proxy_host', ip)
            background_content = background_content.replace('%proxy_port', port)
            background_content = background_content.replace('%username', username)
            background_content = background_content.replace('%password', password)
            zf.writestr('background.js', background_content)
            zf.close()
        return extension_file_path
    else:
        raise Exception('Invalid proxy format. Should be username:password@ip:port')