# 打卡小助手V 1.0

## 简介

记录你的打卡信息，工作再忙不要忘记打卡噢~

通过python模拟登录查询签到状态，发生数据到外部后台，再由后台存储在数据库中，最后由前端页面呈现。

**预览地址：**https://foxconn.devkai.site/

## 技术栈

- python 3.8
  - selenium(模拟chrome窗口遍历元素操控)
  - PIL-Image 截图
  - ddddocr 快速识别验证码
  - pipenv 管理虚拟环境
- node
  - koa2 服务端
  - mariadb 连接数据库
- vue3
  - vue-cli vue脚手架
  - naive-ui 组件设计风格库
  - axios 发送http请求
  - 虚拟列表组件加载大数据列表
  - 日历组件直观便捷查看打卡记录
  - websocket通讯手动更新查询数据

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



## Python部分

1. 你可能需要先在`pythonScript/static`添加`chromedriver`和`chromium`；`https://vikyd.github.io/download-chromium-history-version/#/`网址是下载对应你chrome浏览器版本的`chromedriver`和`chromium`；
2. 你可能还需要一个隐私配置，在pythonScript目录下建立`privateConfig.json`

```
{
  "HRM_URL": "https://hrm.myfiinet.com", # hrm网址
  "BASE_URL": "https://frontend-flk.site/bt-sign-in/signIn", # 后台接口网址
  "HTTP_PROXY": "http://F1338718:nEXK593K@10.191.131.156:3128", # 你的http代理
  "PROXY": "F1338718:nEXK593K@10.191.131.156:3128", # 你的代理(无http://)
  "USER_LIST": [
    {
      "username": "F1338718", # 用户名
      "password": "Flkai19980415.." # 密码
    }
  ]
}
```



### 模拟请求数据

```
[{'uId': '9527', 'name': '无情打卡机器', 'time': '2022/08/12 08:06:22', 'machine': 'machine'}, {'uId': '9527', 'name': '无情打卡机器', 'time': '2022/08/12 17:32:50', 'machine': 'machine'}]
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

