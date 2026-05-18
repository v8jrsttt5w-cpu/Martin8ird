# 获取抖音 Cookies（3选1，推荐方案A）

## 方案A: Cookie-Editor 扩展 ⭐推荐

1. Edge浏览器打开: `edge://extensions/`
2. 左上角搜索 "Cookie-Editor"
3. 安装（图标是个饼干🍪的那个，作者 cgagnier）
4. 打开 douyin.com 并登录
5. 点扩展图标 → 点 Export (导出按钮，图标是↓)
6. 复制全部内容 → 粘贴到 `工具/cookies.json`
7. 在终端运行转换:
   ```
   cd d:\马丁鸟内容系统\工具
   python -c "
   import json
   with open('cookies.json') as f:
       data = json.load(f)
   with open('cookies.txt', 'w') as f:
       f.write('# Netscape HTTP Cookie File\n')
       for c in data:
           domain = c.get('domain', '.douyin.com')
           flag = 'TRUE'
           path = c.get('path', '/')
           secure = 'TRUE' if c.get('secure') else 'FALSE'
           expiry = str(int(c.get('expirationDate', 0))) if c.get('expirationDate') else '0'
           name = c['name']
           value = c['value']
           f.write(f'{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n')
   print('cookies.txt 已生成')
   "
   ```

## 方案B: 手动从DevTools提取

1. 打开 douyin.com 并登录
2. F12 → Application → 左侧 Cookies → douyin.com
3. 需要复制这些关键 cookie:
   - `passport_csrf_token`
   - `sid_guard` 或 `s_v_web_id`
   - `ttwid`
4. 在终端运行:
   ```
   cd d:\马丁鸟内容系统\工具
   python -c "
   cookies = input('粘贴完整Cookie字符串(从Network→Headers→Cookie复制): ')
   with open('cookies.txt', 'w') as f:
       f.write('# Netscape HTTP Cookie File\n')
       for item in cookies.split('; '):
           if '=' in item:
               name, value = item.split('=', 1)
               f.write(f'.douyin.com\tTRUE\t/\tTRUE\t0\t{name}\t{value}\n')
   print('cookies.txt 已生成')
   "
   ```

## 方案C: EditThisCookie

1. Edge扩展商店搜索 "EditThisCookie"
2. 安装 → 打开douyin.com登录 → 点扩展 → Export
3. 跟方案A一样的转换步骤

---

> 完成后验证: `python douyin_tools.py dl https://v.douyin.com/随便一个视频/`
> 能下载就说明配好了。
