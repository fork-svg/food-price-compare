# 🍔 外卖比价器

> 真实爬取美团、饿了么、京东到家的外卖数据，跨平台比价，帮你找到最便宜的外卖！

📊 **本次更新**：等待首次真实数据爬取...

---

**📍 位置**: 北京市朝阳区
**⏰ 更新频率**: 每小时自动更新
**🔄 最后更新**: 等待首次运行

---

## 📖 简介

这个项目**只使用真实数据**，自动从三大外卖平台爬取商家和菜品价格：

- 🟡 **美团外卖** - 商家最多，配送快
- 🔵 **饿了么** - 补贴多，价格低
- 🔴 **京东到家** - 配送稳定，品质保证

通过对比**商品价格 + 配送费**的总价，帮你找到最省钱的选择！

---

## ⚠️ 重要：需要配置Cookie

由于外卖平台有严格的反爬机制，**必须配置登录后的Cookie**才能获取真实数据。

### 配置步骤

#### 1. 获取美团Cookie

1. 在浏览器中打开 https://waimai.meituan.com 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 `Console` 标签
4. 执行以下代码：
   ```javascript
   JSON.stringify(Object.fromEntries(document.cookie.split(';').map(c => {
     const [k, ...v] = c.trim().split('=');
     return [k, v.join('=')];
   })))
   ```
5. 复制输出的JSON字符串

#### 2. 保存Cookie文件

```bash
# 在项目根目录创建 config 目录
mkdir -p config

# 将复制的JSON保存到文件
echo '{"cookie_name":"cookie_value",...}' > config/meituan_cookies.json
```

#### 3. 同样配置饿了么和京东

```bash
# 饿了么: https://h5.ele.me
echo '{...}' > config/eleme_cookies.json

# 京东到家: https://daojia.jd.com
echo '{...}' > config/jd_cookies.json
```

---

## 🚀 运行

```bash
# 安装依赖
pip install requests

# 运行比价（必须已配置Cookie）
python main.py
```

程序会：
1. 使用配置的Cookie爬取三家平台的真实数据
2. 智能匹配同类商品
3. 计算总价（商品价 + 配送费）
4. 生成比价报告

---

## 📊 报告示例

运行后 README.md 会自动更新，开头会有简洁的总结：

```
📊 **本次更新**：爬取到 13 家商家，22 种商品可比价。
平均每个商品可省 ¥3.6，最便宜的平台是 **饿了么**（胜出 22 次）。
最省钱的是 **巨无霸**，选 饿了么 可省 ¥6.8。
```

然后是详细的比价表格...

---

## 🏗️ 项目结构

```
food-price-compare/
├── main.py                    # 主程序入口
├── src/
│   ├── crawlers.py           # 真实API爬虫
│   ├── comparator.py         # 比价逻辑
│   └── report.py             # 报告生成
├── config/                    # Cookie配置（需要创建）
│   ├── meituan_cookies.json  # 美团Cookie
│   ├── eleme_cookies.json    # 饿了么Cookie
│   └── jd_cookies.json       # 京东Cookie
├── data/
│   └── raw_data.json         # 爬取的真实数据
└── .github/workflows/
    └── update.yml            # 每小时自动更新
```

---

## 💡 省钱技巧

根据历史比价数据：

| 技巧 | 说明 |
|------|------|
| 🔵 **饿了么通常最便宜** | 补贴力度大，同等商品平均便宜 ¥3-5 |
| 🕐 **错峰下单** | 10:30 和 16:30 有下午茶优惠 |
| 🎫 **关注满减** | 凑单满减更划算 |
| 🚚 **计算总价** | 免配送费 ≠ 最便宜，要算总价 |

---

## ⚙️ 自定义

### 修改搜索品牌

编辑 `main.py`：

```python
restaurants = fetch_all_platforms(
    keywords=["麦当劳", "肯德基", "星巴克", "喜茶"],  # 改这里
    limit=5,
)
```

### 修改位置

```python
# 北京朝阳区（默认）
BEIJING_CHAOYANG = {"lat": 39.9210, "lng": 116.4430}

# 上海浦东
SHANGHAI_PUDONG = {"lat": 31.2209, "lng": 121.5447}

# 深圳南山
SHENZHEN_NANSHAN = {"lat": 22.5330, "lng": 113.9300}
```

---

## ⚠️ 注意事项

1. **Cookie时效**: Cookie通常7-30天过期，需要定期更新
2. **请求频率**: 每小时爬取一次，不要太频繁
3. **法律合规**: 仅用于个人比价，不要用于商业用途
4. **数据准确性**: 价格实时变化，以实际下单为准

---

<div align="center">

**只使用真实数据 · 帮你省钱吃好的** 💰

</div>
