"""
外卖数据模型
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json

@dataclass
class MenuItem:
    """菜品/商品"""
    name: str
    price: float
    original_price: Optional[float] = None
    category: str = ""  # 分类：快餐、奶茶、火锅等
    description: str = ""
    image_url: str = ""
    monthly_sales: int = 0  # 月销量

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "original_price": self.original_price,
            "category": self.category,
            "description": self.description,
            "image_url": self.image_url,
            "monthly_sales": self.monthly_sales,
        }

@dataclass
class Restaurant:
    """商家/餐厅"""
    name: str
    platform: str  # meituan, eleme, jd
    location: str  # 位置描述
    distance: float  # 距离(km)
    delivery_fee: float  # 配送费
    delivery_time: int  # 预计配送时间(分钟)
    rating: float  # 评分
    min_order: float  # 起送价
    menu: List[MenuItem] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "platform": self.platform,
            "location": self.location,
            "distance": self.distance,
            "delivery_fee": self.delivery_fee,
            "delivery_time": self.delivery_time,
            "rating": self.rating,
            "min_order": self.min_order,
            "menu": [item.to_dict() for item in self.menu],
        }

@dataclass
class PriceComparison:
    """比价结果"""
    item_name: str  # 菜品名称
    category: str  # 分类
    prices: List[dict] = field(default_factory=list)  # [{platform, restaurant, price, delivery_fee, total}]
    cheapest_platform: str = ""
    cheapest_price: float = 0
    price_diff: float = 0  # 价差

    def to_dict(self):
        return {
            "item_name": self.item_name,
            "category": self.category,
            "prices": self.prices,
            "cheapest_platform": self.cheapest_platform,
            "cheapest_price": self.cheapest_price,
            "price_diff": self.price_diff,
        }

def save_data(restaurants: List[Restaurant], filepath: str):
    """保存数据到JSON"""
    data = {
        "update_time": datetime.now().isoformat(),
        "restaurants": [r.to_dict() for r in restaurants],
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(filepath: str) -> List[Restaurant]:
    """从JSON加载数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        restaurants = []
        for r in data.get("restaurants", []):
            menu = [MenuItem(**item) for item in r.get("menu", [])]
            restaurants.append(Restaurant(
                name=r["name"],
                platform=r["platform"],
                location=r["location"],
                distance=r["distance"],
                delivery_fee=r["delivery_fee"],
                delivery_time=r["delivery_time"],
                rating=r["rating"],
                min_order=r["min_order"],
                menu=menu,
            ))
        return restaurants
    except FileNotFoundError:
        return []
