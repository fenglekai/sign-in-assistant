# 打卡小助手

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
  - PyQt UI界面
  - websocket 发送数据
- node
  - koa2 服务端
  - mariadb 连接数据库
- vue3
  - vue-cli vue 脚手架
  - naive-ui 组件设计风格库
  - axios 发送http请求
  - 虚拟列表组件加载大数据列表
  - 日历组件直观便捷查看打卡记录
  - websocket 通讯手动更新查询数据

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
  "HRM_URL": "", # hrm网址
  "BASE_URL": "", # 后台接口网址
  "HTTP_PROXY": "", # 你的http代理
  "USER_LIST": [
    {
      "username": "", # 用户名
      "password": "" # 密码
    }
  ]
}
```



### 模拟请求数据

```
[{'uId': '9527', 'name': '无情打卡机器', 'time': '2022/08/12 08:06:22', 'machine': 'machine'}, {'uId': '9527', 'name': '无情打卡机器', 'time': '2022/08/12 17:32:50', 'machine': 'machine'}]
```

### 构建应用

```shell
pyinstaller -D -w ./UI/window.py -n sign-in-assistant --add-data "./UI/resource/:./resource/"
```

> WARNING: Library not found: could not resolve 'libglib-2.0.so.0', dependency of 'XXX'
>
> linux pyinstaller出现打包时问题，导致无法正常打开PyQt应用
>
> 是命令行的lib环境没有配置。在应用命令行环境如：.bashrc，配置LD_LIBRARY_PATH
>
> `export LD_LIBRARY_PATH=/path/to/your/libgcc_s.so.1:$LD_LIBRARY_PATH`



## Node部分

你可能还需要一个数据库配置，在koa-node/public/javascripts目录下建立`config.js`

```
const config = {
  // 数据库配置
  database: {
    DATABASE: "user",
    USERNAME: "root",
    PASSWORD: "",
    PORT: "3306",
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

