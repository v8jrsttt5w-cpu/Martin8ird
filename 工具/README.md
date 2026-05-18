# 工具集

> 抖音数据分析工具链。用 Python 脚本 + Claude Code AI 能力配合使用。

---

## 工具清单

| 脚本 | 用途 | 需要什么 |
|------|------|---------|
| `video_analyzer.py` | **新** 从视频提取关键帧 → AI分析结构 | opencv-python |
| `update_competitor_data.py` | 批量更新对标账号数据 | Playwright |

---

## 使用流程

### 场景1: 分析竞品视频

```
1. 用户: "分析这个视频 https://v.douyin.com/xxxx/"
2. AI 执行: python douyin_tools.py dl https://v.douyin.com/xxxx/
3. AI 执行: python douyin_tools.py frames downloads/xxx.mp4
4. AI 读取关键帧 → 分析结构 → 写入竞品拆解文件
```

**前置条件**: 首次下载视频需要 cookies.txt
- 在浏览器登录 douyin.com
- 用 Get cookies.txt 扩展导出 Netscape 格式
- 存到 `工具/cookies.txt`

### 场景2: 搜索热点

```
在对话中说 "搜索热点" → AI 触发 WebSearch
```

这个不需要 Python 脚本，直接走 WebSearch 工具。

### 场景3: 更新竞品数据

```
python update_competitor_data.py
```
会逐个访问对标账号主页，抓取粉丝数/昵称等公开信息。

---

## 环境依赖

```bash
pip install yt-dlp playwright
playwright install chromium
# 可选: 安装 ffmpeg (提取关键帧)
# winget install ffmpeg
```

---

## 当前能力边界

| 能做到 | 做不到(需要手动) |
|--------|----------------|
| 下载公开视频 | 下载私密/仅粉丝可见视频 |
| 提取关键帧供AI分析 | AI直接"看"视频(文本模型限制) |
| 抓取用户主页公开信息 | 获取精确互动数据(需登录) |
| WebSearch 搜索热点 | 实时监控热榜变化 |
| 分析视频结构(通过帧+描述) | 自动转录口播内容 |
