from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import json
import csv
import os
from datetime import datetime

def dynamic_browser_crawl():
    try:
        driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
        
        print(f"Driver路径: {driver_path}")
        
        # 配置浏览器选项
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 先注释掉，方便调试
        options.add_argument('--disable-gpu')
        
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        url = "http://www.weather.com.cn/weather1d/101020100.shtml"
        print(f"正在访问: {url}")
        driver.get(url)

        # 等待动态内容加载
        time.sleep(5)

        # 获取页面源码
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        
        # 分析动态加载数据的来源
        analyze_dynamic_sources(driver, soup)
        
        driver.quit()
        return soup
        
    except Exception as e:
        print(f"浏览器启动错误: {e}")
        return None

def analyze_dynamic_sources(driver, soup):
    """分析动态加载数据的来源"""
    print("\n" + "="*50)
    print("动态加载数据分析报告")
    print("="*50)
    
    # 1. 分析AJAX请求的数据源
    print("\n1. AJAX请求数据源分析:")
    analyze_ajax_sources(soup)
    
    # 2. 查找通过JavaScript动态插入的元素
    print("\n2. JavaScript动态插入元素分析:")
    analyze_js_inserted_elements(soup)
    
    # 3. 识别定时刷新的数据区域
    print("\n3. 定时刷新数据区域分析:")
    analyze_timer_refresh_elements(soup)
    
    # 4. 分析数据存储位置
    print("\n4. 数据存储位置分析:")
    analyze_data_storage_locations(soup)

def analyze_ajax_sources(soup):
    """分析AJAX请求的数据源"""
    scripts = soup.find_all('script')
    
    # 查找可能的AJAX端点
    ajax_patterns = [
        r'http[s]?://[^\s"\']*\.(json|html|php|aspx)[^\s"\']*',
        r'fetch\([\'"]([^\'"]+)[\'"]',
        r'\.get\([\'"]([^\'"]+)[\'"]',
        r'\.post\([\'"]([^\'"]+)[\'"]',
        r'XMLHttpRequest[^}]*url[^:]*:[\'"]([^\'"]+)[\'"]'
    ]
    
    found_endpoints = set()
    
    for script in scripts:
        if script.string:
            content = script.string
            for pattern in ajax_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]  # 获取第一个分组
                    if 'weather' in match.lower() or 'data' in match.lower():
                        found_endpoints.add(match)
    
    if found_endpoints:
        print("发现的潜在AJAX端点:")
        for endpoint in found_endpoints:
            print(f"  - {endpoint}")
    else:
        print("  未找到明显的AJAX端点")

def analyze_js_inserted_elements(soup):
    """查找通过JavaScript动态插入的元素"""
    print("  查找动态插入的天气数据容器:")
    
    # 常见的动态容器类名
    dynamic_containers = [
        'hour3', 'hours', 'hourly', 'weather_hours',
        'curve', 'livezs', 'tqtongji', 'dynamic-content'
    ]
    
    found_containers = []
    
    for container_class in dynamic_containers:
        elements = soup.find_all(class_=re.compile(container_class))
        for element in elements:
            found_containers.append({
                'class': container_class,
                'element': element.name,
                'preview': str(element)[:100] + '...' if len(str(element)) > 100 else str(element)
            })
    
    if found_containers:
        print("  发现的动态容器:")
        for container in found_containers:
            print(f"    - 类名包含: '{container['class']}', 元素: <{container['element']}>")
            print(f"      内容预览: {container['preview']}")
    else:
        print("  未找到明显的动态容器")

def analyze_timer_refresh_elements(soup):
    """识别定时刷新的数据区域"""
    scripts = soup.find_all('script')
    
    timer_patterns = [
        r'setInterval\([^,]*,\s*(\d+)\)',
        r'setTimeout\([^,]*,\s*(\d+)\)',
        r'\.autoRefresh\s*=\s*true',
        r'refresh.*\d+',
        r'timer.*\d+'
    ]
    
    timer_found = False
    
    for script in scripts:
        if script.string:
            content = script.string
            for pattern in timer_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"  发现定时刷新机制: {pattern}")
                    print(f"    匹配内容: {matches}")
                    timer_found = True
    
    if not timer_found:
        print("  未发现明显的定时刷新机制")

def analyze_data_storage_locations(soup):
    """分析数据存储位置"""
    print("  数据存储位置分析:")
    
    # 查找script标签中的数据变量
    scripts = soup.find_all('script')
    
    data_variables = []
    for script in scripts:
        if script.string:
            content = script.string
            # 查找包含天气数据的变量
            data_patterns = [
                r'var\s+(\w+)\s*=\s*({[^;]+});',
                r'window\.(\w+)\s*=\s*({[^;]+});',
                r'(\w+)\s*=\s*({[^;]+});'
            ]
            
            for pattern in data_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for var_name, var_value in matches:
                    if any(keyword in var_name.lower() for keyword in ['hour', 'weather', 'data', 'forecast']):
                        data_variables.append({
                            'var_name': var_name,
                            'preview': var_value[:200] + '...' if len(var_value) > 200 else var_value
                        })
    
    if data_variables:
        print("  发现的数据变量:")
        for data in data_variables:
            print(f"    - 变量名: {data['var_name']}")
            print(f"      数据预览: {data['preview']}")
    else:
        print("  未在script标签中发现明显的数据变量")

def save_dom_structure(soup, filename="dynamic_page_dom.html"):
    """保存页面的DOM结构到文件"""
    if not soup:
        print("没有可用的soup对象")
        return
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"DOM结构已保存到: {filename}")
        
        # 同时保存动态数据区域的DOM
        dynamic_areas = [
            ('curve_livezs', '曲线图区域'),
            ('hour3', '逐小时数据区域'),
            ('hours', '小时数据区域'),
            ('weather_hours', '天气小时数据')
        ]
        
        for class_name, description in dynamic_areas:
            element = soup.find(class_=re.compile(class_name))
            if element:
                dom_filename = f"dynamic_{class_name}_dom.html"
                with open(dom_filename, 'w', encoding='utf-8') as f:
                    f.write(element.prettify())
                print(f"{description}DOM已保存到: {dom_filename}")
                
    except Exception as e:
        print(f"保存DOM结构时出错: {e}")

def crawl_hourly_data(soup):
    if not soup:
        print("没有获取到页面内容")
        return
        
    print("\n=== 开始提取逐小时数据 ===")
    
    # 首先保存DOM结构
    save_dom_structure(soup)
    
    # 1. 查找所有可能的XHR请求端点
    scripts = soup.find_all('script')
    hourly_data = None
    
    for script in scripts:
        if script.string:
            content = script.string
            
            # 尝试多种可能的匹配模式
            patterns = [
                r'hour3data\s*=\s*({.*?});',
                r'var hour3data\s*=\s*({.*?});',
                r'window\.hour3data\s*=\s*({.*?});',
                r'hour3data:\s*({.*?})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(1)
                        hourly_data = json.loads(json_str)
                        print(f"成功使用模式 '{pattern}' 提取逐小时数据")
                        break
                    except (json.JSONDecodeError, Exception) as e:
                        print(f"JSON解析错误 (模式: {pattern}): {e}")
                        continue
            if hourly_data:
                break
    
    # 方法2：如果JavaScript提取失败，尝试从隐藏的input或数据属性中提取
    if not hourly_data:
        print("尝试从其他位置查找数据...")
        
        # 查找包含天气数据的script标签
        for script in scripts:
            if script.string and 'hour3data' in script.string:
                print("找到包含hour3data的script标签:")
                print(script.string[:500])  # 打印前500字符用于调试
                
                # 尝试更宽松的匹配
                match = re.search(r'hour3data\s*[=:]\s*({[^;]*})', script.string, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(1)
                        hourly_data = json.loads(json_str)
                        print("通过宽松匹配成功提取数据")
                        break
                    except Exception as e:
                        print(f"宽松匹配解析错误: {e}")
    
    # 处理提取到的数据
    if hourly_data:
        print(f"完整的数据结构: {list(hourly_data.keys())}")
        
        if '1d' in hourly_data:
            print("\n=== 上海逐小时天气预报 ===")
            for hour_data in hourly_data['1d']:
                parts = hour_data.split(',')
                if len(parts) >= 6:
                    time_slot = parts[0]
                    weather_icon = parts[1]
                    weather = parts[2]
                    temp = parts[3]
                    wind_direction = parts[4]
                    wind_level = parts[5]
                    print(f"时间: {time_slot}, 天气: {weather}, 温度: {temp}, 风向: {wind_direction}, 风力: {wind_level}")
            
            # 保存数据
            csv_file = save_hourly_data_to_csv(hourly_data['1d'])
            print(f"\n数据已保存到: {csv_file}")
        else:
            print(f"未找到'1d'键，可用键: {list(hourly_data.keys())}")
    else:
        print("未找到逐小时数据")
        
        # 调试：打印所有script标签的内容片段
        print("\n=== 所有script标签内容片段 ===")
        for i, script in enumerate(scripts[:10]):  # 只检查前10个script
            if script.string:
                content_preview = script.string.replace('\n', ' ').replace('\r', ' ')[:200]
                print(f"Script {i}: {content_preview}...")
    
    # 输出动态生成部分的DOM结构
    print("\n=== 动态生成区域的DOM结构 ===")
    curve_div = soup.find('div', class_='curve_livezs')
    if curve_div:
        print("曲线图区域的DOM结构（前800字符）:")
        print(curve_div.prettify()[:800])
    else:
        print("未找到曲线图区域")

def save_hourly_data_to_csv(hourly_data, filename="上海逐小时天气预报.csv"):
    """保存逐小时数据到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['时间', '天气', '温度', '风向', '风力', '天气图标']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for hour_data in hourly_data:
            parts = hour_data.split(',')
            if len(parts) >= 6:
                writer.writerow({
                    '时间': parts[0],
                    '天气': parts[2],
                    '温度': parts[3],
                    '风向': parts[4],
                    '风力': parts[5],
                    '天气图标': parts[1]
                })
    
    print(f"数据已保存到: {filename}")
    return filename

if __name__ == "__main__":
    soup = dynamic_browser_crawl()
    if soup:
        crawl_hourly_data(soup)
    else:
        print("无法获取页面内容")