<!-- filepath: c:\Users\HS\Desktop\数据库\frontend\src\views\Home.vue -->
<template>
  <div>
    <div class="home-bg"></div>
    <div class="home" @click="handleStarClick">
      <StarBurstPerfect ref="starburstRef" style="position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:10;" />
      <!-- 欢迎横幅 -->
      <el-card class="welcome-banner" :body-style="{ padding: '0' }">
        <div class="banner-content">
          <div class="banner-left">
            <h1>欢迎使用蓝核智眼数据库管理系统</h1>
            <p>Marine Radioactivity Information System - 海洋放射性信息系统</p>
            <div class="banner-stats">
              <div class="stat-item">
                <el-icon :size="24"><TrendCharts /></el-icon>
                <span>实时监测</span>
              </div>
              <div class="stat-item">
                <el-icon :size="24"><DataAnalysis /></el-icon>
                <span>数据分析</span>
              </div>
              <div class="stat-item">
                <el-icon :size="24"><Location /></el-icon>
                <span>全球覆盖</span>
              </div>
            </div>
          </div>
          <div class="banner-right">
            <OceanCarousel />
          </div>
        </div>
      </el-card>

      <!-- 项目介绍与邀请意见 -->
      <el-row :gutter="32" style="margin-top: 32px;">
        <el-col :span="14">
          <el-card class="project-intro-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span style="font-size: 22px; font-weight: bold; margin-left: 8px;">项目简介</span>
              </div>
            </template>
            <div style="display: flex; gap: 32px; align-items: flex-start;">
              <img src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500&q=80" style="width: 220px; border-radius: 12px; box-shadow: 0 4px 16px #0001; object-fit: cover;" alt="海洋采样" />
              <div style="font-size: 17px; line-height: 2; color: #444;">
                <p style="font-size: 18px; font-weight: bold; color: #2d3a4b;">蓝核智眼数据库管理系统</p>
                <p>Marine Radioactivity Information System 致力于为海洋放射性监测、数据管理与分析提供一站式平台。系统集成了站点、样本、核素、测量等多维度数据，支持高效的数据录入、可视化分析与权限管理，助力科研、监管与公众服务。</p>
                <ul style="margin: 16px 0 0 20px;">
                  <li>🌊 支持全球范围的海洋放射性数据采集与管理</li>
                  <li>📊 丰富的数据统计与可视化能力</li>
                  <li>🔒 多角色权限体系，保障数据安全</li>
                  <li>🛠️ 灵活的扩展性，适配多种业务场景</li>
                  <li>✨ 体验更美观，交互更友好</li>
                </ul>
                <p style="margin-top: 24px; color: #666;">我们欢迎您的宝贵意见与建议，帮助我们不断完善系统功能与用户体验。请通过页面下方的反馈渠道联系我们，您的每一条建议都将被认真对待！</p>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="10">
          <el-card class="gallery-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><PictureFilled /></el-icon>
                <span style="font-size: 20px; font-weight: bold; margin-left: 8px;">项目掠影</span>
              </div>
            </template>
            <div class="gallery-grid">
              <img src="https://images.unsplash.com/photo-1508672019048-805c876b67e2?w=400&q=80" alt="全球覆盖" />
              <img src="https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=400&q=80" alt="科研协作" />
              <img src="https://images.unsplash.com/photo-1464983953574-0892a716854b?w=400&q=80" alt="海洋环境" />
              <img src="https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=400&q=80" alt="数据分析" />
            </div>
            <div style="margin-top: 18px; font-size: 16px; color: #4b5e7a; line-height: 2; font-style: italic;">
              我们选择用数据和科技守护海洋，不是因为它浩瀚无垠，而是因为每一滴海水都承载着生命的希望。让最美的海，依然可以被孩子们奔跑、被诗人歌咏、被科学家探索。守护蔚蓝，不只是责任，更是浪漫。
            </div>
          </el-card>
          <el-card class="feedback-card" shadow="hover" style="margin-top: 24px;">
            <template #header>
              <div class="card-header">
                <el-icon><Message /></el-icon>
                <span style="font-size: 20px; font-weight: bold; margin-left: 8px;">意见与建议</span>
              </div>
            </template>
            <div style="font-size: 15px; color: #555;">
              <p>如果您在使用过程中有任何问题、建议或合作意向，欢迎通过以下方式联系我们：</p>
              <ul style="margin: 12px 0 0 20px;">
                <li>📧 邮箱：2351136@tongji.edu.cn</li>
                <li>💬 反馈表单：<a href="#" style="color: #409eff;">点击填写</a></li>
                <li>📞 电话：无</li>
              </ul>
              <p style="margin-top: 18px; color: #888;">我们期待与您共同推动海洋环境保护与科学研究！</p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 数据库统计小卡片展示 -->
      <div class="db-cards-row" style="margin-top: 32px; display: flex; gap: 32px; flex-wrap: wrap;">
        <div class="db-card">
          <span class="db-emoji">👤</span>
          <span class="db-label">用户数</span>
          <span class="db-value" style="color:#7f5fff;">{{ stats.users }}</span>
        </div>
        <div class="db-card">
          <span class="db-emoji">🧪</span>
          <span class="db-label">样本数</span>
          <span class="db-value" style="color:#67c23a;">{{ stats.samples }}</span>
        </div>
        <div class="db-card">
          <span class="db-emoji">📄</span>
          <span class="db-label">检测记录</span>
          <span class="db-value" style="color:#e6a23c;">{{ stats.measurements }}</span>
        </div>
        <div class="db-card">
          <span class="db-emoji">📍</span>
          <span class="db-label">监测站点</span>
          <span class="db-value" style="color:#409eff;">{{ stats.locations }}</span>
        </div>
        <div class="db-card logo-card">
          <img :src="bluecoreLogo" alt="BlueCore Logo" style="height: 60px; margin-bottom: 6px;" />
          <span class="db-label" style="font-size: 18px; color: #2196f3; font-family: 'Pacifico', cursive;">BlueCore</span>
          <span class="db-value" style="font-size: 14px; color: #1565c0;">守护蔚蓝</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { statsAPI } from '../api'
import OceanCarousel from '../components/OceanCarousel.vue'
import StarBurstPerfect from '../components/StarBurstPerfect.vue'
import bluecoreLogo from '../assets/bluecore-logo.svg'

const stats = ref({
  users: 0,
  samples: 0,
  measurements: 0,
  locations: 0
})

const loading = ref(false)
const starEffect = ref({ visible: false, x: 0, y: 0 })
const starburstRef = ref(null)
const handleStarClick = (e) => {
  try {
    if (starburstRef.value && typeof starburstRef.value.starBurst === 'function') {
      starburstRef.value.starBurst({
        clientX: e.clientX,
        clientY: e.clientY,
        currentTarget: starburstRef.value.$el || document.body
      })
    } else {
      console.error('StarBurstPerfect ref 未绑定或 starBurst 方法不存在', starburstRef.value)
    }
  } catch (err) {
    console.error('星星特效触发异常:', err)
  }
}

onMounted(async () => {
  await fetchStats()
})

const fetchStats = async () => {
  loading.value = true
  try {
    const response = await statsAPI.getStats()
    if (response.data) {
      stats.value = {
        users: response.data.users || 0,
        samples: response.data.samples || 0,
        measurements: response.data.measurements || 0,
        locations: response.data.locations || 0
      }
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败，请检查后端服务是否正常运行')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  background: url('/images/aurora-bg.jpg') center center / cover no-repeat;
  opacity: 0.38;
  pointer-events: none;
  filter: blur(0.5px) brightness(1.08);
}
.gallery-card .gallery-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 8px;
}
.gallery-card .gallery-grid img {
  width: 100%;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px #0001;
  transition: transform 0.3s;
}
.gallery-card .gallery-grid img:hover {
  transform: scale(1.08) rotate(-2deg);
  box-shadow: 0 6px 18px #0002;
}
.el-card.welcome-banner {
  background: linear-gradient(135deg, rgba(102,126,234,0.38) 0%, rgba(118,75,162,0.38) 100%);
  box-shadow: 0 4px 24px #0002;
}
.project-intro-card {
  background: rgba(255,255,255,0.78);
}
.gallery-card {
  background: rgba(255,255,255,0.78);
}
.feedback-card {
  background: rgba(255,255,255,0.78);
}
.home {
  position: relative;
  z-index: 1;
  padding: 0;
}

/* 欢迎横幅 */
.welcome-banner {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.banner-content {
  display: flex;
  align-items: center;
  min-height: 200px;
}

.banner-left {
  flex: 1;
  padding: 32px;
  color: white;
}

.banner-left h1 {
  font-size: 32px;
  margin-bottom: 12px;
  font-weight: 700;
}

.banner-left p {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 24px;
}

.banner-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.banner-right {
  width: 500px;
  height: 260px;
  overflow: hidden;
  padding: 0 20px;
}

/* 统计卡片 */
.stats-row {
  margin-top: 24px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card.ocean-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.ocean-green {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-card.ocean-purple {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-card.ocean-orange {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px 0;
}

.stat-icon {
  opacity: 0.9;
}

.stat-details {
  flex: 1;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  opacity: 0.8;
}

/* 图表卡片 */
.chart-card {
  border-radius: 12px;
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 320px;
  color: #94a3b8;
}

/* 活动卡片 */
.activity-card {
  border-radius: 12px;
  min-height: 400px;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.db-overview-card {
  background: rgba(255,255,255,0.82);
  border-radius: 18px;
  box-shadow: 0 8px 32px #7f5fff22;
  border: none;
  padding: 24px 32px;
}
.db-overview-card .card-header {
  font-family: 'Pacifico', cursive;
  font-size: 32px;
  color: #67c23a;
  letter-spacing: 2px;
  text-shadow: 0 2px 12px #7f5fff33;
}
.db-overview-card ul {
  margin: 0;
  padding: 0;
  list-style: none;
}
.db-overview-card li {
  margin-bottom: 12px;
  font-size: 20px;
  font-weight: 500;
  display: flex;
  align-items: center;
}
.db-overview-card li span {
  margin-left: 8px;
  font-size: 22px;
  font-weight: bold;
  text-shadow: 0 2px 8px #409eff33;
}
.db-overview-card .db-icon {
  font-size: 28px;
  margin-right: 10px;
}
.art-card {
  background: linear-gradient(135deg, #e6a23c22 0%, #7f5fff22 100%);
  border-radius: 18px;
  box-shadow: 0 8px 32px #e6a23c22;
  border: none;
  padding: 24px 32px;
}
.art-card .card-header {
  font-family: 'Pacifico', cursive;
  font-size: 32px;
  color: #7f5fff;
  letter-spacing: 2px;
  text-shadow: 0 2px 12px #e6a23c33;
}
.art-card .art-main {
  font-size: 54px;
  font-family: 'Pacifico', cursive;
  color: #67c23a;
  text-shadow: 0 6px 32px #7f5fff55, 0 2px 12px #e6a23c33;
  margin-bottom: 12px;
}
.art-card .art-sub {
  font-size: 24px;
  color: #409eff;
  font-family: 'Pacifico', cursive;
  margin-bottom: 8px;
}
.art-card .art-desc {
  font-size: 16px;
  color: #888;
  margin-top: 18px;
  font-style: italic;
}
.db-cards-row {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
  justify-content: flex-start;
  margin-bottom: 24px;
}
.db-card {
  background: rgba(255,255,255,0.85);
  border-radius: 16px;
  box-shadow: 0 4px 16px #2196f322;
  padding: 18px 28px;
  min-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.18s;
  cursor: default;
}
.db-card:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 8px 32px #2196f333;
}
.db-emoji {
  font-size: 32px;
  margin-bottom: 8px;
}
.db-label {
  font-size: 16px;
  color: #444;
  font-weight: 500;
  margin-bottom: 4px;
}
.db-value {
  font-size: 22px;
  font-weight: bold;
  text-shadow: 0 2px 8px #2196f322;
}
.logo-card {
  background: linear-gradient(135deg, #b3e5fc 0%, #2196f3 100%);
  box-shadow: 0 4px 24px #2196f355;
}
</style>