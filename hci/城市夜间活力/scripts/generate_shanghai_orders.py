"""
生成上海夜间消费热度合成数据集
输出：data/synthetic/shanghai_night_orders.csv
字段：order_id, poi_id, poi_name, category_lv1, category_lv2,
      city, district, lng, lat, order_time, order_amount,
      payment_type, rating
"""

import csv
import math
import os
import random
from datetime import datetime, timedelta

# ── 基础配置 ──────────────────────────────────────────────
RNG = random.Random(7)          # 固定种子，可复现
N_DAYS = 30                     # 生成 30 天（4月1日–30日）
START_DATE = datetime(2026, 4, 1)
NIGHT_HOURS = list(range(18, 24)) + list(range(0, 3))  # 18–02 时
OUTPUT_PATH = "data/synthetic/shanghai_night_orders.csv"

# ── 上海区县 + 大致经纬度中心点 ────────────────────────────
DISTRICTS = {
    "黄浦区": (121.4865, 31.2305),
    "徐汇区": (121.4360, 31.1883),
    "长宁区": (121.4245, 31.2204),
    "静安区": (121.4480, 31.2282),
    "普陀区": (121.3955, 31.2493),
    "虹口区": (121.5050, 31.2644),
    "杨浦区": (121.5255, 31.2591),
    "浦东新区": (121.5445, 31.2216),
    "闵行区": (121.3812, 31.1126),
    "宝山区": (121.4892, 31.3988),
}

# ── POI 库（仿大众点评风格，上海真实存在的连锁/知名品牌） ──
# 每条：(poi_name_模板, category_lv1, category_lv2, 人均消费基准, 评分均值, 评分波动)
POI_TEMPLATES = [
    # 餐饮 - 火锅
    ("海底捞火锅({district}店)", "餐饮", "火锅", 130, 4.6, 0.2),
    ("巴奴毛肚火锅({district}店)", "餐饮", "火锅", 110, 4.5, 0.2),
    ("呷哺呷哺({district}店)", "餐饮", "火锅", 65, 4.2, 0.3),
    ("小龙坎老火锅({district}店)", "餐饮", "火锅", 95, 4.3, 0.25),
    # 餐饮 - 烧烤/串串
    ("费大厨辣椒炒肉({district}店)", "餐饮", "湘菜", 85, 4.4, 0.2),
    ("探鱼({district}店)", "餐饮", "烤鱼", 75, 4.3, 0.25),
    ("木屋烧烤({district}店)", "餐饮", "烧烤", 90, 4.1, 0.3),
    ("撸串不({district}店)", "餐饮", "烧烤", 60, 4.0, 0.35),
    # 餐饮 - 日料/韩料
    ("鱼の屋({district}店)", "餐饮", "日料", 150, 4.5, 0.2),
    ("将太无二({district}店)", "餐饮", "日料", 200, 4.6, 0.15),
    ("八色烤肉({district}店)", "餐饮", "韩料", 120, 4.4, 0.2),
    # 餐饮 - 小吃/夜宵
    ("好伦哥欢乐餐厅({district}店)", "餐饮", "自助餐", 80, 3.9, 0.4),
    ("沪上阿姨({district}店)", "餐饮", "奶茶/饮品", 20, 4.2, 0.3),
    ("蜜雪冰城({district}店)", "餐饮", "奶茶/饮品", 15, 4.0, 0.35),
    ("古茗({district}店)", "餐饮", "奶茶/饮品", 18, 4.1, 0.3),
    ("喜茶({district}店)", "餐饮", "奶茶/饮品", 32, 4.5, 0.2),
    ("文和友海鲜市场({district}店)", "餐饮", "海鲜/夜宵", 110, 4.4, 0.25),
    ("老盐城小海鲜", "餐饮", "海鲜/夜宵", 95, 4.2, 0.3),
    # 休闲娱乐 - KTV
    ("钱柜KTV({district}店)", "娱乐", "KTV", 120, 4.1, 0.3),
    ("麦乐迪({district}店)", "娱乐", "KTV", 80, 4.0, 0.35),
    ("好乐迪({district}店)", "娱乐", "KTV", 90, 4.0, 0.35),
    # 休闲娱乐 - 酒吧/夜店
    ("Bar Rouge上海", "娱乐", "酒吧", 250, 4.3, 0.3),
    ("Arkham地下俱乐部", "娱乐", "夜店", 180, 4.2, 0.35),
    ("The Nest({district})", "娱乐", "酒吧", 150, 4.1, 0.3),
    ("Dada Bar({district})", "娱乐", "酒吧", 120, 4.0, 0.4),
    # 休闲娱乐 - 桌游/剧本杀
    ("谋杀之谜剧本杀({district}店)", "娱乐", "剧本杀", 150, 4.4, 0.2),
    ("推理部落({district}店)", "娱乐", "剧本杀", 130, 4.3, 0.25),
    ("王者荣耀网咖({district}店)", "娱乐", "网咖", 20, 3.9, 0.4),
    # 休闲娱乐 - 电影
    ("CGV影城({district}店)", "娱乐", "电影", 65, 4.2, 0.25),
    ("万达影城({district}店)", "娱乐", "电影", 55, 4.1, 0.3),
    ("百老汇影城({district}店)", "娱乐", "电影", 70, 4.3, 0.2),
    # 便利/零售 - 夜间消费
    ("全家FamilyMart({district}店)", "零售", "便利店", 18, 4.0, 0.3),
    ("罗森LAWSON({district}店)", "零售", "便利店", 20, 4.1, 0.25),
    ("7-Eleven({district}店)", "零售", "便利店", 16, 3.9, 0.35),
]

PAYMENT_TYPES = ["微信支付", "支付宝", "银行卡", "现金", "美团支付", "抖音支付"]
PAYMENT_WEIGHTS = [35, 30, 10, 5, 15, 5]   # 概率权重（%）


# ── 工具函数 ───────────────────────────────────────────────
def jitter(base: float, scale: float) -> float:
    """在 base 附近加高斯扰动"""
    return base + RNG.gauss(0, scale)


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def hour_demand_factor(hour: int) -> float:
    """夜间各时段需求系数，22–23时最高，0时后衰减"""
    curve = {
        18: 0.55, 19: 0.72, 20: 0.88, 21: 0.97,
        22: 1.00, 23: 0.95, 0: 0.75, 1: 0.52, 2: 0.30,
    }
    base = curve.get(hour, 0.5)
    return clamp(jitter(base, 0.04), 0.1, 1.3)


def weekend_factor(weekday: int) -> float:
    """周五/六/日消费更旺"""
    if weekday in (4, 5, 6):   # 周五=4, 周六=5, 周日=6
        return clamp(jitter(1.22, 0.05), 1.0, 1.5)
    return clamp(jitter(1.00, 0.04), 0.85, 1.15)


def district_heat(district: str) -> float:
    """各区热度基数（黄浦/静安/浦东核心区更高）"""
    heats = {
        "黄浦区": 1.35, "静安区": 1.28, "浦东新区": 1.20,
        "徐汇区": 1.15, "长宁区": 1.05, "虹口区": 1.00,
        "杨浦区": 0.95, "普陀区": 0.90, "闵行区": 0.85, "宝山区": 0.78,
    }
    base = heats.get(district, 1.0)
    return clamp(jitter(base, 0.06), 0.6, 1.6)


def category_hour_factor(cat: str, hour: int) -> float:
    """不同品类在不同时段的活跃度"""
    if cat == "餐饮":
        peaks = {20: 1.15, 21: 1.20, 22: 1.10, 23: 0.90, 0: 0.65, 1: 0.40}
    elif cat == "娱乐":
        peaks = {20: 0.90, 21: 1.05, 22: 1.20, 23: 1.25, 0: 1.10, 1: 0.80, 2: 0.55}
    else:  # 零售
        peaks = {18: 1.10, 19: 1.05, 20: 0.95, 21: 0.85, 22: 0.80, 23: 0.65}
    base = peaks.get(hour, 0.75)
    return clamp(jitter(base, 0.06), 0.2, 1.5)


def random_coord(center_lng: float, center_lat: float) -> tuple:
    """在中心点附近 ±0.025° 范围随机散点（约 2.5km）"""
    lng = center_lng + RNG.uniform(-0.025, 0.025)
    lat = center_lat + RNG.uniform(-0.018, 0.018)
    return round(lng, 6), round(lat, 6)


def build_order_amount(base_price: float, h_factor: float,
                       d_factor: float, c_factor: float) -> float:
    """
    订单金额 = 人均消费基准 × 各种乘数 + 高斯扰动
    加入长尾分布：小概率出现大额订单（多人聚餐）
    """
    amount = base_price * h_factor * d_factor * c_factor
    # 高斯扰动（±15% 标准差）
    amount = jitter(amount, amount * 0.15)
    # 小概率大额聚餐（5%）
    if RNG.random() < 0.05:
        amount *= RNG.uniform(2.5, 5.0)
    # 小概率只点一杯饮料/外带（3%，餐饮品类）
    if RNG.random() < 0.03:
        amount = RNG.uniform(8, 25)
    return clamp(round(amount, 2), 5.0, 3000.0)


def build_rating(base: float, std: float) -> float:
    r = jitter(base, std)
    return round(clamp(r, 1.0, 5.0), 1)


def weighted_choice(options, weights):
    total = sum(weights)
    r = RNG.random() * total
    acc = 0
    for opt, w in zip(options, weights):
        acc += w
        if r <= acc:
            return opt
    return options[-1]


# ── 构建 POI 池 ────────────────────────────────────────────
def build_poi_pool() -> list:
    """为每个区生成 POI 实例，返回 POI 信息列表"""
    pool = []
    poi_counter = 1
    for district, (center_lng, center_lat) in DISTRICTS.items():
        for tmpl in POI_TEMPLATES:
            name_tmpl, cat1, cat2, base_price, rating_base, rating_std = tmpl
            poi_name = name_tmpl.replace("{district}", district)
            lng, lat = random_coord(center_lng, center_lat)
            pool.append({
                "poi_id": f"SH{poi_counter:05d}",
                "poi_name": poi_name,
                "category_lv1": cat1,
                "category_lv2": cat2,
                "district": district,
                "lng": lng,
                "lat": lat,
                "base_price": base_price,
                "rating_base": rating_base,
                "rating_std": rating_std,
                "d_factor": district_heat(district),
            })
            poi_counter += 1
    return pool


# ── 主生成逻辑 ────────────────────────────────────────────
def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    poi_pool = build_poi_pool()
    print(f"POI 数量：{len(poi_pool)} 个（{len(DISTRICTS)} 区 × {len(POI_TEMPLATES)} 模板）")

    fieldnames = [
        "order_id", "poi_id", "poi_name",
        "category_lv1", "category_lv2",
        "city", "district", "lng", "lat",
        "order_time", "order_amount",
        "payment_type", "rating",
    ]

    order_counter = 1
    rows = []

    for day_offset in range(N_DAYS):
        current_date = START_DATE + timedelta(days=day_offset)
        weekday = current_date.weekday()   # 0=周一 … 6=周日
        w_factor = weekend_factor(weekday)

        for hour in NIGHT_HOURS:
            h_factor = hour_demand_factor(hour)

            # 每小时每个 POI 生成 0–4 条订单（泊松分布模拟）
            for poi in poi_pool:
                cat = poi["category_lv1"]
                c_factor = category_hour_factor(cat, hour)

                # 期望订单数：由热度系数决定，夜宵/娱乐高峰期更多
                lam = 1.8 * h_factor * poi["d_factor"] * c_factor * w_factor
                n_orders = min(RNG.poisson(lam) if hasattr(RNG, "poisson") else _poisson(lam), 8)

                for _ in range(n_orders):
                    # 随机分钟/秒
                    minute = RNG.randint(0, 59)
                    second = RNG.randint(0, 59)
                    if hour < 18:   # 跨零点情况，日期加1
                        order_dt = current_date + timedelta(days=1, hours=hour,
                                                             minutes=minute, seconds=second)
                    else:
                        order_dt = current_date + timedelta(hours=hour,
                                                             minutes=minute, seconds=second)

                    amount = build_order_amount(
                        poi["base_price"], h_factor, poi["d_factor"], c_factor
                    )
                    rating = build_rating(poi["rating_base"], poi["rating_std"])
                    payment = weighted_choice(PAYMENT_TYPES, PAYMENT_WEIGHTS)

                    rows.append({
                        "order_id": f"ORD{order_counter:08d}",
                        "poi_id": poi["poi_id"],
                        "poi_name": poi["poi_name"],
                        "category_lv1": poi["category_lv1"],
                        "category_lv2": poi["category_lv2"],
                        "city": "上海",
                        "district": poi["district"],
                        "lng": poi["lng"],
                        "lat": poi["lat"],
                        "order_time": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "order_amount": amount,
                        "payment_type": payment,
                        "rating": rating,
                    })
                    order_counter += 1

    # 写出
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"生成完成：{len(rows):,} 条订单 → {OUTPUT_PATH}")

    # 简单统计
    amounts = [r["order_amount"] for r in rows]
    print(f"  订单金额：均值 {sum(amounts)/len(amounts):.1f} 元，"
          f"最小 {min(amounts):.1f}，最大 {max(amounts):.1f}")
    cats = {}
    for r in rows:
        cats[r["category_lv1"]] = cats.get(r["category_lv1"], 0) + 1
    for k, v in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {k}：{v:,} 条（{v/len(rows)*100:.1f}%）")


def _poisson(lam: float) -> int:
    """手写泊松采样（不依赖 numpy）"""
    if lam <= 0:
        return 0
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= RNG.random()
    return k - 1


if __name__ == "__main__":
    main()