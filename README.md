# 工程说明

### 开发语言说明

#### 前端

开发语言：HTML、CSS、JavaSript

部署平台：Netlify

#### 后端

开发语言：python 3.10
使用框架：flask架构、flask-restful代码风格
部署平台：github

### 开发环境说明

**基于github跨平台协作开发**

#### 前端

操作系统：Windows 11 22H2
开发环境：Visual Studio Code 1.78.2

#### 后端

操作系统：Windows 11 22H2
开发环境：PyCharm 2022.1.3 Pro

#### 第三方库版本

Flask 2.2.3

Flask-JWT-Extended 4.4.4

Flask-RESTful 0.3.9

Flask-SQLAlchemy 3.0.3

Flask-Cors 3.0.10

passlib 1.7.4

### 数据库软件说明

数据库版本：MySQL 8.0.28

数据库图形化工具：DataGrip 2021.3.4

### 软件安装部署说明

#### 准备工作

1. 下载程序压缩包解压到本地文件夹
2. 将项目文件夹导入Pycharm中，配置项目解释器为python 3.10，并修改项目框架为flask
3. 确保mysql服务处于运行状态

#### 启动项目

1. 编辑项目配置，在其他选项中添加"--host=0.0.0.0"即可通过本机IP地址访问服务器程序
2. backend目录下的app.py文件为后端服务器的入口，运行该文件或在pycharm中直接启动项目即可

#### 访问页面

1. 方法一（推荐）：frontend目录下的user文件夹下的index.html为充电系统主界面，打开该html文件，右键选择在浏览器中打开即可访问登录页面
2. 方法二（暂不推荐）：由于前端已实现自动化部署，也可通过netlify网站分配的地址远程访问本地前端界面，本项目的前端地址为https://bupt-charging-10.netlify.app/ ，但由于项目还在实时更新中，此方法访问可能会遇到未知问题，建议采用方法一
