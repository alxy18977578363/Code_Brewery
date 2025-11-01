from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import matplotlib.pyplot as plt
import pandas as pd
import re
import numpy as np
import time
import random

# 设置中文字体解决显示问题
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# 设置浏览器
options = Options()
# options.add_argument('--headless')  # 无头模式可选
driver = webdriver.Chrome(options=options)

def get_weather():
    regions = ['hb', 'db', 'hd', 'hz', 'hn', 'xb', 'xn', 'gat']
    base_url = "http://www.weather.com.cn/textFC/{}.shtml"
    
    all_data = []
    
    for region in regions:
        url = base_url.format(region)
        driver.get(url)
        
        # 尝试点击切换到第二天（示例：点击第二个标签，即11月2日）
        try:
            day_tabs = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.day_tabs li"))
            )
            if len(day_tabs) > 1:
                # 点击第二个标签（11月2日）
                day_tabs[1].click()
                time.sleep(2)  # 等待数据刷新
        except Exception as e:
            print(f"点击切换日期失败: {e}")
        
        # 解析当前页面数据
        soup = BeautifulSoup(driver.page_source, "lxml")
        region_data = parse_data(soup, region)
        all_data.extend(region_data)
        
    return all_data



def parse_data(soup, region_name):
    weather_list = []
    
    # 查找所有的conMidtab div，每个代表一天的天气预报
    con_midtabs = soup.find_all("div", class_="conMidtab")
    
    for day_index, con_midtab in enumerate(con_midtabs):
        # 跳过隐藏的表格（display:none）
        if con_midtab.has_attr('style') and 'display:none' in con_midtab['style']:
            continue
            
        # 在每个conMidtab中查找所有的conMidtab2
        con_midtab2s = con_midtab.find_all("div", class_="conMidtab2")
        
        for con_midtab2 in con_midtab2s:
            # 在conMidtab2中查找table
            table = con_midtab2.find("table")
            if not table:
                continue
                
            # 获取所有行，跳过表头行（前2行）
            trs = table.find_all("tr")[2:]
            
            current_province = ""
            
            for tr in trs:
                tds = tr.find_all("td")
                
                # 确保有足够的列数
                if len(tds) < 8:
                    continue
                
                # 检查第一列是否是省份（有rowsPan类）
                if 'rowsPan' in tds[0].get('class', []):
                    current_province = tds[0].text.strip()
                    # 如果是省份行，城市在第二列
                    city_td = tds[1]
                    data_start_index = 2  # 数据从第3列开始
                else:
                    # 普通城市行，城市在第一列
                    city_td = tds[0]
                    data_start_index = 1  # 数据从第2列开始
                
                # 解析城市
                city_link = city_td.find("a")
                city = city_link.text.strip() if city_link else city_td.text.strip()
                
                # 解析天气数据
                # 白天天气现象
                day_weather = tds[data_start_index].text.strip() if data_start_index < len(tds) else ""
                # 白天风向风力
                day_wind = parse_wind_direction(tds[data_start_index + 1]) if data_start_index + 1 < len(tds) else ""
                # 白天气温
                day_temp = tds[data_start_index + 2].text.strip() if data_start_index + 2 < len(tds) else ""
                # 夜间天气现象
                night_weather = tds[data_start_index + 3].text.strip() if data_start_index + 3 < len(tds) else ""
                # 夜间风向风力
                night_wind = parse_wind_direction(tds[data_start_index + 4]) if data_start_index + 4 < len(tds) else ""
                # 夜间气温
                night_temp = tds[data_start_index + 5].text.strip() if data_start_index + 5 < len(tds) else ""
                
                # 获取日期信息
                date_info = get_date_info(soup, day_index)
                
                # 处理空数据
                if day_weather == "-":
                    day_weather = ""
                if day_temp == "-":
                    day_temp = ""
                
                weather_list.append({
                    "省份": current_province,
                    "城市": city,
                    "日期": date_info,
                    "白天天气": day_weather,
                    "白天风力": day_wind,
                    "白天气温": day_temp,
                    "夜间天气": night_weather,
                    "夜间风力": night_wind,
                    "夜间气温": night_temp,
                    "地区": region_name
                })
    
    return weather_list

def parse_wind_direction(wind_td):
    """解析风向风力数据"""
    wind_spans = wind_td.find_all("span")
    if len(wind_spans) >= 2:
        direction = wind_spans[0].text.strip()
        strength = wind_spans[1].text.strip()
        return f"{direction}{strength}"
    else:
        return wind_td.text.strip()

def get_date_info(soup, day_index):
    """从页面中获取日期信息"""
    try:
        # 查找日期标签
        day_tabs = soup.find("ul", class_="day_tabs")
        if day_tabs:
            day_items = day_tabs.find_all("li")
            if day_index < len(day_items):
                return day_items[day_index].text.strip()
    except:
        pass
    
    # 如果无法获取具体日期，返回索引
    return f"第{day_index + 1}天"

def save_to_csv(data):
    if not data:
        print("没有数据可保存")
        return
        
    columns = [
        "省份", "城市", "日期", "地区",
        "白天天气", "白天风力", "白天气温",
        "夜间天气", "夜间风力", "夜间气温"
    ]
    
    df = pd.DataFrame(data)
    
    # 确保所有列都存在
    for col in columns:
        if col not in df.columns:
            df[col] = ""
    
    df = df[columns]
    df.to_csv("weather_data.csv", index=False, encoding="utf_8_sig")
    print(f"数据已保存到weather_data.csv，共{len(data)}条记录")

def test_gat_only():
    """单独测试港澳台地区"""
    url = "http://www.weather.com.cn/textFC/gat.shtml"
    try:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "lxml")
        
        print("测试港澳台地区数据提取...")
        gat_data = parse_data(soup, "gat")
        
        # 显示前几条数据
        print("\n港澳台地区天气预报:")
        for i, item in enumerate(gat_data[:15]):
            day_temp_display = item['白天气温'] if item['白天气温'] else "暂无"
            night_temp_display = item['夜间气温'] if item['夜间气温'] else "暂无"
            print(f"{i+1}. {item['省份']}-{item['城市']}: 白天{item['白天天气']} {day_temp_display}°C, 夜间{item['夜间天气']} {night_temp_display}°C")
        
        return gat_data
    except Exception as e:
        print(f"测试港澳台地区时出错: {e}")
        return []

if __name__ == "__main__":
    # 先测试港澳台地区
    test_data = test_gat_only()
    
    if test_data:
        # 如果测试成功，爬取所有地区
        print("\n开始爬取所有地区数据...")
        weather_data = get_weather()
        save_to_csv(weather_data)
        
        # 显示统计信息
        print(f"\n数据统计:")
        print(f"总记录数: {len(weather_data)}")
        regions_count = pd.DataFrame(weather_data)['地区'].value_counts()
        print("各地区数据量:")
        for region, count in regions_count.items():
            print(f"  {region}: {count}条")
    else:
        print("测试失败，请检查网络连接或网站结构是否变化")