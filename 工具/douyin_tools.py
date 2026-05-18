"""
抖音内容分析工具集
作者: 马丁鸟AI助手
用途: 分析竞品视频结构、抓取公开信息、下载视频素材

══════════════════════════════════════════════
能力清单:
  1. 下载视频 → 提取关键帧 → 分析结构
  2. 搜索热榜/话题/BGM (WebSearch)
  3. 获取用户公开页面信息
══════════════════════════════════════════════

使用方式(在 Claude Code 中):
  用户: "分析这个视频 https://v.douyin.com/xxxx/"
  AI: 自动下载 → 提取帧 → 分析脚本结构

  用户: "俊杰哥哥最近发了什么"
  AI: 用 WebSearch 搜 "俊杰哥哥 抖音 最新"

前置准备(仅下载视频需要):
  1. 浏览器登录 douyin.com
  2. 导出 cookies → 工具/cookies.txt
"""

import sys
import io
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOL_DIR = Path(__file__).parent
DOWNLOAD_DIR = TOOL_DIR / "downloads"
FRAME_DIR = TOOL_DIR / "frames"
COOKIES_FILE = TOOL_DIR / "cookies.txt"


# ══════════════════════════════════════════
# 1. 视频下载 + 关键帧提取
# ══════════════════════════════════════════

def download_video(url):
    """下载抖音视频(需要cookies.txt)"""
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    cmd = [
        "yt-dlp",
        "-o", str(DOWNLOAD_DIR / "%(title).100s.%(ext)s"),
        "--no-playlist",
        "--merge-output-format", "mp4",
        url
    ]
    if COOKIES_FILE.exists():
        cmd.extend(["--cookies", str(COOKIES_FILE)])

    print(f"[下载] {url}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

    if result.returncode == 0:
        # 找到刚下载的文件
        mp4s = sorted(DOWNLOAD_DIR.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
        if mp4s:
            print(f"[完成] {mp4s[0].name}")
            return mp4s[0]
    else:
        err = result.stderr[-300:] if result.stderr else ""
        print(f"[失败] {err}")
    return None


def extract_frames(video_path, interval=3):
    """从视频提取关键帧(每N秒一帧)"""
    out_dir = FRAME_DIR / video_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", f"fps=1/{interval}",
        "-qscale:v", "2",
        str(out_dir / "f_%03d.jpg"),
        "-y"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

    frames = sorted(out_dir.glob("f_*.jpg"))
    if frames:
        print(f"[关键帧] {len(frames)} 张 → {out_dir}")
        return frames
    else:
        print("[警告] ffmpeg未安装，无法提取关键帧")
        print("  安装: winget install ffmpeg  或  https://ffmpeg.org/download.html")
        return []


def analyze_structure(frames_dir):
    """输出视频结构分析引导"""
    frames = sorted(Path(frames_dir).glob("f_*.jpg")) if isinstance(frames_dir, str) else sorted(Path(frames_dir).glob("f_*.jpg"))

    print(f"""
══════════════════════════════════════════
视频结构分析(共{len(frames)}帧, 需要AI视觉分析)

请回复:
  "分析结构" → AI会逐帧分析画面并拆解:
    - 0-3秒: 开头钩子类型
    - 3-8秒: 问题/痛点设置
    - 8-20秒: 核心内容节奏
    - 20秒+: 结尾引导方式

或者直接描述:
  - 开头用了什么钩子?
  - BGM是什么风格?
  - 口播节奏怎么样?
══════════════════════════════════════════
""")


# ══════════════════════════════════════════
# 2. 热榜/话题 (WebSearch辅助)
# ══════════════════════════════════════════

HOT_SEARCH_QUERIES = {
    "热榜": "抖音热榜 2026年5月",
    "摄影": "抖音 摄影 热门话题 2026",
    "穿搭": "抖音 小个子穿搭 热门 2026",
    "BGM": "抖音 热门BGM 卡点 2026年5月",
    "挑战": "抖音 最新挑战 话题 2026年5月",
}


def get_search_suggestions():
    """返回建议的搜索词 → 在Claude Code中触发WebSearch"""
    print("\n可用的搜索方向(在对话中说'搜[方向]'):\n")
    for key, query in HOT_SEARCH_QUERIES.items():
        print(f"  搜{key} → {query}")
    print()


# ══════════════════════════════════════════
# 3. 用户公开信息
# ══════════════════════════════════════════

def get_user_page(douyin_id):
    """获取用户主页信息(尝试多种方法)"""
    from playwright.sync_api import sync_playwright

    print(f"[用户] 获取 {douyin_id} 信息...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()

        info = {}
        try:
            # 方法1: 直接访问用户主页
            page.goto(f"https://www.douyin.com/user/{douyin_id}", timeout=30000)
            page.wait_for_timeout(5000)

            # 尝试获取页面标题(通常包含昵称)
            title = page.title()
            info["page_title"] = title

            # 获取页面文本内容
            text = page.evaluate("document.body.innerText")
            lines = [l.strip() for l in text.split('\n') if l.strip()][:30]
            info["page_text"] = lines

        except Exception as e:
            info["error"] = str(e)
        finally:
            browser.close()

    return info


# ══════════════════════════════════════════
# CLI
# ══════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n用法:")
        print("  python douyin_tools.py dl <视频链接>    下载视频")
        print("  python douyin_tools.py frames <视频路径> 提取关键帧")
        print("  python douyin_tools.py user <抖音号>     获取用户信息")
        print("  python douyin_tools.py search            显示搜索建议")
        sys.exit(0)

    action = sys.argv[1]

    if action == "dl":
        if len(sys.argv) < 3:
            print("请提供视频链接")
            sys.exit(1)
        video = download_video(sys.argv[2])
        if video:
            print(f"\n下载成功: {video}")
            print("下一步: python douyin_tools.py frames " + str(video))

    elif action == "frames":
        if len(sys.argv) < 3:
            print("请提供视频文件路径")
            sys.exit(1)
        extract_frames(sys.argv[2])

    elif action == "user":
        if len(sys.argv) < 3:
            print("请提供抖音号")
            sys.exit(1)
        info = get_user_page(sys.argv[2])
        print(json.dumps(info, ensure_ascii=False, indent=2))

    elif action == "search":
        get_search_suggestions()

    else:
        print(f"未知操作: {action}")
