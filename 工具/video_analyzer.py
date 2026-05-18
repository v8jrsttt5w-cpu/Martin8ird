"""
视频结构分析工具
从视频提取关键帧 → AI分析结构 → 写入爆款结构库

用法:
  python video_analyzer.py analyze <视频路径>
  python video_analyzer.py batch <文件夹路径>
"""

import sys
import io
import json
import cv2
import os
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOL_DIR = Path(__file__).parent
FRAME_DIR = TOOL_DIR / "frames"
SYSTEM_ROOT = TOOL_DIR.parent


def extract_keyframes(video_path, interval=2):
    """每N秒提取一帧，返回帧路径列表"""
    # 处理中文路径：先复制到临时英文路径再处理
    video_path = Path(video_path)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"[错误] 无法打开视频: {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"[视频信息] {video_path.name}")
    print(f"  时长: {duration:.1f}秒 | FPS: {fps:.1f} | 总帧数: {total_frames}")

    # 用纯ASCII路径避免编码问题
    out_dir = FRAME_DIR / f"v{datetime.now().strftime('%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    frame_interval = int(fps * interval)
    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            timestamp = frame_count / fps
            fname = f"t{timestamp:05.1f}s.jpg"
            fpath = out_dir / fname
            # 用 imencode 绕过 Windows 中文路径问题
            _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            with open(str(fpath), 'wb') as f:
                f.write(buf.tobytes())
            frames.append({
                "file": str(fpath),
                "path": fpath.name,
                "time": round(timestamp, 1)
            })
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"[完成] 提取 {saved_count} 个关键帧 → {out_dir}")
    return frames, out_dir, duration


def analyze_structure(frames, duration, video_name):
    """生成结构分析报告模板"""
    report = f"""# 视频结构分析: {video_name}

> 自动分析 · {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 视频时长: {duration:.1f}秒 | 提取帧数: {len(frames)}张

---

## 时间轴拆解

"""
    for i, f in enumerate(frames):
        time_pct = f["time"] / duration * 100 if duration > 0 else 0
        report += f"### [{f['time']:.1f}s] ({time_pct:.0f}%) — 帧: {f['path']}\n\n"
        report += f"![{f['path']}]({f['path']})\n\n"
        report += "<!-- AI分析: 这个画面在做什么? 属于什么阶段(钩子/问题/方法/成片/引导)? -->\n\n"

    report += """---

## AI 结构判断

| 时间段 | 阶段 | 内容判断 |
|--------|------|---------|
"""
    for i, f in enumerate(frames):
        report += f"| {f['time']:.1f}s | 待分析 | |\n"

    report += """
---

## 结构结论

- **开头钩子类型**: 待判断
- **核心内容节奏**: 待判断
- **结尾引导方式**: 待判断
- **BGM风格推测**: 待判断
- **整体结构归类**: 待判断

## 可复用元素

- 钩子:
- 节奏:
- 视觉风格:
"""
    return report


def batch_analyze(folder_path):
    """批量分析文件夹内所有视频"""
    folder = Path(folder_path)
    videos = list(folder.glob("*.mp4")) + list(folder.glob("*.mov")) + list(folder.glob("*.avi"))
    videos.extend(list(folder.glob("*.mkv")) + list(folder.glob("*.webm")))

    if not videos:
        print(f"[无视频] {folder} 中没有找到视频文件")
        print("支持的格式: mp4, mov, avi, mkv, webm")
        return

    print(f"[批量分析] 找到 {len(videos)} 个视频\n")

    results = []
    for v in videos:
        print(f"\n{'='*50}")
        frames, out_dir, duration = extract_keyframes(v, interval=2)
        if frames:
            report = analyze_structure(frames, duration, v.name)
            report_path = out_dir / "结构分析.md"
            report_path.write_text(report, encoding='utf-8')
            print(f"[报告] {report_path}")
            results.append({
                "video": str(v),
                "frames_dir": str(out_dir),
                "report": str(report_path),
                "duration": duration,
                "frame_count": len(frames)
            })

    print(f"\n{'='*50}")
    print(f"[完成] 共分析 {len(results)} 个视频")
    print(f"帧文件目录: {FRAME_DIR}")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(0)

    action = sys.argv[1]
    target = sys.argv[2]

    if action == "analyze":
        frames, out_dir, duration = extract_keyframes(target, interval=2)
        if frames:
            report = analyze_structure(frames, duration, Path(target).name)
            report_path = out_dir / "结构分析.md"
            report_path.write_text(report, encoding='utf-8')
            print(f"\n[报告已生成] {report_path}")
            print("下一步: 在对话中说「分析视频结构」，AI会读取关键帧并拆解")

    elif action == "batch":
        batch_analyze(target)

    else:
        print(f"未知操作: {action}")
