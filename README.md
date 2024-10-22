# SQL注入漏洞示例

## 漏洞概述

- **漏洞名称**：SQL 注入
- **受影响组件**：用户名输入框

## 漏洞描述

测试代码仅供示范，在原始代码基础上去除了User类中的ORM框架，取消参数化查询和自动转义逻辑，执行最原始的SQL命令，且未对用户输入做校验。
攻击者可以通过输入特制的SQL语句尝试绕过登录验证或窃取数据库信息。
```
   query = text(f"SELECT * FROM user WHERE username = '{username}'")
   result = db.session.execute(query).fetchone()
```

## 漏洞证明

### 重现步骤

1. 调试运行代码
2. 打开测试网站登录页面。
3. 在用户名输入框中输入以下payload：
   ```
   ' OR '1'='1
   ```
4. 在密码输入框中输入任意值。
5. 点击登录按钮。

### 测试结果

- 输入上述payload后，在调试框中可以看到数据库数据，包括加密后的密码
  ![image](https://github.com/user-attachments/assets/653a07dc-6315-4230-8312-c017f64155d7)


## 漏洞影响

因后台逻辑中存在进一步校验，即使触发SQL注入也无法直接绕过认证系统，仅能在代码调试中看到数据库数据

## 修复建议

1. **输入验证**：对用户输入进行严格的验证和过滤，确保输入仅包含有效字符。
2. **使用预编译语句**：采用参数化查询或预编译语句来避免SQL注入。如
```
   query = text("SELECT * FROM user WHERE username = :username")
   result = db.session.execute(query, {'username': username}).fetchone()
```
3. **最小权限原则**：限制数据库账户的权限，使其只能执行必要操作。
4. **安全审计**：定期进行代码审计和安全测试，确保及时发现和修复安全漏洞。
