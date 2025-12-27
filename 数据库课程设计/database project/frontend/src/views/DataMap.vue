<template>
  <div class="data-map">
    <!-- 筛选卡片 -->
    <el-card class="filter-card" shadow="hover">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-select v-model="selectedOcean" placeholder="选择海域" clearable style="width: 100%;" @change="filterLocations">
            <el-option label="全部海域" value="" />
            <el-option label="太平洋" value="Pacific Ocean" />
            <el-option label="大西洋" value="Atlantic Ocean" />
            <el-option label="印度洋" value="Indian Ocean" />
            <el-option label="北冰洋" value="Arctic Ocean" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input 
            v-model="searchText" 
            placeholder="搜索站点名称"
            clearable
            @input="filterLocations"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-checkbox-group v-model="showTypes" @change="updateMarkers">
            <el-checkbox label="stations">站点</el-checkbox>
            <el-checkbox label="samples">样本</el-checkbox>
          </el-checkbox-group>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" style="width: 100%;" @click="refreshMap">
            <el-icon><Refresh /></el-icon>
            刷新地图
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 地图主卡片 -->
    <el-card style="margin-top: 20px;" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="24" color="#3b82f6"><MapLocation /></el-icon>
            <span class="header-title">全球采样点分布地图</span>
            <el-tag style="margin-left: 10px;">{{ filteredLocations.length }} 个站点</el-tag>
          </div>
          <div class="header-right">
            <el-button-group>
              <el-button size="small" @click="resetView">
                <el-icon><Aim /></el-icon>
                重置视图
              </el-button>
              <el-button size="small" @click="toggleClusters">
                <el-icon><Grid /></el-icon>
                {{ clusterEnabled ? '关闭聚合' : '开启聚合' }}
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>
      
      <div class="map-wrapper">
        <div id="map" ref="mapContainer" class="map-container"></div>
        
        <!-- 图例 -->
        <div class="map-legend">
          <h4>图例说明</h4>
          <div class="legend-item">
            <div class="legend-marker green"></div>
            <span>正常水平站点</span>
          </div>
          <div class="legend-item">
            <div class="legend-marker red"></div>
            <span>高浓度站点</span>
          </div>
          <div class="legend-item">
            <div class="legend-marker blue"></div>
            <span>当前选中</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card>
          <el-statistic title="总站点数" :value="allLocations.length">
            <template #prefix>
              <el-icon color="#409eff"><Location /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic title="高浓度站点" :value="highConcentrationCount" :precision="0">
            <template #prefix>
              <el-icon color="#f56c6c"><Warning /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <el-statistic title="覆盖海域" :value="oceanCount">
            <template #prefix>
              <el-icon color="#67c23a"><Place /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { radioactiveSourceAPI } from '../api'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// 修复Leaflet默认图标问题
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// 状态
const loading = ref(false)
const selectedOcean = ref('')
const searchText = ref('')
const showTypes = ref(['stations'])
const clusterEnabled = ref(false)
const allLocations = ref([])
const filteredLocations = ref([])

// 地图相关
let map = null
const mapContainer = ref(null)
let markers = []

// 自定义图标
const createIcon = (color) => {
  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="25" height="41">
      <path d="M12 0C7.03 0 3 4.03 3 9c0 7.5 9 17 9 17s9-9.5 9-17c0-4.97-4.03-9-9-9z" 
            fill="${color}" stroke="white" stroke-width="1"/>
      <circle cx="12" cy="9" r="3" fill="white"/>
    </svg>
  `
  return L.divIcon({
    html: svgIcon,
    className: 'custom-marker',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34]
  })
}

const greenIcon = createIcon('#10b981')
const redIcon = createIcon('#ef4444')
const blueIcon = createIcon('#3b82f6')

// 计算属性
const highConcentrationCount = computed(() => {
  return Math.floor(allLocations.value.length * 0.3) // 模拟30%为高浓度
})

const oceanCount = computed(() => {
  const oceans = new Set(allLocations.value.map(loc => loc.OceanArea).filter(Boolean))
  return oceans.size
})

// 获取放射源数据
const fetchLocations = async () => {
  loading.value = true
  try {
    const res = await radioactiveSourceAPI.getAll()
    // 适配字段
    const data = (res.data || []).map((item, idx) => ({
      StationID: item.SourceID,
      StationName: item.SourceOrigin,
      Latitude: item.Latitude,
      Longitude: item.Longitude,
      OceanArea: item.CountryISO || '未知',
      WaterDepth: null,
      SampleCount: null,
      AvgConcentration: null
    }))
    allLocations.value = data
    filteredLocations.value = [...data]
    nextTick(() => {
      if (!map) {
        initMap()
      }
      updateMarkers()
    })
  } catch (e) {
    ElMessage.error('获取放射源数据失败')
  }
  loading.value = false
}

// 生成模拟数据（已废弃，实际开发用不到）
// const generateMockData = () => {}

// 初始化地图
const initMap = () => {
  if (!mapContainer.value) return
  
  map = L.map(mapContainer.value, {
    center: [20, 0],
    zoom: 2,
    minZoom: 2,
    maxZoom: 18,
    zoomControl: true
  })
  
  // 添加图层
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18
  }).addTo(map)
  
  // 添加缩放控件
  map.zoomControl.setPosition('topright')
}

// 更新标记
const updateMarkers = () => {
  if (!map) return
  
  // 清除旧标记
  markers.forEach(marker => map.removeLayer(marker))
  markers = []
  
  // 添加新标记
  filteredLocations.value.forEach((location, index) => {
    const lat = location.Latitude
    const lng = location.Longitude
    
    if (lat && lng && !isNaN(lat) && !isNaN(lng)) {
      // 根据浓度选择颜色
      const isHigh = (index % 3) === 0 // 模拟约1/3为高浓度
      const icon = isHigh ? redIcon : greenIcon
      
      const marker = L.marker([lat, lng], { icon })
        .bindPopup(`
          <div style="min-width: 200px;">
            <h3 style="margin: 0 0 8px 0; color: #303133;">${location.StationName || '未知站点'}</h3>
            <p style="margin: 4px 0;"><strong>海域:</strong> ${location.OceanArea || '未知'}</p>
            <p style="margin: 4px 0;"><strong>坐标:</strong> ${lat.toFixed(4)}°, ${lng.toFixed(4)}°</p>
            <p style="margin: 4px 0;"><strong>水深:</strong> ${location.WaterDepth ? location.WaterDepth.toFixed(0) + 'm' : '未知'}</p>
            <p style="margin: 4px 0;"><strong>样本数:</strong> ${location.SampleCount || 0}</p>
            <p style="margin: 4px 0; color: ${isHigh ? '#f56c6c' : '#67c23a'};">
              <strong>平均浓度:</strong> ${(Math.random() * 2).toFixed(3)} Bq/m³
            </p>
          </div>
        `)
        .addTo(map)
      
      markers.push(marker)
    }
  })
}

// 筛选站点
const filterLocations = () => {
  let filtered = [...allLocations.value]
  
  if (selectedOcean.value) {
    filtered = filtered.filter(loc => loc.OceanArea === selectedOcean.value)
  }
  
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(loc => 
      loc.StationName?.toLowerCase().includes(search) ||
      loc.OceanArea?.toLowerCase().includes(search)
    )
  }
  
  filteredLocations.value = filtered
  updateMarkers()
}

// 刷新地图
const refreshMap = () => {
  fetchLocations()
  ElMessage.success('地图已刷新')
}

// 重置视图
const resetView = () => {
  if (map) {
    map.setView([20, 0], 2)
  }
}

// 切换聚合
const toggleClusters = () => {
  clusterEnabled.value = !clusterEnabled.value
  ElMessage.info(clusterEnabled.value ? '聚合模式已开启' : '聚合模式已关闭')
}

// 页面加载
onMounted(() => {
  fetchLocations()
})
</script>

<style scoped>
.data-map {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.filter-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 8px;
}

.map-wrapper {
  position: relative;
  height: 600px;
}

.map-container {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
}

.map-legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
}

.map-legend h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: #606266;
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  border: 2px solid white;
  box-shadow: 0 0 4px rgba(0,0,0,0.3);
}

.legend-marker.green {
  background: #10b981;
}

.legend-marker.red {
  background: #ef4444;
}

.legend-marker.blue {
  background: #3b82f6;
}

:deep(.custom-marker) {
  background: transparent;
  border: none;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

:deep(.leaflet-popup-content) {
  margin: 12px;
}
</style>
