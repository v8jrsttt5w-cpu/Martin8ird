import numpy as np
from PIL import Image
from pathlib import Path

FRAME_DIR = Path(__file__).parent / "frames"


def read_frame(path):
    img = Image.open(str(path)).convert('RGB')
    return np.array(img)


def gray(rgb):
    return np.mean(rgb, axis=2)


def analyze_all():
    for vdir in sorted(FRAME_DIR.glob("v*")):
        if not vdir.is_dir():
            continue
        frames = sorted(vdir.glob("t*.jpg"))
        if not frames:
            continue
        print("\n" + "=" * 60)
        print("Video: %s | Frames: %d" % (vdir.name, len(frames)))
        analyze(frames, vdir)


def analyze(frame_paths, out_dir):
    results = []
    prev_gray = None

    for f in frame_paths:
        rgb = read_frame(f)
        h, w = rgb.shape[:2]
        g = gray(rgb)
        b = float(np.mean(g))
        sat = float(np.mean(np.std(rgb, axis=2)))

        diff = 0.0
        if prev_gray is not None:
            diff = float(np.mean(np.abs(g - prev_gray))) * 100
        prev_gray = g.copy()

        b_change = 0.0
        if results:
            b_change = abs(b - results[-1]["brightness"])

        results.append({
            "time": float(f.stem.replace("t", "").replace("s", "")),
            "brightness": round(b, 1),
            "saturation": round(sat, 1),
            "diff": round(diff, 1),
            "b_change": round(b_change, 1),
            "h": h, "w": w
        })

    avg_b = float(np.mean([r["brightness"] for r in results]))
    b_changes = [r["b_change"] for r in results]
    diffs = [r["diff"] for r in results]
    t_b = float(np.mean(b_changes) + np.std(b_changes) * 1.3)
    t_d = float(np.mean(diffs) + np.std(diffs) * 1.3)

    print("%6s | %6s | %6s | %8s | %6s | %s" % ("Time", "Bright", "Sat", "Diff", "B-Chg", "Tags"))
    print("-" * 70)

    switches = []
    for r in results:
        tags = []
        if r["b_change"] > t_b:
            tags.append("SCENE")
            switches.append(r)
        if r["diff"] > t_d:
            tags.append("MOTION")
        if r["brightness"] < 50:
            tags.append("DARK")
        if r["brightness"] > 210:
            tags.append("BRIGHT")
        print("%5.1fs | %6.1f | %6.1f | %8.1f | %6.1f | %s" % (
            r["time"], r["brightness"], r["saturation"],
            r["diff"], r["b_change"], ", ".join(tags)))

    sw_strs = ["%.1fs" % s["time"] for s in switches]
    print("\n[Summary] Avg Brightness=%.0f | Resolution=%dx%d" % (avg_b, results[0]["w"], results[0]["h"]))
    print("Scene Changes(%d): %s" % (len(switches), ", ".join(sw_strs)))

    # Structure inference
    print("\n[Structure]")
    segments = [
        ("0-3s", 0, 3),
        ("3-8s", 3, 8),
        ("8-20s", 8, 20),
        ("20s+", 20, 999)
    ]
    for label, t0, t1 in segments:
        seg = [r for r in results if t0 < r["time"] <= t1]
        if not seg:
            continue
        seg_b = float(np.mean([r["brightness"] for r in seg]))
        seg_d = float(np.mean([r["diff"] for r in seg]))
        sw_in = len([s for s in switches if t0 < s["time"] <= t1])
        print("  %s: brightness=%.0f motion=%.0f switches=%d" % (label, seg_b, seg_d, sw_in))

    # Save report
    report = out_dir / "frame_data.txt"
    with open(str(report), "w", encoding="utf-8") as f:
        f.write("Frame Data\n")
        f.write("Resolution: %dx%d\n" % (results[0]["w"], results[0]["h"]))
        f.write("Avg Brightness: %.0f\n" % avg_b)
        f.write("Scene Changes: %s\n" % ", ".join(sw_strs))
        for r in results:
            tags = []
            if r["b_change"] > t_b: tags.append("SCENE")
            if r["brightness"] < 50: tags.append("DARK")
            f.write("%.1fs b=%.0f %s\n" % (r["time"], r["brightness"], ",".join(tags)))
    print("[Report] %s" % report)


if __name__ == "__main__":
    analyze_all()
