"""
竞品数据更新脚本
批量抓取对标账号的公开数据，更新到竞品拆解文件

用法:
  python update_competitor_data.py          # 更新所有对标账号
  python update_competitor_data.py --user 48340578326  # 更新单个
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# 导入上面的抓取工具
sys.path.insert(0, str(Path(__file__).parent))
from douyin_scraper import get_user_info

PROJECT_ROOT = Path(__file__).parent.parent
COMPETITOR_DIR = PROJECT_ROOT / "04-竞品研究/对标账号库"

# 对标账号列表 (从README提取)
COMPETITORS = {
    "马丁鸟对标": [
        {"name": "俊杰哥哥", "id": "48340578326", "file": "俊杰哥哥-拆解.md"},
        {"name": "一只大夹子", "id": "2TIMER", "file": "一只大夹子-拆解.md"},
        {"name": "小李是个摄象狮", "id": "Yujiangengmei", "file": "小李是个摄象狮-拆解.md"},
        {"name": "華夏", "id": "huaxia185", "file": "華夏-拆解.md"},
        {"name": "Soso🌀", "id": "4175696", "file": "Soso-拆解.md"},
        {"name": "卡卡宝贝贝", "id": "kk112233445678", "file": "卡卡宝贝贝-拆解.md"},
    ],
    "马丁老师对标": [
        {"name": "痴五安 chammy", "id": None, "file": "痴五安chammy-拆解.md"},
        {"name": "165的岛羊", "id": "daoyang165", "file": "165的岛羊-拆解.md"},
    ]
}


def main():
    print(f"🔄 竞品数据更新 · {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 40)

    updated = 0
    failed = 0

    for group_name, accounts in COMPETITORS.items():
        print(f"\n📋 {group_name}")
        for acc in accounts:
            if not acc["id"]:
                print(f"  ⏭️ {acc['name']}: 无抖音号，跳过")
                continue

            print(f"  🔍 {acc['name']} ({acc['id']})...")
            try:
                info = get_user_info(acc["id"])
                if info:
                    # 更新拆解文件
                    file_path = COMPETITOR_DIR / acc["file"]
                    if file_path.exists():
                        content = file_path.read_text(encoding="utf-8")
                        # 在粉丝量行后添加更新时间
                        update_line = f"\n- **数据更新时间**：{datetime.now().strftime('%Y-%m-%d')}\n"
                        if "数据更新时间" not in content:
                            content = content.rstrip() + update_line
                        file_path.write_text(content, encoding="utf-8")
                    updated += 1
                    print(f"    ✅ {info.get('nickname', '?')} | 粉丝: {info.get('follower', '?')}")
                else:
                    failed += 1
                    print(f"    ⚠️ 无数据返回")
            except Exception as e:
                failed += 1
                print(f"    ❌ {e}")

            time.sleep(2)  # 避免被限流

    print(f"\n{'='*40}")
    print(f"✅ 更新 {updated} 个 | ❌ 失败 {failed} 个")
    print(f"📁 数据更新时间已写入拆解文件")


if __name__ == "__main__":
    main()
