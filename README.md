# 打卡小助手V 0.1

## 快速运行项目

### python

```
pipenv install
pipenv shell
python fetchSignIn.py
```

### mariadb

```
# 创建数据库user
# sql文件在koa-node目录下
# 预设端口8001
```

### node

```
npm install
npm run start
# 预设端口8002
```

### web

```
npm install
npm run serve
# 预设端口8003
```

## 简介

为了解决富士康卡机无法知道上班或下班有没有即时打卡的信息的痛点，包括`相信`、`富圈圈`都无法查询到当日打卡纪录。

目前已知能查询到当日打卡纪录的`HRM`也要7-15分钟才能刷新，但这已经是最快知道打卡信息的位置了。

通过python模拟登录查询签到状态，发生数据到外部后台，再由后台存储在数据库中，最后由前端页面呈现。

## 技术栈

- python 3.8
  - selenium(模拟chrome窗口遍历元素操控)
  - PIL-Image 截图
  - ddddocr 快速识别验证码
  - pipenv 管理虚拟环境
- node
  - koa2 node脚手架
  - mariadb 连接数据库
- vue3
  - vue-cli vue脚手架
  - naive-ui 组件设计风格库
  - axios 发送http请求

## Python部分

1. 你可能需要先在`/usr/bin`添加`chromedriver`；`https://chromedriver.chromium.org/`网址是下载对应你chrome浏览器版本的`chromedriver`；
2. 你可能还需要一个隐私配置，在pythonScript目录下建立`privateConfig.json`

```
{
  "HRM_URL": "", # hrm网址
  "BASE_URL": "http://localhost:8888/signIn", # 后台接口网址
  "GLOBAL_USERNAME": "", # 用户名
  "GLOBAL_PASSWORD": "", # 密码
  "HTTP_PROXY": "", # 你的http代理
  "PROXY": "" # 你的代理(无http://)
}
```



### 模拟请求数据

```
[{'uId': '9527', 'name': '无情打卡机器', 'time': '2022/08/12 08:06:22', 'machine': 'D1N1-02', 'isEffective': 'Y'}, {'uId': '9527', 'name': '无情打卡机器', 'time': '2022/08/12 17:32:50', 'machine': 'D1N1-02', 'isEffective': 'Y'}]
```

## Node部分

你可能还需要一个数据库配置，在koa-node/public/javascripts目录下建立`config.js`

```
const config = {
  // 数据库配置
  database: {
    DATABASE: "user",
    USERNAME: "root",
    PASSWORD: "",
    PORT: "8008",
    HOST: "localhost",
  },
};

module.exports = config;
```

## Web部分

你可能还需要一个接口配置，在sign-in-web/src/components目录下建立`httpUrl.js`

```
const httpUrl = "";
export default httpUrl;
```

