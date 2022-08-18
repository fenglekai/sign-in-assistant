#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
from PIL import Image
from interval import Interval
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests
import zipfile
import time
import os
import re
import ddddocr

with open("./privateConfig.json") as json_file:
    config = json.load(json_file)
    HRM_URL = config['HRM_URL']
    BASE_URL = config['BASE_URL']
    GLOBAL_USERNAME = config['GLOBAL_USERNAME']
    GLOBAL_PASSWORD = config['GLOBAL_PASSWORD']
    proxies = {'http': config['HTTP_PROXY'],
               'https': config['HTTP_PROXY']}
    IS_MORNING = False


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
def get_sign_in_list(browser):
    rowsData = browser.find_elements(By.CSS_SELECTOR, '#DG_Result>tbody>tr')
    signInList = []
    if len(rowsData) >= 2:
        for index, row in enumerate(rowsData):
            colsData = row.find_elements(By.CSS_SELECTOR, 'td')
            signInData = {}
            if len(colsData) >= 9 and index != 0:
                try:
                    signInData["uId"] = colsData[1].text
                    signInData['name'] = colsData[3].text
                    signInData['time'] = colsData[4].text
                    signInData['machine'] = colsData[5].text
                    signInData['isEffective'] = colsData[9].text
                except NoSuchElementException as e:
                    continue
                else:
                    signInList.append(signInData)
    return signInList


# 获取数据
def get_sign_in_data(username, password, isMorning):
    global browser
    options = webdriver.ChromeOptions()
    # 添加一个自定义的代理插件（配置特定的代理，含用户名密码认证）
    options.add_extension(get_chrome_proxy_extension(
        proxy=config['PROXY']))
    browser = webdriver.Chrome(options=options)
    browser.get(HRM_URL)
    # 登录操作
    browser.find_element('name', 'txtUserName').send_keys(username)
    browser.find_element('name', 'txtPassWord').send_keys(password)
    # 识别验证码
    browser.save_screenshot('./images/printScreen.png')
    vCode = browser.find_element(By.CSS_SELECTOR, '#Table2>tbody>tr>td>div>span>img')
    location = vCode.location  # 获取验证码x,y轴坐标
    size = vCode.size  # 获取验证码的长宽
    img_range = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                 int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
    i = Image.open("./images/printScreen.png")  # 打开截图
    frame4 = i.crop(img_range)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
    frame4.save('./images/save.png')  # 保存我们接下来的验证码图片 进行打码
    ocr = ddddocr.DdddOcr()
    with open('./images/save.png', 'rb') as f:
        img_bytes = f.read()
    ocrRes = ocr.classification(img_bytes)
    print('验证码为:', ocrRes)
    browser.find_element('name', 'CaptchaControl1').send_keys(ocrRes)
    try:
        browser.find_element('id', 'Btn_Login').click()
    except IOError:
        browser.close()
        get_sign_in_data(GLOBAL_USERNAME, GLOBAL_PASSWORD, IS_MORNING)
    time.sleep(1)
    # 查询考勤纪录
    # 进入侧边栏frame
    asideFrame = browser.find_element(By.CSS_SELECTOR, 'frameset>frameset').find_element('name', 'contents')
    browser.switch_to.frame(asideFrame)
    browser.find_element('id', 'TreOrgant15').click()
    time.sleep(0.5)
    browser.find_element('id', 'TreOrgant16').click()
    time.sleep(1)
    browser.switch_to.default_content()
    # 进入主内容frame
    mainFrame = browser.find_element(By.CSS_SELECTOR, 'frameset>frameset').find_element('name', 'main')
    browser.switch_to.frame(mainFrame)
    browser.find_element('id', 'btnSearch').click()
    time.sleep(1)

    signInList = get_sign_in_list(browser)
    if isMorning:
        maxClick = 15
        listLen = 1
    else:
        maxClick = 60
        listLen = 2
    if len(signInList) < listLen:
        print("无打卡数据，即将刷新列表")
        temp = []
        clickNum = 0
        while len(temp) < listLen and clickNum < maxClick:
            time.sleep(60)
            print("刷新第%s次,还会刷新%s次" % (clickNum+1,maxClick-clickNum-1))
            reload_btn = browser.find_elements(By.CSS_SELECTOR, '#TBar>tbody>tr>td>table>tbody>tr>td')
            reload_btn[7].click()
            temp = get_sign_in_list(browser)
            clickNum += 1
        signInList = temp
    print(signInList)
    browser.close()
    if len(signInList):
        insert_sign_in_data(signInList)
    else:
        print("无打卡数据")
    return signInList


if __name__ == "__main__":
    # IS_MORNING = True
    # get_sign_in_data(GLOBAL_USERNAME, GLOBAL_PASSWORD, IS_MORNING)
    while True:
        # 当前时间
        now_localtime = time.strftime("%H:%M:%S", time.localtime())
        # 当前时间（以时间区间的方式表示）
        now_time = Interval(now_localtime, now_localtime)
        morning_time_interval = Interval("8:00:00", "8:15:00")
        afternoon_time_interval = Interval("17:30:00", "18:30:00")
        print(now_time)
        if now_time in morning_time_interval:
            IS_MORNING = True
            get_sign_in_data(GLOBAL_USERNAME, GLOBAL_PASSWORD, IS_MORNING)
        if now_time in afternoon_time_interval:
            IS_MORNING = False
            get_sign_in_data(GLOBAL_USERNAME, GLOBAL_PASSWORD, IS_MORNING)
        time.sleep(60)
