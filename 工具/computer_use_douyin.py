"""
Computer Use — 操作电脑浏览器分析抖音博主
使用方法：python computer_use_douyin.py
前提：设置环境变量 ANTHROPIC_API_KEY=你的key
"""

import os
import sys
import json
import time
import base64
import traceback
from io import BytesIO
from datetime import datetime

import mss
import pyautogui
from PIL import Image
from anthropic import Anthropic

# ============ 配置 ============

TARGET_DOUYIN_ID = "4710050"  # hohooo 的抖音号
DOUYIN_URL = f"https://www.douyin.com/user/{TARGET_DOUYIN_ID}"

# 截图保存目录
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 屏幕缩放系数（Windows 高分屏通常需要，拿不准就保持1.0）
SCALE = 1.0

# ============ 工具函数 ============

def take_screenshot() -> str:
    """截全屏，返回 base64"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        png = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
        # 压缩到 1024px 宽，控制 token 消耗
        w, h = png.size
        if w > 1024:
            ratio = 1024 / w
            png = png.resize((1024, int(h * ratio)), Image.LANCZOS)
        buf = BytesIO()
        png.save(buf, format="JPEG", quality=75)
        return base64.b64encode(buf.getvalue()).decode()


def save_screenshot(b64: str, label: str):
    """保存截图到本地"""
    path = os.path.join(SCREENSHOT_DIR, f"{label}_{datetime.now().strftime('%H%M%S')}.jpg")
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"  📸 已保存: {path}")
    return path


def do_action(action: dict):
    """执行电脑操作"""
    a = action["type"]

    if a == "screenshot":
        return  # 截图在循环里统一处理

    elif a == "key":
        text = action["text"]
        pyautogui.write(text, interval=0.05)
        time.sleep(0.5)

    elif a == "keypress":
        keys = action["keys"]
        if isinstance(keys, str):
            keys = [keys]
        for k in keys:
            pyautogui.press(k)
        time.sleep(0.3)

    elif a == "mouse_move":
        x, y = action["x"], action["y"]
        x *= SCALE; y *= SCALE
        pyautogui.moveTo(x, y, duration=0.3)

    elif a == "left_click":
        if "x" in action and "y" in action:
            x, y = action["x"] * SCALE, action["y"] * SCALE
            pyautogui.click(x, y)
        else:
            pyautogui.click()
        time.sleep(1)

    elif a == "scroll":
        amount = action.get("amount", -3)
        pyautogui.scroll(amount)
        time.sleep(0.5)

    elif a == "type":
        text = action["text"]
        pyautogui.write(text, interval=0.05)
        time.sleep(0.5)

    elif a == "wait":
        seconds = action.get("seconds", 2)
        time.sleep(seconds)


# ============ 主循环 ============

def run_computer_use(task: str):
    client = Anthropic()

    messages = [{"role": "user", "content": task}]

    # 系统提示
    system_prompt = """你是一个能操作电脑的 AI 助手。你可以截图、点击、打字、滚动。

当前任务：在浏览器中打开抖音，搜索并分析一个博主账号。

重要规则：
1. 每次你只能输出 1 个电脑操作动作
2. 先截图看当前屏幕状态，再决定下一步做什么
3. 用中文思考
4. 看到目标信息后，输出一个完整的拆解报告，然后停止

可用的操作类型：
- screenshot: 截图看当前屏幕（这个我会自动执行）
- mouse_move: 移动鼠标到 (x, y) 坐标
- left_click: 左键点击，可选 (x, y)
- scroll: 滚轮滚动，amount 正数向上、负数向下
- key: 输入文本
- keypress: 按键，如 ["ctrl", "l"] 是 Ctrl+L
- type: 输入文本
- wait: 等待秒数

输出格式（必须是合法 JSON）：
{"action": {"type": "操作类型", ...参数}, "thought": "你的思考"}"""

    print("=" * 60)
    print("🤖 Computer Use 启动")
    print(f"📋 任务: {task}")
    print("=" * 60)

    for step in range(20):  # 最多 20 步
        try:
            # 1. 截图
            print(f"\n📍 Step {step + 1}: 截图中...")
            screenshot_b64 = take_screenshot()

            # 2. 构建消息
            content = [
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": screenshot_b64
                }},
                {"type": "text", "text": "这是当前屏幕截图。请决定下一步操作。输出 JSON 格式。"}
            ]

            messages.append({"role": "user", "content": content})

            # 3. 调用 Claude
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=system_prompt,
                messages=messages,
            )

            reply = response.content[0].text
            print(f"  💭 {reply[:200]}")

            # 4. 解析动作
            # 尝试从回复中提取 JSON
            try:
                # 可能被包在 ```json ... ``` 里
                if "```" in reply:
                    json_part = reply.split("```")[1]
                    if json_part.startswith("json"):
                        json_part = json_part[4:]
                    action_data = json.loads(json_part.strip())
                else:
                    action_data = json.loads(reply.strip())
            except json.JSONDecodeError:
                # 如果不是 JSON，可能是纯文本分析结果
                print("\n📊 Claude 返回了分析结果（非操作指令），任务可能已完成")
                save_screenshot(screenshot_b64, f"step{step+1:02d}")
                print(f"\n✅ 完整回复:\n{reply}")
                break

            thought = action_data.get("thought", "")
            action = action_data.get("action", {})

            if not action:
                print("\n✅ 无操作指令，任务完成")
                save_screenshot(screenshot_b64, f"step{step+1:02d}_final")
                break

            # 5. 保存截图
            save_screenshot(screenshot_b64, f"step{step+1:02d}")

            # 6. 执行操作
            action_type = action.get("type", "")
            print(f"  🎬 执行: {action_type} {str(action)[:100]}")

            if action_type == "done" or action_type == "finish":
                print("\n✅ Claude 标记任务完成")
                break

            do_action(action)

            # 7. 把 Claude 的回复加入消息历史
            messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            print(f"  ❌ 出错: {e}")
            traceback.print_exc()
            break

    print("\n" + "=" * 60)
    print("🏁 Computer Use 结束")
    print(f"📂 截图保存在: {SCREENSHOT_DIR}")


# ============ 入口 ============

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ 请先设置环境变量: set ANTHROPIC_API_KEY=你的key")
        print("   获取 key: https://console.anthropic.com/")
        sys.exit(1)

    task = f"""
请完成以下任务：

1. 如果浏览器没有打开，先打开浏览器（按 Win 键，输入 Chrome 或 Edge，回车）
2. 在地址栏输入: {DOUYIN_URL}
3. 等待页面加载
4. 截图查看页面内容
5. 如果页面正常显示，滚动浏览这个博主的主页
6. 记录以下信息：
   - 博主昵称、抖音号
   - 粉丝数、总获赞
   - 个人简介
   - 内容类型（摄影/穿搭/街拍等）
   - 最近5条视频的标题、点赞数
   - 视频风格特征（调色、构图、节奏）
7. 基于以上信息，写一份拆解报告（500字以内），格式参考：
   - 定位分析
   - 内容结构
   - 可复用的点
   - 与马丁鸟的对比

注意：每步操作后等1-2秒让页面加载。
如果遇到验证码或登录弹窗，尽量跳过或关闭。
"""

    run_computer_use(task)
