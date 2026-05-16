"""
模拟生成夜间经济数据集
四张表：
  1. night_orders.csv        — 夜间消费热度（主表）
  2. grid_flow.csv           — 夜间活力人流（辅助）
  3. poi_features.csv        — 城市功能与可达性
  4. reviews.csv             — 评论与情感
数值字段均为浮点数（非整数）
"""

import csv
import math
import random
import hashlib
from datetime import datetime, timedelta

random.seed(42)

# ── 基础配置 ────────────────────────────────────────────────────────────────

CITIES = {
    "上海": {
        "districts": ["黄浦区", "徐汇区", "静安区", "浦东新区", "虹口区", "杨浦区", "长宁区", "闵行区"],
        "lng_range": (121.36, 121.60),
        "lat_range": (31.10, 31.40),
    }
}

CATEGORIES = {
    "餐饮": ["烧烤/烤肉", "火锅", "湘菜", "日料", "小吃快餐", "西餐", "粤菜", "酒吧/餐吧"],
    "娱乐": ["KTV", "电影院", "密室逃脱", "桌游/棋牌", "剧本杀", "游戏厅"],
    "零售": ["便利店", "夜市摊位", "甜品饮品", "超市"],
    "生活服务": ["美甲美睫", "足疗按摩", "健身房", "24h洗衣"],
}

POI_NAMES = {
    "烧烤/烤肉": ["撸串吧", "老街烤肉", "炉鱼", "一品烤肉", "炭火烤鱼"],
    "火锅":      ["海底捞", "呷哺呷哺", "小龙坎", "凑凑", "巴奴毛肚"],
    "湘菜":      ["费大厨辣椒炒肉", "辣上瘾", "农耕记", "湘西土家"],
    "日料":      ["鮨一", "花まる回转寿司", "和民居酒屋", "鸟贵族"],
    "小吃快餐":  ["麦当劳", "肯德基", "塔斯汀", "沙县小吃", "兰州拉面"],
    "西餐":      ["胡桃里", "COSTA", "牛排之家", "Ole Cafe"],
    "粤菜":      ["广州酒家", "避风塘", "太兴餐厅"],
    "酒吧/餐吧": ["Mao Livehouse", "M1NT", "The Shelter", "Arkham", "新天地酒吧街"],
    "KTV":       ["钱柜KTV", "麦乐迪", "好乐迪", "唱吧KTV"],
    "电影院":    ["万达影城", "CGV影城", "百丽宫影城", "上影影城"],
    "密室逃脱":  ["魔方密室", "异次元密室", "探案密室"],
    "桌游/棋牌": ["棋牌室", "三国杀桌游馆", "大富翁桌游"],
    "剧本杀":    ["推理剧场", "侦探事务所", "剧本杀工坊"],
    "游戏厅":    ["大玩家游乐城", "电玩城", "彩虹乐园"],
    "便利店":    ["全家FamilyMart", "罗森", "711"],
    "夜市摊位":  ["夜市大排档", "网红夜市", "文创夜市"],
    "甜品饮品":  ["喜茶", "奈雪的茶", "茶百道", "COCO都可"],
    "超市":      ["大润发", "盒马鲜生", "华联超市"],
    "美甲美睫":  ["花田美甲", "美睫工坊", "指尖艺术"],
    "足疗按摩":  ["足道养生", "正和足浴", "峰汇养生"],
    "健身房":    ["超级猩猩", "乐刻运动", "Keep健身房"],
    "24h洗衣":   ["熊猫洗衣", "小白鲸洗衣", "e袋洗"],
}

PAYMENT_TYPES = ["微信支付", "支付宝", "美团支付", "银行卡", "现金"]
USER_LEVELS   = ["普通用户", "黄金会员", "铂金会员", "钻石会员"]

START_DATE = datetime(2026, 3, 1)
END_DATE   = datetime(2026, 3, 31)

# ── 工具函数 ─────────────────────────────────────────────────────────────────

def rand_coord(lo, hi):
    return round(random.uniform(lo, hi), 6)

def rand_float(lo, hi, decimals=2):
    return round(random.uniform(lo, hi), decimals)

def rand_datetime(start, end):
    delta = end - start
    secs  = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=secs)

def night_biased_hour():
    """返回偏向夜间（18–03）的小时"""
    weights = [
        0.5, 0.3, 0.3, 0.2, 0.2, 0.3,   # 0–5
        0.1, 0.1, 0.2, 0.3, 0.4, 0.6,   # 6–11
        0.7, 0.8, 0.7, 0.6, 0.7, 0.9,   # 12–17
        1.5, 2.0, 2.5, 2.8, 2.6, 2.0,   # 18–23
    ]
    return random.choices(range(24), weights=weights, k=1)[0]

def make_order_time(base_date):
    h = night_biased_hour()
    m = random.randint(0, 59)
    return base_date.replace(hour=h, minute=m, second=random.randint(0, 59))

def uid(prefix, n, width=8):
    return f"{prefix}{str(n).zfill(width)}"

# ── 预生成 POI 库 ─────────────────────────────────────────────────────────────

def build_poi_pool(n_poi=200):
    pool = []
    for i in range(1, n_poi + 1):
        city_name  = "上海"
        cfg        = CITIES[city_name]
        district   = random.choice(cfg["districts"])
        cat1       = random.choice(list(CATEGORIES.keys()))
        cat2       = random.choice(CATEGORIES[cat1])
        base_names = POI_NAMES.get(cat2, ["商家"])
        name       = f"{random.choice(base_names)}({district}店)"
        lng        = rand_coord(*cfg["lng_range"])
        lat        = rand_coord(*cfg["lat_range"])
        pool.append({
            "poi_id":       uid("SH", i, 5),
            "poi_name":     name,
            "category_lv1": cat1,
            "category_lv2": cat2,
            "city":         city_name,
            "district":     district,
            "lng":          lng,
            "lat":          lat,
        })
    return pool

POI_POOL = build_poi_pool(200)

# ── 表1：夜间消费热度 ─────────────────────────────────────────────────────────

def generate_orders(n=5000):
    rows = []
    for i in range(1, n + 1):
        poi   = random.choice(POI_POOL)
        cat1  = poi["category_lv1"]
        # 金额区间因类别而异
        amount_range = {
            "餐饮":     (18.0,  380.0),
            "娱乐":     (30.0,  260.0),
            "零售":     (5.0,   180.0),
            "生活服务": (45.0,  320.0),
        }.get(cat1, (20.0, 200.0))

        base_day = START_DATE + timedelta(days=random.randint(0, 30))
        ot = make_order_time(base_day)

        rows.append({
            "order_id":      uid("ORD", i, 8),
            "poi_id":        poi["poi_id"],
            "poi_name":      poi["poi_name"],
            "category_lv1":  poi["category_lv1"],
            "category_lv2":  poi["category_lv2"],
            "city":          poi["city"],
            "district":      poi["district"],
            "lng":           poi["lng"],
            "lat":           poi["lat"],
            "order_time":    ot.strftime("%Y/%m/%d %H:%M"),
            "order_amount":  rand_float(*amount_range, 2),
            "payment_type":  random.choice(PAYMENT_TYPES),
            "rating":        rand_float(2.5, 5.0, 1),
        })
    return rows

# ── 表2：夜间活力人流（网格） ──────────────────────────────────────────────────

def build_grid(city="上海", cell_deg=0.005):
    """以 ~500m 网格覆盖城区，返回 (grid_id, lng_center, lat_center, district)"""
    cfg = CITIES[city]
    lng_lo, lng_hi = cfg["lng_range"]
    lat_lo, lat_hi = cfg["lat_range"]
    grids = []
    gid   = 1
    lng   = lng_lo
    while lng < lng_hi:
        lat = lat_lo
        while lat < lat_hi:
            lng_c = round(lng + cell_deg / 2, 6)
            lat_c = round(lat + cell_deg / 2, 6)
            # 最近区（简化：按经纬度分区）
            district = random.choice(CITIES[city]["districts"])
            grids.append({
                "grid_id":  f"GRID{str(gid).zfill(5)}",
                "city":     city,
                "district": district,
                "lng":      lng_c,
                "lat":      lat_c,
            })
            gid += 1
            lat += cell_deg
        lng += cell_deg
    return grids

GRID_POOL = build_grid()

def generate_grid_flow(n_records=3000):
    rows = []
    for _ in range(n_records):
        g   = random.choice(GRID_POOL)
        day = START_DATE + timedelta(days=random.randint(0, 30))
        h   = night_biased_hour()
        dt  = day.replace(hour=h, minute=random.randint(0, 59), second=0)

        # 深夜高峰在 20–23 点，人流更大
        peak_factor = 1.0 + 0.8 * math.exp(-0.5 * ((h - 21) / 3) ** 2)
        flow_in     = round(random.gauss(120, 35) * peak_factor, 2)
        flow_out    = round(flow_in * rand_float(0.70, 1.10, 4), 2)
        stay        = round(random.gauss(42.0, 12.5), 2)      # 分钟
        heat        = round(rand_float(0.01, 0.99, 4) * peak_factor, 4)

        rows.append({
            "grid_id":       g["grid_id"],
            "city":          g["city"],
            "district":      g["district"],
            "lng":           g["lng"],
            "lat":           g["lat"],
            "datetime":      dt.strftime("%Y/%m/%d %H:%M"),
            "flow_in":       max(flow_in, 0.01),
            "flow_out":      max(flow_out, 0.01),
            "stay_duration": max(stay, 1.0),
            "heat_index":    min(heat, 1.0),
        })
    return rows

# ── 表3：城市功能与可达性 ──────────────────────────────────────────────────────

def generate_poi_features():
    rows = []
    for poi in POI_POOL:
        rows.append({
            "poi_id":         poi["poi_id"],
            "category_lv1":   poi["category_lv1"],
            "category_lv2":   poi["category_lv2"],
            "lng":            poi["lng"],
            "lat":            poi["lat"],
            "density_1km":    rand_float(2.5,  85.0, 2),   # POI/km²
            "transit_access": rand_float(0.10,  1.00, 4),  # 归一化可达性
            "road_density":   rand_float(3.2,  22.8, 2),   # km/km²
        })
    return rows

# ── 表4：评论与情感 ────────────────────────────────────────────────────────────

REVIEW_TEMPLATES_POS = [
    "环境很好，菜品新鲜，夜晚来这里消费感觉很值，下次还会来！",
    "服务很到位，夜宵时段人不多，安静舒适，强烈推荐！",
    "性价比超高，口味地道，夜间营业到凌晨很方便，赞！",
    "夜晚灯光氛围好，食物味道不错，适合朋友聚会。",
    "24小时营业真的太贴心了，深夜饥饿首选！",
]
REVIEW_TEMPLATES_NEG = [
    "排队等了将近一小时，服务员态度一般，有些失望。",
    "夜间噪音比较大，影响用餐体验，停车也不方便。",
    "菜品分量偏少，价格偏贵，性价比不高，不太值得推荐。",
    "安全感略差，周边环境一般，希望能改善。",
    "等位时间太长，菜上的慢，夜间服务质量有待提高。",
]
REVIEW_TEMPLATES_NEU = [
    "整体感觉还行，不算惊艳，适合路过时顺便吃一下。",
    "味道中规中矩，价格合理，夜间选择不多时可以考虑。",
    "环境一般，但食物不错，综合体验尚可。",
]

def generate_reviews(n=2000):
    rows = []
    for i in range(1, n + 1):
        poi      = random.choice(POI_POOL)
        day      = START_DATE + timedelta(days=random.randint(0, 30))
        rt       = make_order_time(day)

        # 情感倾向
        r = random.random()
        if r < 0.60:
            sentiment_label = "正面"
            sentiment_score = rand_float(0.55, 1.00, 4)
            text = random.choice(REVIEW_TEMPLATES_POS)
            rating = rand_float(3.8, 5.0, 1)
        elif r < 0.85:
            sentiment_label = "中性"
            sentiment_score = rand_float(0.35, 0.65, 4)
            text = random.choice(REVIEW_TEMPLATES_NEU)
            rating = rand_float(2.8, 4.2, 1)
        else:
            sentiment_label = "负面"
            sentiment_score = rand_float(0.00, 0.40, 4)
            text = random.choice(REVIEW_TEMPLATES_NEG)
            rating = rand_float(1.0, 3.2, 1)

        rows.append({
            "review_id":       uid("REV", i, 8),
            "poi_id":          poi["poi_id"],
            "poi_name":        poi["poi_name"],
            "city":            poi["city"],
            "district":        poi["district"],
            "category_lv1":    poi["category_lv1"],
            "category_lv2":    poi["category_lv2"],
            "review_time":     rt.strftime("%Y/%m/%d %H:%M"),
            "rating":          rating,
            "review_text":     text,
            "like_count":      rand_float(0.0, 128.0, 1),
            "user_level":      random.choice(USER_LEVELS),
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
        })
    return rows

# ── 写 CSV ────────────────────────────────────────────────────────────────────

def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  写出 {len(rows):,} 行 → {path}")

if __name__ == "__main__":
    import os
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
    os.makedirs(out_dir, exist_ok=True)

    print("生成夜间消费热度表 (5000 条)…")
    write_csv(os.path.join(out_dir, "night_orders.csv"), generate_orders(5000))

    print("生成夜间活力人流表 (3000 条)…")
    write_csv(os.path.join(out_dir, "grid_flow.csv"), generate_grid_flow(3000))

    print("生成城市功能与可达性表 (200 条)…")
    write_csv(os.path.join(out_dir, "poi_features.csv"), generate_poi_features())

    print("生成评论与情感表 (2000 条)…")
    write_csv(os.path.join(out_dir, "reviews.csv"), generate_reviews(2000))

    print("\n全部完成！")
