# Reading请求伪造工具

## 功能特点
- ✅ 自动获取课程列表
- ✅ 自动获取课程资源列表
- ✅ 自动生成签名（MD5）
- ✅ 自动处理认证信息
- ✅ 实时显示请求统计
- ✅ 支持多课程选择
- ✅ 支持多资源选择
- ✅ 可调请求间隔

## 使用方法

### 步骤1：导出认证信息
1. 浏览器打开 https://eqx.shzhzj.cn/zhjxpt/#/ 并登录
2. 按 F12 → Console（控制台）
3. 复制 `export_auth.js` 中的代码运行
4. 自动复制JSON到剪贴板

### 步骤2：运行Python程序
1. 双击 `run_spammer.bat`
2. 粘贴JSON字典 → 按两次Enter
3. 选择课程编号
4. 选择资源编号（或输入'a'全部刷）
5. 设置请求间隔（默认1秒）
6. 自动持续发送reading请求

### 停止
按 `Ctrl+C`

## 文件说明
- `export_auth.js`: 浏览器控制台JS代码（可直接复制使用）
- `reading_spammer.py`: Python主程序
- `run_spammer.bat`: 双击运行批处理
- `使用说明.bat`: 使用说明

## 签名算法
```
1. 取请求参数（排除sign/timestamp/nonce）按键排序
2. 拼接：key1=value1&key2=value2&...&timestamp=<timestamp>&nonce=<nonce>&key=nheam-sign-key-2024
3. 计算MD5，转小写
```

## 请求参数说明
- `rg_bh`: 资源ID（UUID格式）
- `rg_yhid`: 用户ID
- `rg_kcid`: 课程ID
- `rg_jxhdid`: 教学活动ID
- `rg_zylx`: 资源类型（如mp4）
- `rg_pjbzbh`: 评估标准编号（可为空）
- `rg_sfkw`: 是否可为空（可为空）

## 安全头说明
- `x-sign`: 签名
- `x-timestamp`: 13位时间戳
- `x-nonce`: 8位随机字符串
- `x-token`: 用户认证token
- `s-token`: 系统token
- `stamp`: 时间戳
- `system`: 系统标识（如s1）

## 注意事项
1. 需要Python和requests库（`pip install requests`）
2. 程序会持续发送请求直到手动停止
3. 请合理使用，避免对服务器造成过大压力
4. 如果遇到问题，请检查认证信息是否过期

## 常见问题

### Q: 为什么获取课程列表失败？
A: 可能是认证信息过期，请重新登录并导出认证信息。

### Q: 程序支持哪些课程？
A: 程序支持所有课程，只要认证信息有效即可。

## 技术支持
如遇到问题，请检查：
1. 认证信息是否有效
2. 网络连接是否正常
3. Python和requests库是否正确安装