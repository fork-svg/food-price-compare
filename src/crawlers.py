"""
外卖平台爬虫模块 - 真实API调用
支持美团、饿了么、京东到家

需要配置各平台的Cookie才能正常爬取
"""
import json
import random
import re
import os
from typing import List, Dict, Optional
from datetime import datetime

import requests

from .models import Restaurant, MenuItem

# 北京朝阳区坐标
BEIJING_CHAOYANG = {
    "lat": 39.9210,
    "lng": 116.4430,
    "name": "北京市朝阳区",
    "address": "北京市朝阳区三里屯"
}

# 配置目录
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")


def load_cookies(platform: str) -> Dict[str, str]:
    """加载平台Cookie配置"""
    config_file = os.path.join(CONFIG_DIR, f"{platform}_cookies.json")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}


class MeituanCrawler:
    """
    美团外卖爬虫 - 真实API

    需要配置Cookie:
    1. 在浏览器中登录 https://waimai.meituan.com
    2. 按F12打开开发者工具
    3. 在Console中执行: document.cookie
    4. 将结果保存到 config/meituan_cookies.json
       格式: {"cookie_name": "cookie_value", ...}
    """

    API_BASE = "https://waimai.meituan.com"
    SEARCH_API = "https://waimai.meituan.com/ajax/search/food"
    POI_API = "https://waimai.meituan.com/ajax/poi"

    def __init__(self, lat: float = None, lng: float = None):
        self.lat = lat or BEIJING_CHAOYANG["lat"]
        self.lng = lng or BEIJING_CHAOYANG["lng"]
        self.session = requests.Session()
        self.cookies = load_cookies("meituan")

        # 设置基础请求头
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://waimai.meituan.com/",
            "Origin": "https://waimai.meituan.com",
        })

        # 设置Cookie
        if self.cookies:
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value)

    def fetch_restaurants(self, keywords: List[str] = None, limit: int = 5) -> List[Restaurant]:
        """获取商家列表"""
        restaurants = []
        keywords = keywords or ["麦当劳", "肯德基", "瑞幸咖啡"]

        for keyword in keywords[:limit]:
            print(f"    🔍 搜索: {keyword}")
            try:
                found = self._search_brand(keyword)
                restaurants.extend(found)
                print(f"       ✓ 找到 {len(found)} 家")
            except Exception as e:
                print(f"       ✗ 失败: {e}")

        return restaurants

    def _search_brand(self, keyword: str) -> List[Restaurant]:
        """搜索品牌"""
        params = {
            "lat": self.lat,
            "lng": self.lng,
            "keyword": keyword,
            "page": 1,
            "pageSize": 10,
        }

        try:
            resp = self.session.get(self.SEARCH_API, params=params, timeout=10)

            if resp.status_code == 403:
                raise Exception("需要配置Cookie才能爬取，请查看 README.md")

            resp.raise_for_status()
            data = resp.json()

            restaurants = []
            pois = data.get("data", {}).get("pois", []) or data.get("pois", [])

            for poi in pois:
                name = poi.get("name", "")
                if keyword.lower() not in name.lower():
                    continue

                # 获取菜单
                menu = self._fetch_menu(poi.get("id", ""))

                restaurants.append(Restaurant(
                    name=name,
                    platform="meituan",
                    location=BEIJING_CHAOYANG["name"],
                    distance=float(poi.get("distance", "0").replace("m", "")) / 1000,
                    delivery_fee=float(poi.get("shippingFee", 0)),
                    delivery_time=int(poi.get("deliveryTime", 30)),
                    rating=float(poi.get("rating", 4.5)),
                    min_order=float(poi.get("minPrice", 20)),
                    menu=menu,
                ))

            return restaurants

        except requests.exceptions.JSONDecodeError:
            raise Exception("API返回非JSON数据，可能被反爬")
        except Exception as e:
            raise Exception(f"请求失败: {e}")

    def _fetch_menu(self, poi_id: str) -> List[MenuItem]:
        """获取商家菜单"""
        if not poi_id:
            return []

        menu = []
        url = f"{self.POI_API}/{poi_id}/menu"

        try:
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                foods = data.get("data", {}).get("food_spu_list", []) or data.get("foods", [])

                for food in foods[:10]:
                    menu.append(MenuItem(
                        name=food.get("name", ""),
                        price=float(food.get("price", 0)),
                        original_price=float(food.get("originPrice", 0)) if food.get("originPrice") else None,
                        monthly_sales=food.get("monthSales", 0),
                    ))
        except:
            pass

        return menu


class ElemeCrawler:
    """
    饿了么爬虫 - 真实API

    需要配置Cookie:
    1. 在浏览器中登录 https://h5.ele.me
    2. 按F12打开开发者工具
    3. 在Console中执行: document.cookie
    4. 将结果保存到 config/eleme_cookies.json
    """

    API_BASE = "https://h5.ele.me"
    RESTAURANT_API = "https://h5.ele.me/restapi/v2/restaurants"

    def __init__(self, lat: float = None, lng: float = None):
        self.lat = lat or BEIJING_CHAOYANG["lat"]
        self.lng = lng or BEIJING_CHAOYANG["lng"]
        self.session = requests.Session()
        self.cookies = load_cookies("eleme")

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://h5.ele.me/",
        })

        if self.cookies:
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value)

    def fetch_restaurants(self, keywords: List[str] = None, limit: int = 5) -> List[Restaurant]:
        """获取商家列表"""
        restaurants = []
        keywords = keywords or ["麦当劳", "肯德基", "瑞幸咖啡"]

        for keyword in keywords[:limit]:
            print(f"    🔍 搜索: {keyword}")
            try:
                found = self._search_brand(keyword)
                restaurants.extend(found)
                print(f"       ✓ 找到 {len(found)} 家")
            except Exception as e:
                print(f"       ✗ 失败: {e}")

        return restaurants

    def _search_brand(self, keyword: str) -> List[Restaurant]:
        """搜索品牌"""
        params = {
            "latitude": self.lat,
            "longitude": self.lng,
            "offset": 0,
            "limit": 20,
        }

        try:
            resp = self.session.get(self.RESTAURANT_API, params=params, timeout=10)

            if resp.status_code == 410:
                raise Exception("API已废弃或需要签名，请配置Cookie")

            resp.raise_for_status()
            data = resp.json()

            restaurants = []
            items = data if isinstance(data, list) else data.get("data", [])

            for item in items:
                name = item.get("name", "")
                if keyword.lower() not in name.lower():
                    continue

                # 提取菜单
                menu = []
                for food in item.get("foods", [])[:5]:
                    menu.append(MenuItem(
                        name=food.get("name", ""),
                        price=float(food.get("price", 0)),
                    ))

                restaurants.append(Restaurant(
                    name=name,
                    platform="eleme",
                    location=BEIJING_CHAOYANG["name"],
                    distance=float(item.get("distance", 1000)) / 1000,
                    delivery_fee=float(item.get("delivery_fee", 0)),
                    delivery_time=int(item.get("order_lead_time", 30)),
                    rating=float(item.get("rating", 4.5)),
                    min_order=float(item.get("float_minimum_order_amount", 20)),
                    menu=menu,
                ))

            return restaurants

        except Exception as e:
            raise Exception(f"请求失败: {e}")


class JDDaojiaCrawler:
    """
    京东到家爬虫 - 真实API

    需要配置Cookie:
    1. 在浏览器中登录 https://daojia.jd.com
    2. 按F12打开开发者工具
    3. 在Console中执行: document.cookie
    4. 将结果保存到 config/jd_cookies.json
    """

    API_BASE = "https://daojia.jd.com"

    def __init__(self, lat: float = None, lng: float = None):
        self.lat = lat or BEIJING_CHAOYANG["lat"]
        self.lng = lng or BEIJING_CHAOYANG["lng"]
        self.session = requests.Session()
        self.cookies = load_cookies("jd")

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://daojia.jd.com/",
        })

        if self.cookies:
            for name, value in self.cookies.items():
                self.session.cookies.set(name, value)

    def fetch_restaurants(self, keywords: List[str] = None, limit: int = 5) -> List[Restaurant]:
        """获取商家列表"""
        restaurants = []
        keywords = keywords or ["麦当劳", "肯德基", "瑞幸咖啡"]

        for keyword in keywords[:limit]:
            print(f"    🔍 搜索: {keyword}")
            try:
                found = self._search_brand(keyword)
                restaurants.extend(found)
                print(f"       ✓ 找到 {len(found)} 家")
            except Exception as e:
                print(f"       ✗ 失败: {e}")

        return restaurants

    def _search_brand(self, keyword: str) -> List[Restaurant]:
        """搜索品牌"""
        url = f"{self.API_BASE}/html/searchResult"
        params = {
            "keyword": keyword,
            "lat": self.lat,
            "lng": self.lng,
        }

        try:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()

            # 尝试解析JSON
            try:
                data = resp.json()
            except:
                raise Exception("返回非JSON数据，请配置Cookie")

            restaurants = []
            shops = data.get("data", {}).get("shops", []) or data.get("shops", [])

            for shop in shops:
                name = shop.get("shopName", "")
                menu = []
                for food in shop.get("goodsList", [])[:5]:
                    menu.append(MenuItem(
                        name=food.get("skuName", ""),
                        price=float(food.get("jdPrice", 0)),
                    ))

                restaurants.append(Restaurant(
                    name=name,
                    platform="jd",
                    location=BEIJING_CHAOYANG["name"],
                    distance=float(shop.get("distance", 2000)) / 1000,
                    delivery_fee=float(shop.get("deliveryFee", 5)),
                    delivery_time=int(shop.get("deliveryTime", 45)),
                    rating=float(shop.get("score", 4.5)),
                    min_order=float(shop.get("minPrice", 25)),
                    menu=menu,
                ))

            return restaurants

        except Exception as e:
            raise Exception(f"请求失败: {e}")


def fetch_all_platforms(
    lat: float = None,
    lng: float = None,
    keywords: List[str] = None,
    limit: int = 3
) -> List[Restaurant]:
    """从所有平台获取数据"""
    print("🔄 开始爬取外卖数据...")
    print(f"📍 位置: {BEIJING_CHAOYANG['name']}")
    print(f"🔍 搜索品牌: {keywords or ['麦当劳', '肯德基', '瑞幸咖啡']}")
    print()

    lat = lat or BEIJING_CHAOYANG["lat"]
    lng = lng or BEIJING_CHAOYANG["lng"]
    keywords = keywords or ["麦当劳", "肯德基", "瑞幸咖啡", "喜茶", "星巴克"]

    all_restaurants = []
    failed_platforms = []

    # 美团
    print("  📱 爬取美团外卖...")
    try:
        meituan = MeituanCrawler(lat, lng)
        results = meituan.fetch_restaurants(keywords, limit)
        all_restaurants.extend(results)
        print(f"    ✓ 共获取 {len(results)} 家商家")
    except Exception as e:
        print(f"    ✗ 美团爬取失败: {e}")
        failed_platforms.append("美团")

    # 饿了么
    print("  📱 爬取饿了么...")
    try:
        eleme = ElemeCrawler(lat, lng)
        results = eleme.fetch_restaurants(keywords, limit)
        all_restaurants.extend(results)
        print(f"    ✓ 共获取 {len(results)} 家商家")
    except Exception as e:
        print(f"    ✗ 饿了么爬取失败: {e}")
        failed_platforms.append("饿了么")

    # 京东到家
    print("  📱 爬取京东到家...")
    try:
        jd = JDDaojiaCrawler(lat, lng)
        results = jd.fetch_restaurants(keywords, limit)
        all_restaurants.extend(results)
        print(f"    ✓ 共获取 {len(results)} 家商家")
    except Exception as e:
        print(f"    ✗ 京东到家爬取失败: {e}")
        failed_platforms.append("京东到家")

    print(f"\n✅ 共爬取 {len(all_restaurants)} 家商家数据")

    if failed_platforms:
        print(f"\n⚠️ 以下平台爬取失败: {', '.join(failed_platforms)}")
        print("💡 请在 config/ 目录配置对应的Cookie文件，详见 README.md")

    return all_restaurants
