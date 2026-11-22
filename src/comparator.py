"""
外卖比价逻辑
"""
import re
from typing import List, Dict
from .models import Restaurant, MenuItem, PriceComparison

# 菜品名称标准化映射
# 将相似名称映射到统一key
NAME_NORMALIZE = {
    "巨无霸": "巨无霸",
    "big mac": "巨无霸",

    "薯条(大)": "薯条大",
    "薯条（大）": "薯条大",
    "大薯条": "薯条大",

    "麦辣鸡腿堡": "麦辣鸡腿堡",
    "香辣鸡腿堡": "香辣鸡腿堡",

    "生椰拿铁": "生椰拿铁",
    "生椰拿铁(大杯)": "生椰拿铁",

    "多肉葡萄": "多肉葡萄",
    "多肉葡萄(大杯)": "多肉葡萄",

    "可乐(大)": "可乐大",
    "可乐（大）": "可乐大",
    "大杯可乐": "可乐大",
}

def normalize_name(name: str) -> str:
    """标准化菜品名称"""
    # 先查映射表
    if name in NAME_NORMALIZE:
        return NAME_NORMALIZE[name]

    # 移除常见变体
    name = re.sub(r'[（(].*?[）)]', '', name)  # 移除括号内容
    name = re.sub(r'\s+', '', name)  # 移除空格
    name = name.strip()

    # 检查是否包含关键词
    for key in NAME_NORMALIZE:
        if key in name or name in key:
            return NAME_NORMALIZE[key]

    return name

def find_similar_items(name: str, items: List[MenuItem]) -> List[MenuItem]:
    """找到相似名称的菜品"""
    normalized = normalize_name(name)
    results = []

    for item in items:
        item_normalized = normalize_name(item.name)
        # 完全匹配
        if item_normalized == normalized:
            results.append(item)
        # 包含关系
        elif normalized in item_normalized or item_normalized in normalized:
            results.append(item)
        # 关键词重叠
        elif len(set(normalized) & set(item_normalized)) > len(normalized) * 0.6:
            results.append(item)

    return results

def compare_items(restaurants: List[Restaurant]) -> List[PriceComparison]:
    """
    比较所有商家的同类商品
    返回比价结果列表
    """
    # 收集所有商品及其来源
    all_items: Dict[str, List[Dict]] = {}

    for restaurant in restaurants:
        for item in restaurant.menu:
            key = normalize_name(item.name)
            if key not in all_items:
                all_items[key] = []

            all_items[key].append({
                "platform": restaurant.platform,
                "restaurant": restaurant.name,
                "location": restaurant.location,
                "price": item.price,
                "original_price": item.original_price,
                "delivery_fee": restaurant.delivery_fee,
                "delivery_time": restaurant.delivery_time,
                "min_order": restaurant.min_order,
                "rating": restaurant.rating,
                "total_price": item.price + restaurant.delivery_fee,
            })

    # 生成比价结果
    comparisons = []

    for key, items in all_items.items():
        # 只比较有多个来源的商品
        if len(items) < 2:
            continue

        # 检查是否有不同平台
        platforms = set(item["platform"] for item in items)
        if len(platforms) < 2:
            continue

        # 找出最便宜的
        cheapest = min(items, key=lambda x: x["total_price"])
        most_expensive = max(items, key=lambda x: x["total_price"])

        comparison = PriceComparison(
            item_name=key,
            category=items[0].get("category", ""),
            prices=sorted(items, key=lambda x: x["total_price"]),
            cheapest_platform=cheapest["platform"],
            cheapest_price=cheapest["total_price"],
            price_diff=most_expensive["total_price"] - cheapest["total_price"],
        )
        comparisons.append(comparison)

    # 按价差排序
    comparisons.sort(key=lambda x: x.price_diff, reverse=True)

    return comparisons

def compare_same_restaurant(restaurants: List[Restaurant]) -> List[PriceComparison]:
    """
    比较同一品牌在不同平台的价格
    例如：麦当劳在美团vs饿了么vs京东
    """
    # 按品牌分组
    brands: Dict[str, List[Restaurant]] = {}

    for r in restaurants:
        # 标准化品牌名
        brand = r.name
        if brand not in brands:
            brands[brand] = []
        brands[brand].append(r)

    comparisons = []

    for brand, rest_list in brands.items():
        # 检查是否有多平台
        platforms = set(r.platform for r in rest_list)
        if len(platforms) < 2:
            continue

        # 比较每个菜品
        for rest in rest_list:
            for item in rest.menu:
                key = normalize_name(item.name)

                # 找其他平台的同款
                other_items = []
                for other_rest in rest_list:
                    if other_rest.platform != rest.platform:
                        for other_item in other_rest.menu:
                            if normalize_name(other_item.name) == key:
                                other_items.append({
                                    "platform": other_rest.platform,
                                    "restaurant": other_rest.name,
                                    "location": other_rest.location,
                                    "price": other_item.price,
                                    "delivery_fee": other_rest.delivery_fee,
                                    "total_price": other_item.price + other_rest.delivery_fee,
                                })

                if other_items:
                    # 添加当前商品
                    current = {
                        "platform": rest.platform,
                        "restaurant": rest.name,
                        "location": rest.location,
                        "price": item.price,
                        "delivery_fee": rest.delivery_fee,
                        "total_price": item.price + rest.delivery_fee,
                    }
                    all_items = [current] + other_items

                    cheapest = min(all_items, key=lambda x: x["total_price"])
                    expensive = max(all_items, key=lambda x: x["total_price"])

                    comp = PriceComparison(
                        item_name=f"{brand} - {key}",
                        category=item.category,
                        prices=all_items,
                        cheapest_platform=cheapest["platform"],
                        cheapest_price=cheapest["total_price"],
                        price_diff=expensive["total_price"] - cheapest["total_price"],
                    )
                    comparisons.append(comp)

    # 去重并排序
    seen = set()
    unique = []
    for c in comparisons:
        key = f"{c.item_name}_{tuple(sorted((p['platform'] for p in c.prices)))}"
        if key not in seen:
            seen.add(key)
            unique.append(c)

    unique.sort(key=lambda x: x.price_diff, reverse=True)
    return unique

PLATFORM_NAMES = {
    "meituan": "美团",
    "eleme": "饿了么",
    "jd": "京东",
}

def get_platform_name(platform: str) -> str:
    return PLATFORM_NAMES.get(platform, platform)
