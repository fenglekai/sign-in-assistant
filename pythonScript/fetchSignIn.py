# -*- coding: UTF-8 -*-
import json
import re
import zipfile
from PIL import Image
from interval import Interval
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests
import time
import datetime
import os
import ddddocr
import shutil
import psutil

local_path = os.getcwd()

with open("%s/static/privateConfig.json" % local_path) as json_file:
    config = json.load(json_file)
    HRM_URL = config["HRM_URL"]
    BASE_URL = config["BASE_URL"]
    proxies = {"http": config["HTTP_PROXY"], "https": config["HTTP_PROXY"]}
    IS_MORNING = True
    USER_LIST = config["USER_LIST"]


# Chrome代理模板插件地址: https://github.com/revotu/selenium-chrome-auth-proxy
CHROME_PROXY_HELPER_DIR = "chrome-proxy-helper"
# 存储自定义Chrome代理扩展文件的目录
CUSTOM_CHROME_PROXY_EXTENSIONS_DIR = "chrome-proxy-extensions"


# 设置selenium的chrome代理
def get_chrome_proxy_extension(proxy):
    """获取一个Chrome代理扩展,里面配置有指定的代理(带用户名密码认证)
    proxy - 指定的代理,格式: username:password@ip:port
    """
    m = re.compile("([^:]+):([^\@]+)\@([\d\.]+):(\d+)").search(proxy)
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
            CUSTOM_CHROME_PROXY_EXTENSIONS_DIR, "{}.zip".format(proxy.replace(":", "_"))
        )
        if not os.path.exists(extension_file_path):
            # 扩展文件不存在，创建
            zf = zipfile.ZipFile(extension_file_path, mode="w")
            zf.write(
                os.path.join(CHROME_PROXY_HELPER_DIR, "manifest.json"), "manifest.json"
            )
            # 替换模板中的代理参数
            background_content = open(
                os.path.join(CHROME_PROXY_HELPER_DIR, "background.js")
            ).read()
            background_content = background_content.replace("%proxy_host", ip)
            background_content = background_content.replace("%proxy_port", port)
            background_content = background_content.replace("%username", username)
            background_content = background_content.replace("%password", password)
            zf.writestr("background.js", background_content)
            zf.close()
        return extension_file_path
    else:
        raise Exception("Invalid proxy format. Should be username:password@ip:port")


# 创建测试浏览器
def create_browser():
    global browser
    options = Options()
    options.binary_location = "%s/static/chrome-linux/chrome" % local_path
    # 防止检测
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # 显示UI
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--verbose")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,960")
    options.add_argument("--remote-debugging-port=9333")
    options.add_argument("--profile-directory=profile")
    options.add_argument("--user-data-dir={}/static/profile".format(local_path))

    # 添加一个自定义的代理插件（配置特定的代理，含用户名密码认证），无法在无ui（--headless）情况下运行
    options.add_extension(get_chrome_proxy_extension(proxy=config["PROXY"]))

    service = Service(executable_path="%s/static/chromedriver" % local_path)
    browser = webdriver.Chrome(options=options, service=service)
    try:
        browser.get(HRM_URL)
    except Exception as e:
        print("打开网页异常 %s" % e)
        destroy()
        create_browser()


# 识别验证码
def use_orc():
    browser.save_screenshot("./images/printScreen.png")
    v_code = browser.find_element(By.CSS_SELECTOR, "#Table2>tbody>tr>td>div>span>img")
    location = v_code.location  # 获取验证码x,y轴坐标
    size = v_code.size  # 获取验证码的长宽
    img_range = (
        int(location["x"]),
        int(location["y"]),
        int(location["x"] + size["width"]),
        int(location["y"] + size["height"]),
    )  # 写成我们需要截取的位置坐标
    i = Image.open("./images/printScreen.png")  # 打开截图
    frame4 = i.crop(img_range)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
    frame4.save("./images/save.png")  # 保存我们接下来的验证码图片 进行打码
    ocr = ddddocr.DdddOcr()
    with open("./images/save.png", "rb") as f:
        img_bytes = f.read()
    ocr_res = ocr.classification(img_bytes)
    print("验证码为:", ocr_res)
    browser.find_element("name", "CaptchaControl1").send_keys(ocr_res)


# 时间处理
def time_format():
    # 当前时间
    now_localtime = time.strftime("%Y/%m/%d", time.localtime())
    return now_localtime


# 检查是否登录
def check_login():
    try:
        browser.implicitly_wait(10)
        title = browser.find_element(By.XPATH, "/html/head/title").get_attribute(
            "textContent"
        )
        print("进入到: %s" % title)
        if title == "Fii 认证中心":
            login_frame()
        if title != "個人中心 - 人力資源管理系統":
            time.sleep(1)
            return check_login()
        return True
    except Exception as e:
        print("未找到对应标识，检查登录失败")
        return False


# 登录操作
def login_frame():
    try:
        login_form = browser.find_element(By.CLASS_NAME, "demo-ruleForm")
        inputs = login_form.find_elements(By.TAG_NAME, "input")
        inputs[0].send_keys(GLOBAL_USERNAME)
        inputs[1].send_keys(GLOBAL_PASSWORD)
        login_btn = login_form.find_element(By.TAG_NAME, "button")
        login_btn.click()
    except NoSuchElementException as e:
        print("登录流程异常: %s" % e)
        sign_in_main()


# 等待接口数据加载
def wait_loading():
    print("等待数据加载")
    loading = browser.find_element(By.CLASS_NAME, "el-loading-spinner")
    display = loading.is_displayed()
    if display == True:
        time.sleep(1)
        wait_loading()


# 获取数据
def get_sign_in_data(isMorning):
    try:
        browser.implicitly_wait(10)
        # 菜单选择
        person_menu = browser.find_element(By.XPATH, "//a[@key='AttPersonal']")
        person_menu.click()
        time.sleep(1)
        emp_card = browser.find_element(By.XPATH, "//li[@key='EmpCardInfo']")
        emp_card.click()
        time.sleep(1)

        wait_loading()

        # 查询范围选择今日
        print("查询")
        content_wrapper = browser.find_element(By.CLASS_NAME, "content-wrapper")
        now_date = time_format()
        start_input = content_wrapper.find_element(
            By.XPATH, "//input[@placeholder='開始日期']"
        )
        start_input.click()
        start_input.clear()
        start_input.send_keys(now_date)
        end_input = content_wrapper.find_element(
            By.XPATH, "//input[@placeholder='結束日期']"
        )
        end_input.click()
        end_input.clear()
        end_input.send_keys(now_date)
        queryBtn = content_wrapper.find_element(By.TAG_NAME, "button")
        queryBtn.click()
        time.sleep(1)
        wait_loading()

        return format_sign_in_data()
    except Exception as e:
        print("获取数据失败: %s" % e)
    return []


# 格式化打卡数据
def format_sign_in_data():
    print("正在读取数据...")
    sign_in_list = []
    sign_in_data = {}
    try:
        wrapper = browser.find_elements(
            By.XPATH, "//div[@class='wz-wrapper wizzy box-card']"
        )
        table = wrapper[1].find_elements(By.TAG_NAME, "tbody")
        tr_list = table[1].find_elements(By.TAG_NAME, "tr")
        for _, row in enumerate(tr_list):
            td_list = row.find_elements(By.XPATH, "td/div")
            sign_in_data["uId"] = td_list[1].text
            sign_in_data["name"] = td_list[2].text
            sign_in_data["time"] = td_list[4].text
            sign_in_data["machine"] = td_list[5].text
            sign_in_list.append(sign_in_data)
    except Exception as e:
        print("格式化打卡数据失败: %s" % e)
    return sign_in_list


# 发送数据到后台
def insert_sign_in_data(data):
    url = BASE_URL
    headers = {"content-type": "application/json"}
    requestData = {"signInData": data}
    ret = requests.post(url, json=requestData, headers=headers, proxies=proxies)
    if ret.status_code == 200:
        text = json.loads(ret.text)
        print(text)
    else:
        print("发送数据异常: %s" % ret)



# 关闭浏览器
def destroy():
    browser.quit()
    shutil.rmtree("chrome-proxy-extensions")


# 杀死残余进程
def detection_process():
    process_name = "chromedriver"
    process_list = [
        process for process in psutil.process_iter() if process.name() == process_name
    ]
    if len(process_list) > 0:
        for process in process_list:
            process.kill()


# 主流程
def sign_in_main():
    create_browser()
    print("登录确认中...")
    check = check_login()
    if check == False:
        return destroy()

    print("查询今日打卡记录...")
    data = get_sign_in_data(IS_MORNING)
    print(data)

    print("发送数据到后台...")
    insert_sign_in_data(data)

    destroy()


# 今日签到数据
def today_sign_in_list(user_list=USER_LIST):
    global GLOBAL_USERNAME
    global GLOBAL_PASSWORD
    # 当前时间
    now_localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # 当前时间（以时间区间的方式表示）
    now_time = Interval(now_localtime, now_localtime)
    print("=========%s script start===============" % now_time)
    detection_process()

    for item in user_list:
        GLOBAL_USERNAME = item["username"]
        GLOBAL_PASSWORD = item["password"]
        sign_in_main()
    print("=========script end===============")


if __name__ == "__main__":
    today_sign_in_list()
