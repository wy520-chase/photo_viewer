一个使用CSP策略防范XSS的示例

## 部署步骤：
### 1、核心修改
为所有内联脚本添加nonce
```
def generate_nonce():
    g.nonce = base64.b64encode(os.urandom(16)).decode('utf-8')
```
```
<script nonce="{{ nonce }}">
```
添加CSP响应头
```
csp = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{nonce}'; "
        "img-src 'self' blob:; "
    ).format(nonce=g.nonce)
```
### 2、效果验证
攻击脚本未成功运行
![image](https://github.com/user-attachments/assets/bc5a0514-9042-495d-9eaf-b5e99f43968c)

### 3、遗留问题
允许blob带来额外风险
