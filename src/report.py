"""
生成比价报告
"""
from datetime import datetime
from typing import List
from .models import Restaurant, PriceComparison
from .comparator import get_platform_name

def generate_readme(comparisons: List[PriceComparison],
                   same_brand: List[PriceComparison],
                   restaurants: List[Restaurant],
                   filepath: str = "README.md"):
    """生成Markdown报告"""

    # 统计
    platform_count = {}
    for r in restaurants:
        platform_count[r.platform] = platform_count.get(r.platform, 0) + 1

    # 省钱统计
    total_savings = sum(c.price_diff for c in comparisons[:20])
    avg_savings = total_savings / min(len(comparisons), 20) if comparisons else 0

    readme = f"""# 🍔 外卖比价器

> 自动爬取美团、饿了么、京东到家的外卖数据，帮你找到最便宜的外卖！

**📍 位置**: 北京市朝阳区
**⏰ 更新频率**: 每小时自动更新
**🔄 最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 数据统计

| 指标 | 数值 |
|------|------|
| 商家总数 | **{len(restaurants)}** 家 |
| 美团商家 | **{platform_count.get('meituan', 0)}** 家 |
| 饿了么商家 | **{platform_count.get('eleme', 0)}** 家 |
| 京东到家商家 | **{platform_count.get('jd', 0)}** 家 |
| 可比价商品 | **{len(comparisons)}** 种 |
| 平均可省 | **¥{avg_savings:.1f}** |

---

## 💰 跨平台比价 TOP 20

> 不同平台的同类商品比价，帮你找到最便宜的！

| 排名 | 商品 | 最便宜 | 价格 | 价差 | 详情 |
|:----:|------|:------:|-----:|-----:|------|
"""

    for i, comp in enumerate(comparisons[:20], 1):
        platform_emoji = {"meituan": "🟡", "eleme": "🔵", "jd": "🔴"}.get(comp.cheapest_platform, "⚪")
        detail = f"{len(comp.prices)}家平台"
        readme += f"| {i} | {comp.item_name} | {platform_emoji} {get_platform_name(comp.cheapest_platform)} | ¥{comp.cheapest_price:.1f} | ¥{comp.price_diff:.1f} | {detail} |\n"

    readme += """
---

## 🏪 同品牌比价 TOP 20

> 同一品牌在不同平台的价格对比

| 排名 | 品牌 - 商品 | 最便宜 | 价格 | 价差 |
|:----:|------------|:------:|-----:|-----:|
"""

    for i, comp in enumerate(same_brand[:20], 1):
        platform_emoji = {"meituan": "🟡", "eleme": "🔵", "jd": "🔴"}.get(comp.cheapest_platform, "⚪")
        readme += f"| {i} | {comp.item_name} | {platform_emoji} {get_platform_name(comp.cheapest_platform)} | ¥{comp.cheapest_price:.1f} | ¥{comp.price_diff:.1f} |\n"

    readme += """
---

## 📋 详细比价

<details>
<summary>点击展开完整比价数据（含所有平台价格）</summary>

"""

    for comp in comparisons[:50]:
        readme += f"### {comp.item_name}\n\n"
        readme += "| 平台 | 商家 | 商品价 | 配送费 | 总价 | 评分 | 配送时间 |\n"
        readme += "|------|------|-------:|-------:|-----:|-----:|---------:|\n"

        for p in comp.prices:
            platform_name = get_platform_name(p["platform"])
            readme += f"| {platform_name} | {p['restaurant']} | ¥{p['price']:.1f} | ¥{p['delivery_fee']:.1f} | **¥{p['total_price']:.1f}** | ⭐{p['rating']} | {p['delivery_time']}分钟 |\n"

        readme += f"\n💡 **建议**: 选择 {get_platform_name(comp.cheapest_platform)}，可省 ¥{comp.price_diff:.1f}\n\n"

    readme += """</details>

---

## 🏆 平台对比

"""

    # 平台统计
    for platform in ["meituan", "eleme", "jd"]:
        name = get_platform_name(platform)
        emoji = {"meituan": "🟡", "eleme": "🔵", "jd": "🔴"}.get(platform, "⚪")

        platform_rests = [r for r in restaurants if r.platform == platform]
        if not platform_rests:
            continue

        avg_rating = sum(r.rating for r in platform_rests) / len(platform_rests)
        avg_delivery = sum(r.delivery_time for r in platform_rests) / len(platform_rests)
        avg_fee = sum(r.delivery_fee for r in platform_rests) / len(platform_rests)

        # 统计最便宜次数
        cheapest_count = sum(1 for c in comparisons if c.cheapest_platform == platform)

        readme += f"""### {emoji} {name}

| 指标 | 数值 |
|------|------|
| 商家数 | **{len(platform_rests)}** 家 |
| 平均评分 | ⭐ **{avg_rating:.1f}** |
| 平均配送时间 | **{avg_delivery:.0f}** 分钟 |
| 平均配送费 | ¥**{avg_fee:.1f}** |
| 最便宜次数 | **{cheapest_count}** 次 |

"""

    readme += """---

## 📱 数据来源

| 平台 | 说明 |
|------|------|
| 🟡 美团外卖 | 中国最大的外卖平台之一 |
| 🔵 饿了么 | 阿里巴巴旗下外卖平台 |
| 🔴 京东到家 | 京东旗下即时零售平台 |

---

## ⚙️ 工作原理

1. **每小时自动运行** GitHub Actions
2. **爬取三家平台** 北京朝阳区的外卖数据
3. **智能匹配** 同一商品/相似商品
4. **计算总价** 商品价格 + 配送费
5. **生成报告** Markdown 表格展示

---

## 💡 使用提示

- 🟡 **美团**: 商家最多，配送快，价格中等
- 🔵 **饿了么**: 优惠多，价格较低，补贴力度大
- 🔴 **京东到家**: 配送稳定，但价格通常较高

**省钱技巧**:
1. 对比三家平台价格
2. 注意配送费（有些免配送费）
3. 关注满减活动
4. 新用户有首单优惠

---

## 🚧 注意事项

> ⚠️ 当前数据为**模拟数据**，用于演示功能。
>
> 真实数据接入需要：
> - 美团/饿了么/京东的API接口
> - 反爬虫处理（签名、设备指纹等）
> - Cookie/Token 认证
>
> 如果你有相关API资源，欢迎贡献代码！

---

## 📦 技术栈

- Python 3.10+
- GitHub Actions (定时任务)
- 数据模拟 (待接入真实API)

---

*Last updated: {datetime.now().isoformat()}*

---

<div align="center">

**Made with ❤️ for hungry developers**

</div>
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(readme)

    print(f"✅ README.md 已更新")
