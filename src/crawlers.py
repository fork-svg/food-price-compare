"""
外卖平台爬虫模块
支持美团、饿了么、京东到家
"""
import random
import time
from typing import List
from .models import Restaurant, MenuItem

# 北京朝阳区坐标
BEIJING_CHAOYANG = {
    "lat": 39.9210,
    "lng": 116.4430,
    "name": "北京市朝阳区"
}

# ==================== 美团爬虫 ====================

class MeituanCrawler:
    """
    美团外卖爬虫

    注意：真实API需要：
    1. 请求签名 (sign参数)
    2. 设备指纹 (__skwm, __skwq)
    3. Cookie认证
    4. 反爬验证

    当前使用模拟数据演示功能
    """

    API_BASE = "https://waimai.meituan.com/api/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)",
        "Referer": "https://waimai.meituan.com/",
    }

    def __init__(self, lat: float = None, lng: float = None):
        self.lat = lat or BEIJING_CHAOYANG["lat"]
        self.lng = lng or BEIJING_CHAOYANG["lng"]

    def fetch_restaurants(self, limit: int = 20) -> List[Restaurant]:
        """获取商家列表"""
        # TODO: 接入真实API
        # url = f"{self.API_BASE}poi/filter"
        # params = {"lat": self.lat, "lng": self.lng, "sort": "default"}
        return self._mock_restaurants(limit)

    def _mock_restaurants(self, limit: int) -> List[Restaurant]:
        """模拟数据 - 替换为真实爬取逻辑"""
        restaurants = []

        # 模拟常见连锁品牌
        brands = [
            ("麦当劳", "西式快餐", 4.5, 2.5),
            ("肯德基", "西式快餐", 4.3, 2.0),
            ("必胜客", "西式快餐", 4.2, 3.0),
            ("海底捞", "火锅", 4.7, 6.0),
            ("喜茶", "奶茶", 4.6, 5.0),
            ("奈雪的茶", "奶茶", 4.5, 6.0),
            ("瑞幸咖啡", "咖啡", 4.4, 4.0),
            ("星巴克", "咖啡", 4.5, 5.5),
            ("真功夫", "中式快餐", 4.1, 2.5),
            ("吉野家", "日式快餐", 4.2, 2.0),
            ("味千拉面", "日式", 4.0, 2.5),
            ("老乡鸡", "中式快餐", 4.3, 2.0),
        ]

        for name, cat, rating, min_order in brands[:limit]:
            menu = self._generate_menu(name, cat)
            restaurants.append(Restaurant(
                name=name,
                platform="meituan",
                location=f"朝阳区{random.choice(['三里屯', '国贸', '望京', '大望路', '双井'])}店",
                distance=round(random.uniform(0.5, 5.0), 1),
                delivery_fee=round(random.uniform(0, 6), 1),
                delivery_time=random.randint(25, 50),
                rating=rating,
                min_order=min_order,
                menu=menu,
            ))

        return restaurants

    def _generate_menu(self, brand: str, category: str) -> List[MenuItem]:
        """生成模拟菜单"""
        menus = {
            "麦当劳": [
                ("巨无霸", 24.0), ("薯条(大)", 13.0), ("麦辣鸡腿堡", 19.0),
                ("麦旋风", 12.0), ("可乐(大)", 10.0), ("麦乐鸡(5块)", 13.5),
            ],
            "肯德基": [
                ("香辣鸡腿堡", 19.0), ("原味鸡(1块)", 13.0), ("薯条(大)", 12.0),
                ("蛋挞", 8.0), ("可乐(大)", 10.0), ("新奥尔良烤翅(2块)", 13.0),
            ],
            "必胜客": [
                ("超级至尊披萨(9寸)", 69.0), ("奶油蘑菇汤", 22.0), ("烤翅(4块)", 28.0),
                ("蒜香面包", 15.0), ("可乐", 12.0), ("凯撒沙拉", 28.0),
            ],
            "海底捞": [
                ("番茄锅底", 58.0), ("麻辣锅底", 48.0), ("肥牛卷", 58.0),
                ("虾滑", 48.0), ("毛肚", 48.0), ("蔬菜拼盘", 32.0),
            ],
            "喜茶": [
                ("多肉葡萄", 29.0), ("芝芝芒芒", 32.0), ("烤黑糖波波", 25.0),
                ("满杯红柚", 27.0), ("纯绿妍", 15.0), ("芋泥波波", 28.0),
            ],
            "奈雪的茶": [
                ("霸气芝士草莓", 32.0), ("霸气橙子", 29.0), ("宝藏茶", 27.0),
                ("软欧包", 18.0), ("鸭屎香柠檬茶", 22.0), ("芋泥麻薯", 25.0),
            ],
            "瑞幸咖啡": [
                ("生椰拿铁", 22.0), ("厚乳拿铁", 19.0), ("美式咖啡", 12.0),
                ("卡布奇诺", 18.0), ("摩卡", 20.0), ("瑞纳冰", 25.0),
            ],
            "星巴克": [
                ("拿铁(大杯)", 33.0), ("美式(大杯)", 27.0), ("卡布奇诺(大杯)", 32.0),
                ("摩卡(大杯)", 35.0), ("星冰乐", 36.0), ("馥芮白", 35.0),
            ],
            "真功夫": [
                ("香菇鸡腿饭", 25.0), ("冬菇鸡腿肉饭", 26.0), ("排骨饭", 28.0),
                ("半边鸡", 32.0), ("蒸蛋", 8.0), ("例汤", 8.0),
            ],
            "吉野家": [
                ("牛肉饭(大)", 28.0), ("照烧鸡排饭", 26.0), ("猪排饭", 30.0),
                ("温泉蛋", 5.0), ("味噌汤", 8.0), ("沙拉", 12.0),
            ],
            "味千拉面": [
                ("豚骨拉面", 32.0), ("叉烧拉面", 38.0), ("味千炒饭", 22.0),
                ("煎饺(6个)", 18.0), ("唐扬鸡块", 18.0), ("可尔必思", 12.0),
            ],
            "老乡鸡": [
                ("肥西老母鸡汤", 35.0), ("梅菜扣肉饭", 22.0), ("鸡杂饭", 20.0),
                ("竹笋蒸鸡翅", 18.0), ("米饭", 2.0), ("酸梅汤", 8.0),
            ],
        }

        items = []
        for name, price in menus.get(brand, [("招牌菜", 25.0), ("小吃", 12.0), ("饮料", 8.0)]):
            items.append(MenuItem(
                name=name,
                price=price,
                original_price=price * random.uniform(1.1, 1.3) if random.random() > 0.5 else None,
                category=category,
                monthly_sales=random.randint(100, 5000),
            ))
        return items


# ==================== 饿了么爬虫 ====================

class ElemeCrawler:
    """
    饿了么爬虫

    注意：真实API需要：
    1. 加密签名 (sign)
    2. 设备ID
    3. 位置信息
    4. Cookie/Token

    当前使用模拟数据
    """

    API_BASE = "https://h5.ele.me/restapi/"

    def __init__(self, lat: float = None, lng: float = None):
        self.lat = lat or BEIJING_CHAOYANG["lat"]
        self.lng = lng or BEIJING_CHAOYANG["lng"]

    def fetch_restaurants(self, limit: int = 20) -> List[Restaurant]:
        """获取商家列表"""
        # TODO: 接入真实API
        return self._mock_restaurants(limit)

    def _mock_restaurants(self, limit: int) -> List[Restaurant]:
        """模拟数据"""
        restaurants = []

        # 饿了么商家（与美团有重叠也有不同）
        brands = [
            ("麦当劳", "西式快餐", 4.6, 2.5),
            ("肯德基", "西式快餐", 4.4, 2.0),
            ("德克士", "西式快餐", 4.0, 1.8),
            ("喜茶", "奶茶", 4.7, 5.0),
            ("奈雪的茶", "奶茶", 4.6, 6.0),
            ("一点点", "奶茶", 4.3, 3.5),
            ("CoCo都可", "奶茶", 4.2, 3.0),
            ("瑞幸咖啡", "咖啡", 4.5, 4.0),
            ("Manner", "咖啡", 4.6, 4.5),
            ("老乡鸡", "中式快餐", 4.4, 2.0),
            ("大米先生", "中式快餐", 4.2, 1.8),
            ("杨国福麻辣烫", "麻辣烫", 4.1, 2.0),
        ]

        for name, cat, rating, min_order in brands[:limit]:
            menu = self._generate_menu(name, cat)
            restaurants.append(Restaurant(
                name=name,
                platform="eleme",
                location=f"朝阳区{random.choice(['三里屯', '国贸', '望京', '大望路', '双井', 'CBD'])}店",
                distance=round(random.uniform(0.3, 4.5), 1),
                delivery_fee=round(random.uniform(0, 5), 1),
                delivery_time=random.randint(20, 45),
                rating=rating,
                min_order=min_order,
                menu=menu,
            ))

        return restaurants

    def _generate_menu(self, brand: str, category: str) -> List[MenuItem]:
        """生成模拟菜单 - 饿了么价格通常略低"""
        menus = {
            "麦当劳": [
                ("巨无霸", 23.0), ("薯条(大)", 12.5), ("麦辣鸡腿堡", 18.0),
                ("麦旋风", 11.5), ("可乐(大)", 9.5), ("麦乐鸡(5块)", 13.0),
            ],
            "肯德基": [
                ("香辣鸡腿堡", 18.5), ("原味鸡(1块)", 12.5), ("薯条(大)", 11.5),
                ("蛋挞", 7.5), ("可乐(大)", 9.5), ("新奥尔良烤翅(2块)", 12.5),
            ],
            "德克士": [
                ("脆皮炸鸡", 12.0), ("鸡腿堡", 15.0), ("薯条", 10.0),
                ("鸡块", 10.0), ("可乐", 8.0), ("蛋挞", 6.0),
            ],
            "喜茶": [
                ("多肉葡萄", 28.0), ("芝芝芒芒", 31.0), ("烤黑糖波波", 24.0),
                ("满杯红柚", 26.0), ("纯绿妍", 14.0), ("芋泥波波", 27.0),
            ],
            "一点点": [
                ("波霸奶茶", 15.0), ("四季春茶", 12.0), ("冰淇淋红茶", 16.0),
                ("椰果奶茶", 14.0), ("阿萨姆红茶", 10.0), ("柠檬绿", 13.0),
            ],
            "CoCo都可": [
                ("百香双响炮", 16.0), ("鲜百香双响炮", 18.0), ("珍珠奶茶", 14.0),
                ("椰果奶茶", 13.0), ("柠檬梅子", 15.0), ("鲜柠檬", 14.0),
            ],
            "Manner": [
                ("拿铁", 15.0), ("美式", 10.0), ("澳白", 18.0),
                ("卡布奇诺", 16.0), ("dirty", 20.0), ("手冲", 25.0),
            ],
            "大米先生": [
                ("回锅肉饭", 18.0), ("番茄炒蛋饭", 15.0), ("红烧排骨饭", 22.0),
                ("宫保鸡丁饭", 17.0), ("米饭", 2.0), ("例汤", 5.0),
            ],
            "杨国福麻辣烫": [
                ("麻辣烫(小份)", 22.0), ("麻辣烫(大份)", 32.0), ("冒菜", 28.0),
                ("拌菜", 18.0), ("饮料", 5.0), ("加面", 3.0),
            ],
        }

        # 复用其他品牌的菜单
        if brand not in menus:
            base_menus = {
                "奈雪的茶": [("霸气芝士草莓", 31.0), ("霸气橙子", 28.0)],
                "瑞幸咖啡": [("生椰拿铁", 21.0), ("厚乳拿铁", 18.0)],
                "老乡鸡": [("肥西老母鸡汤", 34.0), ("梅菜扣肉饭", 21.0)],
            }
            items_data = base_menus.get(brand, [("招牌菜", 24.0), ("小吃", 10.0)])
        else:
            items_data = menus[brand]

        items = []
        for name, price in items_data:
            items.append(MenuItem(
                name=name,
                price=price,
                original_price=price * random.uniform(1.1, 1.25) if random.random() > 0.6 else None,
                category=category,
                monthly_sales=random.randint(100, 5000),
            ))
        return items


# ==================== 京东到家爬虫 ====================

class JDDaojiaCrawler:
    """
    京东到家/京东外卖爬虫

    注意：京东外卖2023年上线，API较新
    需要：
    1. 京东登录态
    2. 地址信息
    3. 签名验证

    当前使用模拟数据
    """

    API_BASE = "https://daojia.jd.com/"

    def __init__(self, lat: float = None, lng: float = None):
        self.lat = lat or BEIJING_CHAOYANG["lat"]
        self.lng = lng or BEIJING_CHAOYANG["lng"]

    def fetch_restaurants(self, limit: int = 20) -> List[Restaurant]:
        """获取商家列表"""
        # TODO: 接入真实API
        return self._mock_restaurants(limit)

    def _mock_restaurants(self, limit: int) -> List[Restaurant]:
        """模拟数据 - 京东到家商家数量较少"""
        restaurants = []

        brands = [
            ("麦当劳", "西式快餐", 4.4, 2.5),
            ("肯德基", "西式快餐", 4.3, 2.0),
            ("必胜客", "西式快餐", 4.1, 3.0),
            ("瑞幸咖啡", "咖啡", 4.3, 4.0),
            ("真功夫", "中式快餐", 4.0, 2.5),
            ("吉野家", "日式快餐", 4.1, 2.0),
        ]

        for name, cat, rating, min_order in brands[:limit]:
            menu = self._generate_menu(name, cat)
            restaurants.append(Restaurant(
                name=name,
                platform="jd",
                location=f"朝阳区{random.choice(['三里屯', '国贸', '望京', '朝阳门'])}店",
                distance=round(random.uniform(0.8, 6.0), 1),
                delivery_fee=round(random.uniform(2, 8), 1),  # 京东配送费通常较高
                delivery_time=random.randint(30, 60),
                rating=rating,
                min_order=min_order,
                menu=menu,
            ))

        return restaurants

    def _generate_menu(self, brand: str, category: str) -> List[MenuItem]:
        """生成模拟菜单 - 京东价格通常较高但配送稳定"""
        base_prices = {
            "麦当劳": [("巨无霸", 25.0), ("薯条(大)", 14.0), ("麦辣鸡腿堡", 20.0)],
            "肯德基": [("香辣鸡腿堡", 20.0), ("原味鸡(1块)", 14.0), ("薯条(大)", 13.0)],
            "必胜客": [("超级至尊披萨(9寸)", 72.0), ("烤翅(4块)", 30.0)],
            "瑞幸咖啡": [("生椰拿铁", 23.0), ("厚乳拿铁", 20.0)],
            "真功夫": [("香菇鸡腿饭", 26.0), ("排骨饭", 29.0)],
            "吉野家": [("牛肉饭(大)", 29.0), ("照烧鸡排饭", 27.0)],
        }

        items = []
        for name, price in base_prices.get(brand, [("招牌菜", 26.0)]):
            items.append(MenuItem(
                name=name,
                price=price,
                category=category,
                monthly_sales=random.randint(50, 2000),
            ))
        return items


def fetch_all_platforms(lat: float = None, lng: float = None, limit: int = 15) -> List[Restaurant]:
    """从所有平台获取数据"""
    print("🔄 开始抓取外卖数据...")

    all_restaurants = []

    # 美团
    print("  📱 抓取美团外卖...")
    meituan = MeituanCrawler(lat, lng)
    all_restaurants.extend(meituan.fetch_restaurants(limit))
    print(f"    ✓ 获取 {limit} 家商家")

    time.sleep(0.5)

    # 饿了么
    print("  📱 抓取饿了么...")
    eleme = ElemeCrawler(lat, lng)
    all_restaurants.extend(eleme.fetch_restaurants(limit))
    print(f"    ✓ 获取 {limit} 家商家")

    time.sleep(0.5)

    # 京东到家
    print("  📱 抓取京东到家...")
    jd = JDDaojiaCrawler(lat, lng)
    all_restaurants.extend(jd.fetch_restaurants(limit))
    print(f"    ✓ 获取 {limit} 家商家")

    print(f"\n✅ 共获取 {len(all_restaurants)} 家商家数据")
    return all_restaurants
