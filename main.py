#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外卖比价器主程序
自动爬取美团、饿了么、京东到家的外卖数据，进行跨平台比价

数据范围：北京朝阳区
更新频率：每小时
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src import (
    fetch_all_platforms,
    compare_items,
    compare_same_restaurant,
    save_data,
    generate_readme,
)

# 配置
DATA_DIR = Path("data")
RAW_DATA_FILE = DATA_DIR / "raw_data.json"
COMPARISON_FILE = DATA_DIR / "comparisons.json"
README_FILE = Path("README.md")

# 北京朝阳区坐标
BEIJING_CHAOYANG = {
    "lat": 39.9210,
    "lng": 116.4430,
}


def main():
    print("=" * 60)
    print("🍔 外卖比价器")
    print("=" * 60)
    print(f"📍 位置: 北京市朝阳区")
    print(f"🕐 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 确保数据目录存在
    DATA_DIR.mkdir(exist_ok=True)

    # 1. 抓取数据
    print("【1/4】抓取外卖数据...")
    restaurants = fetch_all_platforms(
        lat=BEIJING_CHAOYANG["lat"],
        lng=BEIJING_CHAOYANG["lng"],
        limit=15,  # 每个平台15家商家
    )
    print()

    # 2. 保存原始数据
    print("【2/4】保存原始数据...")
    save_data(restaurants, str(RAW_DATA_FILE))
    print(f"  ✓ 已保存到 {RAW_DATA_FILE}")
    print()

    # 3. 进行比价
    print("【3/4】进行跨平台比价...")

    # 跨平台比价（同类商品）
    comparisons = compare_items(restaurants)
    print(f"  ✓ 发现 {len(comparisons)} 种可比价商品")

    # 同品牌比价
    same_brand = compare_same_restaurant(restaurants)
    print(f"  ✓ 同品牌比价: {len(same_brand)} 条结果")
    print()

    # 4. 生成报告
    print("【4/4】生成报告...")
    generate_readme(comparisons, same_brand, restaurants, str(README_FILE))
    print()

    # 输出统计
    print("=" * 60)
    print("📊 统计摘要")
    print("=" * 60)
    print(f"  商家总数: {len(restaurants)} 家")
    print(f"  可比价商品: {len(comparisons)} 种")

    if comparisons:
        # 找出最省钱的
        top_saveings = comparisons[0]
        print(f"\n  💰 最省钱商品: {top_saveings.item_name}")
        print(f"     价差: ¥{top_saveings.price_diff:.1f}")
        print(f"     最便宜: {top_saveings.cheapest_platform}")

        # 平台最便宜统计
        platform_wins = {}
        for c in comparisons:
            p = c.cheapest_platform
            platform_wins[p] = platform_wins.get(p, 0) + 1

        print("\n  🏆 平台胜出次数:")
        for p, count in sorted(platform_wins.items(), key=lambda x: x[1], reverse=True):
            print(f"     {p}: {count} 次")

    print()
    print("✅ 完成！")


if __name__ == "__main__":
    main()
