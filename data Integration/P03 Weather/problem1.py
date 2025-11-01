import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def crawl_weather_shanghai():
    url = "https://lishi.tianqi.com/shanghai/202509.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'  # 设置编码
        soup = BeautifulSoup(response.content, 'lxml')
        
        print("页面请求成功!")
        
        # 方法1: 通过tqtongji2类名查找（这个网站常用的类名）
        weather_list = soup.find('ul', class_='thrui')
        
        # 方法2: 如果上面找不到，尝试其他选择器
        if not weather_list:
            weather_list = soup.find('ul', class_='weather_list')
        if not weather_list:
            weather_list = soup.find('div', class_='tqtongji2')
            if weather_list:
                weather_list = weather_list.find('ul')
        
        if not weather_list:
            print("未找到天气数据，开始详细分析页面结构...")
            # 输出页面标题和关键元素帮助调试
            print("页面标题:", soup.title.text if soup.title else "无标题")
            
            # 查找所有可能的ul
            all_uls = soup.find_all('ul')
            for i, ul in enumerate(all_uls):
                print(f"UL {i}: 包含 {len(ul.find_all('li'))} 个li元素")
                if len(ul.find_all('li')) > 5:  # 假设天气数据有多个li
                    weather_list = ul
                    break
            
            if not weather_list:
                # 保存HTML用于分析
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                print("已保存页面到 debug_page.html，请检查文件分析结构")
                return []
        
        # 提取li中的天气数据
        weather_data = []
    
        # 找到包含天气数据的ul
        ul_content = soup.find('ul', class_='thrui')

        if ul_content:
            # 找到所有的li元素
            li_items = ul_content.find_all('li')

            for li in li_items:
                # 提取每个li中的所有th200和th140 div
                divs = li.find_all('div')

                if len(divs) >= 5:  # 确保有足够的div元素
                    date = divs[0].get_text(strip=True)  # 日期
                    high_temp = divs[1].get_text(strip=True)  # 最高温
                    low_temp = divs[2].get_text(strip=True)   # 最低温
                    weather = divs[3].get_text(strip=True)    # 天气状况
                    wind = divs[4].get_text(strip=True)       # 风力风向

                    weather_data.append({
                        '日期': date,
                        '最高温': high_temp,
                        '最低温': low_temp,
                        '天气状况': weather,
                        '风力风向': wind
                    })

        return weather_data, soup

        
    except Exception as e:
        print(f"爬取过程中出错: {e}")
        return [], None

def output_dom_structure(soup):
    """输出DOM结构并保存到文件"""
    if not soup:
        print("没有可用的soup对象")
        return
    
    print("\n=== DOM结构分析 ===")
    
    # 查找天气数据所在的容器
    weather_container = soup.find('ul', class_='thrui')
    if not weather_container:
        weather_container = soup.find('div', class_='tqtongji2')
    
    # 保存完整的页面DOM
    with open('static_full_page_dom.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("完整页面DOM已保存到 static_full_page_dom.html")
    
    if weather_container:
        print("找到天气数据容器")
        # 保存天气数据容器的DOM
        with open('static_weather_container_dom.html', 'w', encoding='utf-8') as f:
            f.write(weather_container.prettify())
        print("天气数据容器DOM已保存到 static_weather_container_dom.html")
        
        # 控制台输出前1500字符用于预览
        print("\n天气数据容器结构预览:")
        print(weather_container.prettify()[:1500])
    else:
        print("未找到天气数据容器")
        
        # 保存body结构
        body = soup.find('body')
        if body:
            with open('body_structure.html', 'w', encoding='utf-8') as f:
                f.write(body.prettify()[:5000])  # 限制长度
            print("页面主体结构已保存到 body_structure.html")
    

if __name__ == "__main__":

    # 执行爬取
    weather_data, soup = crawl_weather_shanghai()
    
    # 显示结果
    if weather_data:
        print("\n=== 爬取到的天气数据 ===")
        for i, data in enumerate(weather_data[:5]):  # 只显示前5条
            print(f"{i+1}. {data}")
        
        # 保存到CSV
        df = pd.DataFrame(weather_data)
        df.to_csv('上海天气_202509.csv', index=False, encoding='utf-8-sig')
        print(f"\n已保存 {len(weather_data)} 条数据到 上海天气_202509.csv")
    else:
        print("没有爬取到数据")
    
    # 输出DOM结构
    output_dom_structure(soup)