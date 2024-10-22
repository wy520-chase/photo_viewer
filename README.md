自制网页图片浏览器，用于浏览nas上的图片 基于python flask实现，使用docker部署

## 预览图

<p align="center">
  <img src="https://github.com/user-attachments/assets/2794f6af-9e61-4fe3-9998-c936fd221e15" alt="目录查看页面" width="40%">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://github.com/user-attachments/assets/e603cb9f-ca05-4fcf-b524-dcb4011fcfad" alt="图片查看页面" width="40%">
</p>


## 部署步骤：
### 1、拉取项目

`git clone https://github.com/wy520-chase/photo_viewer.git`

### 2、创建容器

```
cd photo_viewer
docker build -t photo_viewer .
```

### 3、按需修改docker-compose.yml中的密钥、密码、图片位置和端口等信息

### 4、启动容器

`docker-compose up -d`

### 5、访问

`http://your_host:8000`

## 问题处理
### 1、检查系统防火墙已放通端口
### 2、检查容器是否正常安装启动
