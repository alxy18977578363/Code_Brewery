import folium
import random

# 地图中心点（上海市中心附近）
center_lat, center_lon = 31.230, 121.470
m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

# 自行车图标 URL（也可换成其他图标）
bike_icon_url = 'https://tse1-mm.cn.bing.net/th/id/OIP-C.ZkiAT2XFkaSN-agDYUyd8AHaHa?rs=1&pid=ImgDetMain'
need_url = 'https://cdn-icons-png.flaticon.com/512/684/684908.png'

# 随机生成52个站点
stations = []
for i in range(52):
    # 在中心附近生成微小偏移
    lat = center_lat + random.uniform(-0.01, 0.01)
    lon = center_lon + random.uniform(-0.01, 0.01)
    name = f"站点{i+1}"
    stations.append({"name": name, "lat": lat, "lon": lon})

    # 添加到地图
    icon = folium.CustomIcon(bike_icon_url, icon_size=(32, 32))
    folium.Marker(
        location=[lat, lon],
        popup=name,
        icon=icon
    ).add_to(m)

needs = []
for i in range(30):
    # 在中心附近生成微小偏移
    lat = center_lat + random.uniform(-0.01, 0.01)
    lon = center_lon + random.uniform(-0.01, 0.01)
    name = f"站点{i+1}"
    needs.append({"name": name, "lat": lat, "lon": lon})

    # 添加到地图
    icon = folium.CustomIcon(need_url, icon_size=(32, 32))
    folium.Marker(
        location=[lat, lon],
        popup=name,
        icon=icon
    ).add_to(m)

# 保存地图
m.save('bike_station_map_52.html')

