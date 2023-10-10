# -*- coding: UTF-8 -*-
import json
from PIL import Image
from interval import Interval
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import requests
import zipfile
import time
from datetime import datetime
import os
import re
import ddddocr
import shutil
import sys
import getpass
import psutil

# local_path = '/home/allen/Documents/flk-code/sign-in-assistant/pythonScript'
local_path = os.getcwd()

with open("%s/static/privateConfig.json" % local_path) as json_file:
    config = json.load(json_file)
    HRM_URL = config['HRM_URL']
    BASE_URL = config['BASE_URL']
    proxies = {'http': config['HTTP_PROXY'],
               'https': config['HTTP_PROXY']}
    IS_MORNING = True
    USER_LIST = config['USER_LIST']


# Chrome代理模板插件地址: https://github.com/revotu/selenium-chrome-auth-proxy
CHROME_PROXY_HELPER_DIR = 'chrome-proxy-helper'
# 存储自定义Chrome代理扩展文件的目录
CUSTOM_CHROME_PROXY_EXTENSIONS_DIR = 'chrome-proxy-extensions'


# 设置selenium的chrome代理
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
        extension_file_path = os.path.join(
            CUSTOM_CHROME_PROXY_EXTENSIONS_DIR, '{}.zip'.format(proxy.replace(':', '_')))
        if not os.path.exists(extension_file_path):
            # 扩展文件不存在，创建
            zf = zipfile.ZipFile(extension_file_path, mode='w')
            zf.write(os.path.join(CHROME_PROXY_HELPER_DIR,
                                  'manifest.json'), 'manifest.json')
            # 替换模板中的代理参数
            background_content = open(os.path.join(
                CHROME_PROXY_HELPER_DIR, 'background.js')).read()
            background_content = background_content.replace('%proxy_host', ip)
            background_content = background_content.replace(
                '%proxy_port', port)
            background_content = background_content.replace(
                '%username', username)
            background_content = background_content.replace(
                '%password', password)
            zf.writestr('background.js', background_content)
            zf.close()
        return extension_file_path
    else:
        raise Exception(
            'Invalid proxy format. Should be username:password@ip:port')


# 发生数据到后台
def insert_sign_in_data(data):
    url = BASE_URL
    headers = {'content-type': 'application/json'}
    requestData = {'signInData': data}
    ret = requests.post(url, json=requestData, headers=headers, proxies=proxies)
    if ret.status_code == 200:
        text = json.loads(ret.text)
        print(text)


# 存储打卡数据
def get_sign_in_list(bs_element):
    try:
        rows_data = bs_element.find_elements(By.CSS_SELECTOR, '#DG_Result>tbody>tr')
    except Exception as e:
        raise Exception(e)
    sign_in_list = []
    if len(rows_data) >= 2:
        for index, row in enumerate(rows_data):
            cols_data = row.find_elements(By.CSS_SELECTOR, 'td')
            sign_in_data = {}
            if len(cols_data) >= 9 and index != 0:
                try:
                    sign_in_data["uId"] = cols_data[1].text
                    sign_in_data['name'] = cols_data[3].text
                    sign_in_data['time'] = cols_data[4].text
                    sign_in_data['machine'] = cols_data[5].text
                    sign_in_data['readCardTime'] = cols_data[7].text
                    sign_in_data['isEffective'] = cols_data[9].text
                except NoSuchElementException as e:
                    continue
                else:
                    sign_in_list.append(sign_in_data)
    return sign_in_list

# 登录操作
def login_frame(browser, username, password):
    try:
        browser.find_element('name', 'txtUserName').send_keys(username)
        browser.find_element('name', 'txtPassWord').send_keys(password)
    except NoSuchElementException as e:
        print('浏览器打开页面失败')
        time.sleep(10)
        browser.quit()
        shutil.rmtree('chrome-proxy-extensions')
        get_sign_in_data(GLOBAL_USERNAME, GLOBAL_PASSWORD, IS_MORNING)
        return False
    # 识别验证码
    browser.save_screenshot('./images/printScreen.png')
    v_code = browser.find_element(By.CSS_SELECTOR, '#Table2>tbody>tr>td>div>span>img')
    location = v_code.location  # 获取验证码x,y轴坐标
    size = v_code.size  # 获取验证码的长宽
    img_range = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                 int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
    i = Image.open("./images/printScreen.png")  # 打开截图
    frame4 = i.crop(img_range)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
    frame4.save('./images/save.png')  # 保存我们接下来的验证码图片 进行打码
    ocr = ddddocr.DdddOcr()
    with open('./images/save.png', 'rb') as f:
        img_bytes = f.read()
    ocr_res = ocr.classification(img_bytes)
    print('验证码为:', ocr_res)
    browser.find_element('name', 'CaptchaControl1').send_keys(ocr_res)
    browser.find_element('id', 'Btn_Login').click()


# 获取数据
def get_sign_in_data(username, password, isMorning):
    global browser
    # options = webdriver.ChromeOptions()
    options = Options()
    # 防止检测
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.binary_location = '%s/static/chrome-linux/chrome' % local_path
    # 显示UI
    options.add_argument('headless')
    options.add_argument('no-sandbox')
    options.add_argument('disable-gpu')
    options.add_argument('start-maximized')
    options.add_argument('disable-notifications')
    options.add_argument('verbose')
    options.add_argument('disable-dev-shm-usage')
    # options.add_argument('--window-size=1500,1000')
    # options.add_argument('remote-debugging-port=9333')
    # options.add_argument("profile-directory=profile")
    # options.add_argument("--user-data-dir=./static/profile")

    # 添加一个自定义的代理插件（配置特定的代理，含用户名密码认证），无法在无ui（--headless）情况下运行
    # options.add_extension(get_chrome_proxy_extension(
    #     proxy=config['PROXY']))
    browser = webdriver.Chrome(executable_path='%s/static/chromedriver' % local_path, options=options)
    browser.get(HRM_URL)
    # 登录操作
    login_frame(browser, username, password)
    try:
        aside_frame = browser.find_element(By.CSS_SELECTOR, 'frameset>frameset').find_element('name', 'contents')
    except Exception as e:
        print(str(e))
        if '域帳號密碼錯誤' and '域 帳 號 被 鎖 定' in str(e):
            browser.quit()
            return print('登录时出现错误，请检查域帳號是否正确')
        if '驗證碼輸入不正確' in str(e):
            browser.quit()
            get_sign_in_data(GLOBAL_USERNAME, GLOBAL_PASSWORD, IS_MORNING)
        else:
            browser.quit()
            return

    time.sleep(1)
    # 查询考勤纪录
    # 进入侧边栏frame
    browser.switch_to.frame(aside_frame)
    browser.find_element('id', 'TreOrgant19').click()
    time.sleep(0.5)
    browser.find_element('id', 'TreOrgant20').click()
    time.sleep(1)
    browser.switch_to.default_content()
    # 进入主内容frame
    main_frame = browser.find_element(By.CSS_SELECTOR, 'frameset>frameset').find_element('name', 'main')
    browser.switch_to.frame(main_frame)
    try:
        browser.find_element('id', 'btnSearch').click()
    except Exception as e:
        print(e)
        browser.quit()
        get_sign_in_data(GLOBAL_USERNAME, GLOBAL_PASSWORD, IS_MORNING)
        return
    time.sleep(1)

    sign_in_list = get_sign_in_list(browser)
    
    if isMorning:
        max_click = 3
        list_len = 1
        print("现在是早上")
    else:
        max_click = 6
        list_len = 2
        print("现在是下午")
    if len(sign_in_list) < list_len:
        print("无打卡数据，即将刷新列表")
        temp = get_sign_in_list(browser)
        clickNum = 0
        while len(temp) < list_len and clickNum < max_click:
            time.sleep(10)
            print("刷新第%s次,还会刷新%s次" % (clickNum+1,max_click-clickNum-1))
            reload_btn = browser.find_elements(By.CSS_SELECTOR, '#TBar>tbody>tr>td>table>tbody>tr>td')
            reload_btn[7].click()
            temp = get_sign_in_list(browser)
            clickNum += 1
        sign_in_list = temp
    print(sign_in_list)
    browser.quit()
    if len(sign_in_list):
        insert_sign_in_data(sign_in_list)
    else:
        print("无打卡数据")
    return sign_in_list


def runserver(user_list):
    global GLOBAL_USERNAME
    global GLOBAL_PASSWORD
    for item in user_list:
        GLOBAL_USERNAME = item['username']
        GLOBAL_PASSWORD = item['password']
        get_sign_in_data(GLOBAL_USERNAME, GLOBAL_PASSWORD, IS_MORNING)

def detection_process():
    process_name = 'chromedriver'
    process_list = [process for process in psutil.process_iter() if process.name() == process_name]
    if len(process_list) > 0:
        for process in process_list:
            process.kill()

def main(user_list=USER_LIST):
    # 当前时间
    now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 当前时间（以时间区间的方式表示）
    now_time = Interval(now_localtime, now_localtime)
    print('=========%s script start===============' % now_time)
    detection_process()
    runserver(user_list)
    print('=========script end===============')


if __name__ == "__main__":
    main()


