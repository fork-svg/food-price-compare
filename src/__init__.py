# 外卖比价器
from .models import Restaurant, MenuItem, PriceComparison, save_data, load_data
from .crawlers import fetch_all_platforms, MeituanCrawler, ElemeCrawler, JDDaojiaCrawler
from .comparator import compare_items, compare_same_restaurant
from .report import generate_readme

__version__ = "1.0.0"
__all__ = [
    "Restaurant", "MenuItem", "PriceComparison",
    "save_data", "load_data",
    "fetch_all_platforms",
    "MeituanCrawler", "ElemeCrawler", "JDDaojiaCrawler",
    "compare_items", "compare_same_restaurant",
    "generate_readme",
]
