<template>
  <div class="data-analysis">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <h2>海洋放射性数据分析</h2>
      <el-select v-model="selectedOcean" placeholder="选择海域" style="width: 200px">
        <el-option label="太平洋" value="Pacific Ocean" />
        <el-option label="大西洋" value="Atlantic Ocean" />
        <el-option label="印度洋" value="Indian Ocean" />
        <el-option label="北冰洋" value="Arctic Ocean" />
        <el-option label="全部海域" value="all" />
      </el-select>
    </div>

    <!-- 主图表区域 - 放射性浓度趋势 -->
    <el-card class="main-chart-card" v-loading="loading.trend">
      <template #header>
        <div class="card-header">
          <span>放射性物质平均浓度变化统计 (Bq/m³)</span>
          <el-tag>{{ selectedOcean === 'all' ? '全部海域' : selectedOcean }}</el-tag>
        </div>
      </template>
      <div ref="trendChartRef" class="chart" style="height: 350px;"></div>
    </el-card>

    <!-- 统计卡片区域 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="8">
        <el-card class="stat-card" v-loading="loading.stats">
          <div class="stat-value">{{ currentYearAvg }}</div>
          <div class="stat-label">当年平均浓度 Bq/m³</div>
          <div class="stat-trend" :class="trendClass">
            <el-icon v-if="trendDirection === 'up'"><CaretTop /></el-icon>
            <el-icon v-else-if="trendDirection === 'down'"><CaretBottom /></el-icon>
            <span>{{ trendPercent }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" v-loading="loading.stats">
          <div class="stat-value">{{ totalMeasurements }}</div>
          <div class="stat-label">总测量记录数</div>
          <div class="stat-info">
            <el-icon><Document /></el-icon>
            <span>累计数据</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card" v-loading="loading.stats">
          <div class="stat-value">{{ totalSamples }}</div>
          <div class="stat-label">生物样本数量</div>
          <div class="stat-info">
            <el-icon><Box /></el-icon>
            <span>样本总数</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 内容区域 -->
    <el-row :gutter="20" class="content-row">
      <!-- 左侧：生物放射性统计 -->
      <el-col :span="12">
        <el-card class="bio-card" v-loading="loading.bio">
          <template #header>
            <div class="card-header">
              <span>海洋生物放射性统计</span>
              <el-button link @click="refreshBioData">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="bio-list">
            <div 
              v-for="(item, index) in bioRadioactivity" 
              :key="index" 
              class="bio-item"
            >
              <div class="bio-info">
                <div class="bio-name">{{ item.species || '未知物种' }}</div>
                <div class="bio-habitat">{{ item.habitat || '未知栖息地' }}</div>
              </div>
              <div class="bio-value">
                <span class="value-range">
                  {{ item.minConcentration?.toFixed(2) || '0.00' }} - {{ item.maxConcentration?.toFixed(2) || '0.00' }}
                </span>
                <span class="value-unit">Bq/m³</span>
              </div>
            </div>
            <el-empty v-if="bioRadioactivity.length === 0" description="暂无数据" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：最新事件通知 -->
      <el-col :span="12">
        <el-card class="events-card" v-loading="loading.events">
          <template #header>
            <div class="card-header">
              <span>最新事件</span>
              <el-button link @click="refreshEvents">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="events-list">
            <div 
              v-for="(event, index) in recentEvents" 
              :key="index" 
              class="event-item"
            >
              <div class="event-icon" :class="`event-${event.status?.toLowerCase() || 'pending'}`">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="event-content">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-time">
                  <el-icon><Clock /></el-icon>
                  {{ formatTime(event.time) }}
                </div>
              </div>
              <el-tag 
                :type="getStatusType(event.status)" 
                size="small"
              >
                {{ getStatusText(event.status) }}
              </el-tag>
            </div>
            <el-empty v-if="recentEvents.length === 0" description="暂无事件" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 核素分布图表 -->
    <el-card class="nuclide-card" v-loading="loading.nuclide">
      <template #header>
        <div class="card-header">
          <span>核素分布统计</span>
          <el-radio-group v-model="nuclideViewType" size="small">
            <el-radio-button label="chart">图表</el-radio-button>
            <el-radio-button label="table">表格</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <div v-if="nuclideViewType === 'chart'" ref="nuclideChartRef" class="chart" style="height: 300px;"></div>
      
      <el-table v-else :data="nuclideDistribution" style="width: 100%" max-height="300">
        <el-table-column prop="symbol" label="核素符号" width="120" />
        <el-table-column prop="name" label="核素名称" />
        <el-table-column prop="avgConcentration" label="平均浓度 (Bq/m³)" width="180">
          <template #default="{ row }">
            {{ row.avgConcentration?.toFixed(3) || '0.000' }}
          </template>
        </el-table-column>
        <el-table-column prop="count" label="测量次数" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { statsAPI } from '../api'
import * as echarts from 'echarts'

// 状态管理
const selectedOcean = ref('all')
const nuclideViewType = ref('chart')

const loading = ref({
  trend: false,
  stats: false,
  bio: false,
  events: false,
  nuclide: false
})

// 数据
const trendData = ref([])
const bioRadioactivity = ref([])
const recentEvents = ref([])
const nuclideDistribution = ref([])
const statsData = ref({})

// 图表实例
let trendChart = null
let nuclideChart = null
const trendChartRef = ref(null)
const nuclideChartRef = ref(null)

// 计算属性
const currentYearAvg = computed(() => {
  if (trendData.value.length === 0) return '0.00'
  const latest = trendData.value[trendData.value.length - 1]
  // 计算所有核素的平均值
  const avg = (latest.cs137 + latest.co60 + latest.sr90 + latest.i131) / 4
  return avg.toFixed(2) || '0.00'
})

const totalMeasurements = computed(() => {
  return statsData.value.measurements || 0
})

const totalSamples = computed(() => {
  return statsData.value.samples || 0
})

const trendDirection = computed(() => {
  if (trendData.value.length < 2) return 'flat'
  const latest = trendData.value[trendData.value.length - 1]
  const previous = trendData.value[trendData.value.length - 2]
  const latestAvg = (latest.cs137 + latest.co60 + latest.sr90 + latest.i131) / 4
  const previousAvg = (previous.cs137 + previous.co60 + previous.sr90 + previous.i131) / 4
  if (latestAvg > previousAvg) return 'up'
  if (latestAvg < previousAvg) return 'down'
  return 'flat'
})

const trendPercent = computed(() => {
  if (trendData.value.length < 2) return '0%'
  const latest = trendData.value[trendData.value.length - 1]
  const previous = trendData.value[trendData.value.length - 2]
  const latestAvg = (latest.cs137 + latest.co60 + latest.sr90 + latest.i131) / 4
  const previousAvg = (previous.cs137 + previous.co60 + previous.sr90 + previous.i131) / 4
  if (previousAvg === 0) return '0%'
  const percent = ((latestAvg - previousAvg) / previousAvg * 100).toFixed(1)
  return `${Math.abs(percent)}%`
})

const trendClass = computed(() => {
  return trendDirection.value === 'up' ? 'trend-up' : trendDirection.value === 'down' ? 'trend-down' : ''
})

// 获取数据
const fetchRadioactivityTrend = async () => {
  loading.value.trend = true
  try {
    const response = await statsAPI.getRadioactivityTrend()
    trendData.value = response.data.data || []
    nextTick(() => {
      initTrendChart()
    })
  } catch (error) {
    console.error('获取放射性趋势失败:', error)
    ElMessage.error('获取放射性趋势数据失败')
  } finally {
    loading.value.trend = false
  }
}

const fetchBioRadioactivity = async () => {
  loading.value.bio = true
  try {
    const response = await statsAPI.getBioRadioactivity()
    bioRadioactivity.value = (response.data.data || []).slice(0, 10)
  } catch (error) {
    console.error('获取生物放射性统计失败:', error)
    ElMessage.error('获取生物放射性统计失败')
  } finally {
    loading.value.bio = false
  }
}

const fetchRecentEvents = async () => {
  loading.value.events = true
  try {
    const response = await statsAPI.getRecentEvents()
    recentEvents.value = response.data.data || []
  } catch (error) {
    console.error('获取最新事件失败:', error)
    ElMessage.error('获取最新事件失败')
  } finally {
    loading.value.events = false
  }
}

const fetchNuclideDistribution = async () => {
  loading.value.nuclide = true
  try {
    const response = await statsAPI.getNuclideDistribution()
    nuclideDistribution.value = response.data.data || []
    nextTick(() => {
      if (nuclideViewType.value === 'chart') {
        initNuclideChart()
      }
    })
  } catch (error) {
    console.error('获取核素分布失败:', error)
    ElMessage.error('获取核素分布数据失败')
  } finally {
    loading.value.nuclide = false
  }
}

const fetchStats = async () => {
  loading.value.stats = true
  try {
    const response = await statsAPI.getStats()
    statsData.value = response.data || {}
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    loading.value.stats = false
  }
}

// 初始化趋势图表
const initTrendChart = () => {
  if (!trendChartRef.value) return
  
  if (trendChart) {
    trendChart.dispose()
  }
  
  trendChart = echarts.init(trendChartRef.value)
  
  const years = trendData.value.map(item => item.year)
  const cs137Data = trendData.value.map(item => item.cs137)
  const co60Data = trendData.value.map(item => item.co60)
  const sr90Data = trendData.value.map(item => item.sr90)
  const i131Data = trendData.value.map(item => item.i131)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['Cs-137', 'Co-60', 'Sr-90', 'I-131']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: years
    },
    yAxis: {
      type: 'value',
      name: 'Bq/m³',
      min: 0,
      max: 1.0
    },
    series: [
      {
        name: 'Cs-137',
        type: 'line',
        data: cs137Data,
        smooth: true,
        areaStyle: {
          opacity: 0.2,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(255, 178, 128, 0.5)' },
              { offset: 1, color: 'rgba(255, 178, 128, 0.1)' }
            ]
          }
        },
        lineStyle: {
          color: '#ff9800',
          width: 2
        },
        itemStyle: {
          color: '#ff9800'
        }
      },
      {
        name: 'Co-60',
        type: 'line',
        data: co60Data,
        smooth: true,
        areaStyle: {
          opacity: 0.2,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(76, 175, 80, 0.5)' },
              { offset: 1, color: 'rgba(76, 175, 80, 0.1)' }
            ]
          }
        },
        lineStyle: {
          color: '#4caf50',
          width: 2
        },
        itemStyle: {
          color: '#4caf50'
        }
      },
      {
        name: 'Sr-90',
        type: 'line',
        data: sr90Data,
        smooth: true,
        areaStyle: {
          opacity: 0.2,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(33, 150, 243, 0.5)' },
              { offset: 1, color: 'rgba(33, 150, 243, 0.1)' }
            ]
          }
        },
        lineStyle: {
          color: '#2196f3',
          width: 2
        },
        itemStyle: {
          color: '#2196f3'
        }
      },
      {
        name: 'I-131',
        type: 'line',
        data: i131Data,
        smooth: true,
        areaStyle: {
          opacity: 0.2,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(156, 39, 176, 0.5)' },
              { offset: 1, color: 'rgba(156, 39, 176, 0.1)' }
            ]
          }
        },
        lineStyle: {
          color: '#9c27b0',
          width: 2
        },
        itemStyle: {
          color: '#9c27b0'
        }
      }
    ]
  }
  
  trendChart.setOption(option)
}

// 初始化核素图表
const initNuclideChart = () => {
  if (!nuclideChartRef.value) return
  
  if (nuclideChart) {
    nuclideChart.dispose()
  }
  
  nuclideChart = echarts.init(nuclideChartRef.value)
  
  const data = nuclideDistribution.value.slice(0, 10).map(item => ({
    name: item.symbol,
    value: item.avgConcentration
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} Bq/m³ ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      type: 'scroll'
    },
    series: [
      {
        name: '核素分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  }
  
  nuclideChart.setOption(option)
}

// 刷新数据
const refreshBioData = () => {
  fetchBioRadioactivity()
}

const refreshEvents = () => {
  fetchRecentEvents()
}

// 工具函数
const formatTime = (timeStr) => {
  if (!timeStr) return '未知时间'
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString('zh-CN')
}

const getStatusType = (status) => {
  const statusMap = {
    'Pending': 'warning',
    'Approved': 'success',
    'Rejected': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'Pending': '待处理',
    'Approved': '已批准',
    'Rejected': '已拒绝'
  }
  return textMap[status] || status
}

// 监听变化
watch(nuclideViewType, (newVal) => {
  if (newVal === 'chart') {
    nextTick(() => {
      initNuclideChart()
    })
  }
})

watch(selectedOcean, () => {
  // 根据选择的海域过滤数据
  fetchRadioactivityTrend()
})

// 页面加载时获取所有数据
onMounted(() => {
  fetchRadioactivityTrend()
  fetchBioRadioactivity()
  fetchRecentEvents()
  fetchNuclideDistribution()
  fetchStats()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    trendChart?.resize()
    nuclideChart?.resize()
  })
})
</script>

<style scoped>
.data-analysis {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.main-chart-card {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #ff9800;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}

.stat-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
}

.trend-up {
  color: #f56c6c;
}

.trend-down {
  color: #67c23a;
}

.stat-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #909399;
  font-size: 12px;
}

.content-row {
  margin-bottom: 20px;
}

.bio-card,
.events-card,
.nuclide-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.bio-list,
.events-list {
  max-height: 500px;
  overflow-y: auto;
}

.bio-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  transition: all 0.3s;
}

.bio-item:hover {
  background: #f5f7fa;
}

.bio-item:last-child {
  border-bottom: none;
}

.bio-info {
  flex: 1;
}

.bio-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.bio-habitat {
  font-size: 12px;
  color: #909399;
}

.bio-value {
  text-align: right;
}

.value-range {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.value-unit {
  font-size: 12px;
  color: #909399;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  transition: all 0.3s;
}

.event-item:hover {
  background: #f5f7fa;
}

.event-item:last-child {
  border-bottom: none;
}

.event-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.event-pending {
  background: #fdf6ec;
  color: #e6a23c;
}

.event-approved {
  background: #f0f9ff;
  color: #67c23a;
}

.event-rejected {
  background: #fef0f0;
  color: #f56c6c;
}

.event-content {
  flex: 1;
  min-width: 0;
}

.event-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.chart {
  width: 100%;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}

/* 滚动条样式 */
.bio-list::-webkit-scrollbar,
.events-list::-webkit-scrollbar {
  width: 6px;
}

.bio-list::-webkit-scrollbar-thumb,
.events-list::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.bio-list::-webkit-scrollbar-track,
.events-list::-webkit-scrollbar-track {
  background: #f5f7fa;
}
</style>