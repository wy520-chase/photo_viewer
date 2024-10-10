自制网页图片浏览器，用于浏览nas上的图片 基于python flask实现，使用docker部署

## 部署步骤：
### 1、拉取项目

`git pull https://github.com/wy520-chase/photo_viewer.git`

### 2、创建容器

`docker build -t photo_viewer .`

### 3、按需修改docker-compose.yml中的密钥、密码和图片位置

### 4、启动容器

`docker-compose up -d`

### 5、访问

`http://your_host:8000`

## 问题处理
### 1、检查系统防火墙已放通端口
### 2、检查容器是否正常安装启动
