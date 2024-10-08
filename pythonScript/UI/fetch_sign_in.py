# -*- coding: UTF-8 -*-
import json
import platform
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests
import time
import os
import ddddocr
import psutil
import ws_client
import private_config
from proxy import get_chrome_proxy_extension

ws = None
browser = None


def get_config():
    global HRM_URL
    global BASE_URL
    global proxies
    global USER_LIST
    global config
    config = private_config.read_config()
    HRM_URL = config["HRM_URL"]
    BASE_URL = config["BASE_URL"]
    proxies = {"http": config["HTTP_PROXY"], "https": config["HTTP_PROXY"]}
    USER_LIST = config["USER_LIST"]


error_count = int(0)


def add_error_count():
    global error_count
    error_count += 1


def get_error_count():
    global error_count
    if error_count > 5:
        ws_client.send_msg("异常次数过多停止任务")
        raise Exception("异常次数过多停止任务")


def clear_error_count():
    global error_count
    error_count = 0


# 时间处理
def time_format(format="%Y-%m-%d %H:%M:%S"):
    # 当前时间
    now_localtime = time.strftime(format, time.localtime())
    return now_localtime


# 创建测试浏览器
def create_browser(headless=True):
    get_error_count()
    global browser

    # 判断win添加应用后缀
    suffix = ""
    if platform.system().lower() == "windows":
        suffix = ".exe"

    chrome_path = os.path.join(f"{config['CHROME']}", f"chrome{suffix}")
    chromedriver_path = os.path.join(
        f"{config['CHROME_DRIVER']}", f"chromedriver{suffix}"
    )
    if (
        os.path.exists(chrome_path) == False
        or os.path.exists(chromedriver_path) == False
    ):
        ws_client.send_msg("chrome与chromedriver不存在")
        raise Exception("chrome与chromedriver不存在")

    options = webdriver.ChromeOptions()
    options.binary_location = chrome_path
    # 防止检测
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("detach", True)
    # 显示UI
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    options.add_argument("--verbose")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,960")
    # options.add_argument("--remote-debugging-port=30725")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")

    # 添加一个自定义的代理插件（配置特定的代理，含用户名密码认证）
    # proxy_pass = config["HTTP_PROXY"].split("http://")[1]
    # options.add_extension(get_chrome_proxy_extension(proxy=proxy_pass))

    try:
        # service = webdriver.ChromeService(executable_path=chromedriver_path, port=30726)
        service = webdriver.ChromeService(executable_path=chromedriver_path)
        browser = webdriver.Chrome(options=options, service=service)
        ws_client.send_msg(f"即将进入：{HRM_URL}")
        browser.get(HRM_URL)
        clear_error_count()
    except Exception as e:
        add_error_count()
        ws_client.send_msg("打开网页异常 %s" % e, ws)
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
    ws_client.send_msg("验证码为:", ocr_res, ws)
    browser.find_element("name", "CaptchaControl1").send_keys(ocr_res)


# 检查是否登录
def check_login():
    try:
        browser.implicitly_wait(10)
        title = browser.find_element(By.XPATH, "/html/head/title").get_attribute(
            "textContent"
        )
        ws_client.send_msg("进入到: %s" % title, ws)
        if title == "Fii 认证中心":
            login_frame()
            clear_error_count()
        if title != "個人中心 - 人力資源管理系統":
            get_error_count()
            add_error_count()
            time.sleep(1)
            return check_login()
        return True
    except Exception as e:
        ws_client.send_msg(f"未找到对应标识，检查登录失败{e}", ws)
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
        add_error_count()
        ws_client.send_msg("登录流程异常: %s" % e, ws)

    try:
        warning_msg = browser.find_element(
            By.XPATH, "//div[@class='el-message el-message--warning']/p"
        )
        if warning_msg:
            raise Exception(warning_msg.text)
    except NoSuchElementException as e:
        return


# 等待接口数据加载
def wait_loading():
    ws_client.send_msg("等待数据加载", ws)
    loading = browser.find_element(By.CLASS_NAME, "el-loading-spinner")
    display = loading.is_displayed()
    if display == True:
        time.sleep(1)
        wait_loading()


# 从请求接口获取数据
def get_sign_in_data_for_request(start_date, end_date, current_page=1):
    try:
        browser.implicitly_wait(10)
        ws_client.send_msg(f",正在读取数据...", ws)
        ws_client.send_msg(
            f"当前页数{current_page}, 时间范围{start_date} - {end_date}", ws
        )

        # cookie获取
        cookies_list = browser.get_cookies()
        cookieString = ""
        for cookie in cookies_list[:-1]:
            cookieString = cookieString + cookie["name"] + "=" + cookie["value"] + "; "

        cookieString = (
            cookieString + cookies_list[-1]["name"] + "=" + cookies_list[-1]["value"]
        )
        headers = {"cookie": cookieString}

        # 用户信息
        user_info = browser.find_element(By.CLASS_NAME, "emp-info").find_elements(
            By.TAG_NAME, "div"
        )[0]
        username = user_info.find_element(By.TAG_NAME, "p").text
        user_id = (
            user_info.find_element(By.TAG_NAME, "div")
            .find_element(By.TAG_NAME, "span")
            .text
        )
        page_size = 50

        query = {
            "RC": str(int(time.time() * 1000)),
            "EmpNo": user_id,
            "EmpName": username,
            "CardInfoTimeSDate": start_date,
            "CardInfoTimeEDate": end_date,
            "CurrentPage": str(current_page),
            "PageSize": str(page_size),
        }
        ws_client.send_msg(query)

        url = "https://hrm.myfiinet.com/EmpCardInfo/Search"
        ret = requests.get(url, headers=headers, params=query, proxies=proxies)
        if ret.status_code == 200:
            json_data = json.loads(ret.text)
            ws_client.send_msg(str(json_data))
            return format_sign_in_data_for_request(
                json_data, start_date, end_date, current_page
            )
        else:
            ws_client.send_msg("获取数据异常: %s" % ret, ws)

        return []
    except Exception as e:
        ws_client.send_msg("获取数据失败: %s" % e, ws)
    return []


# 格式化打卡数据
def format_sign_in_data_for_request(json_data, start_date, end_date, current_page):
    try:
        sign_in_list = []
        total = json_data["total"]
        rows = json_data["rows"]
        for _, row in enumerate(rows):
            sign_in_data = {}
            sign_in_data["uId"] = row["EmpNo"]
            sign_in_data["name"] = row["EmpName"]
            sign_in_data["time"] = row["CardInfoTime"]
            sign_in_data["readCardTime"] = row["CardInfoTime"]
            sign_in_data["machine"] = row["DevName"]
            sign_in_data["isEffective"] = "Y"
            sign_in_list.append(sign_in_data)
        # 多页查询逻辑
        if total - (current_page - 1) * len(rows) > len(rows):
            next_data = get_sign_in_data_for_request(
                start_date, end_date, current_page=current_page + 1
            )
            sign_in_list = sign_in_list + next_data
    except Exception as e:
        ws_client.send_msg("格式化打卡数据失败: %s" % e, ws)
    return sign_in_list


# 模拟查询操作获取数据
def get_sign_in_data_for_window(start_date, end_date):
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

        # 查询范围选择
        ws_client.send_msg("查询", ws)
        ws_client.send_msg(f"时间范围{start_date} - {end_date}", ws)
        content_wrapper = browser.find_element(By.CLASS_NAME, "content-wrapper")
        start_input = content_wrapper.find_element(
            By.XPATH, "//input[@placeholder='開始日期']"
        )
        start_input.click()
        start_input.clear()
        start_input.send_keys(start_date)
        end_input = content_wrapper.find_element(
            By.XPATH, "//input[@placeholder='結束日期']"
        )
        end_input.click()
        end_input.clear()
        end_input.send_keys(end_date)
        queryBtn = content_wrapper.find_element(By.TAG_NAME, "button")
        queryBtn.click()
        time.sleep(1)
        wait_loading()

        return format_sign_in_data_for_window()
    except Exception as e:
        ws_client.send_msg("获取数据失败: %s" % e, ws)
    return []


# 格式化打卡数据
def format_sign_in_data_for_window():
    ws_client.send_msg("正在读取数据...", ws)
    sign_in_list = []

    try:
        wrapper = browser.find_elements(
            By.XPATH, "//div[@class='wz-wrapper wizzy box-card']"
        )
        table = wrapper[1].find_elements(By.TAG_NAME, "tbody")
        tr_list = table[1].find_elements(By.TAG_NAME, "tr")
        for _, row in enumerate(tr_list):
            td_list = row.find_elements(By.XPATH, "td/div")
            sign_in_data = {}
            sign_in_data["uId"] = td_list[1].text
            sign_in_data["name"] = td_list[2].text
            sign_in_data["time"] = td_list[4].text
            sign_in_data["readCardTime"] = td_list[4].text
            sign_in_data["machine"] = td_list[5].text
            sign_in_data["isEffective"] = "Y"
            sign_in_list.append(sign_in_data)
    except Exception as e:
        ws_client.send_msg("格式化打卡数据失败: %s" % e, ws)
    return sign_in_list


# 发送数据到后台
def insert_sign_in_data(data):
    url = BASE_URL
    headers = {"content-type": "application/json"}
    requestData = {"signInData": data}
    ret = requests.post(url, json=requestData, headers=headers, proxies=proxies)
    if ret.status_code == 200:
        text = json.loads(ret.text)
        ws_client.send_msg(str(text), ws)
    else:
        ws_client.send_msg("发送数据异常: %s" % ret, ws)


# 关闭浏览器
def destroy():
    if browser:
        browser.quit()


# 杀死残余进程
def kill_process_by_name(process_name):
    ws_client.send_msg(f"正在关闭{process_name}进程...")
    for process in psutil.process_iter():
        try:
            if len(process.cmdline()) > 0:
                if process_name in process.cmdline()[0]:
                    process.kill()
                    ws_client.send_msg(f"已终止: {process.pid}")
        except Exception as e:
            ws_client.send_msg(f"关闭{process.pid}失败: {e}")
            continue


def kill_process_by_port(port):
    ws_client.send_msg(f"正在关闭30725端口进程...")
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == "LISTEN":
            p = psutil.Process(conn.pid)
            p.kill()
            ws_client.send_msg(f"已终止: {p.pid}")


def detection_process():
    destroy()
    kill_process_by_name("resource/static/chrome/chrome")
    kill_process_by_name("chromedriver")

    # kill_process_by_port(30725)
    # kill_process_by_port(30726)
    ws_client.send_msg(f"检测进程结束")


# 主流程
def sign_in_main(start_date=None, end_date=None, handless=True):
    now_date = time_format("%Y/%m/%d")
    if not start_date:
        start_date = now_date
    if not end_date:
        end_date = now_date
    create_browser(handless)

    ws_client.send_msg("登录确认中...", ws)
    check = check_login()
    if check == False:
        return destroy()

    ws_client.send_msg("查询打卡记录...", ws)
    data = get_sign_in_data_for_request(start_date, end_date)
    ws_client.send_msg(str(data), ws)

    if len(data) == 0:
        destroy()
        return ws_client.send_msg("没有需要发送的打卡纪录", ws)

    ws_client.send_msg("发送数据到后台...", ws)
    insert_sign_in_data(data)

    destroy()


# 获取签到列表
def fetch_sign_in_list(user_list=[], client=None, range_date=[], headless=True):
    global GLOBAL_USERNAME
    global GLOBAL_PASSWORD
    global ws
    ws = client
    now_time = time_format("%Y-%m-%d %H:%M:%S")
    ws_client.send_msg("=========%s script start===============" % now_time, ws)
    # detection_process()
    get_config()
    if len(user_list) == 0:
        user_list = USER_LIST

    if len(range_date) < 2:
        now_date = time_format("%Y/%m/%d")
        range_date.clear()
        range_date.append(now_date)
        range_date.append(now_date)

    for user in user_list:
        GLOBAL_USERNAME = user["username"]
        GLOBAL_PASSWORD = user["password"]
        clear_error_count()
        sign_in_main(range_date[0], range_date[1], headless)
    ws_client.send_msg("=========script end===============", ws)


if __name__ == "__main__":
    fetch_sign_in_list(range_date=["2024/08/01", "2024/08/01"], headless=False)
    # detection_process()
