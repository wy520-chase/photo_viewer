自制网页图片浏览器，用于浏览nas上的图片 基于python flask实现，使用docker部署

## 预览图
![image](https://github.com/user-attachments/assets/690db250-8066-4b62-8672-f74fb98ab751)
![image](https://github.com/user-attachments/assets/a948f7fc-359f-4be3-9783-8728adc7eca8)

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
