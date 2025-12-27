<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { currentUser, setCurrentUser, hasPermission } from './store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const activeIndex = ref('/')

// 监听路由变化,更新活动菜单
watch(() => route.path, (newPath) => {
  activeIndex.value = newPath
}, { immediate: true })

const handleSelect = (key) => {
  router.push(key)
}

const switchRole = (role) => {
  setCurrentUser({
    ...currentUser.value,
    role: role
  })
  ElMessage.success(`已切换为${role === 'admin' ? '管理员' : role === 'data_manager' ? '数据管理员' : '普通用户'}`)
  router.push('/')
}
</script>

<template>
  <div class="app-container">
    <el-container style="height: 100vh;">
      <!-- 顶部导航栏 -->
      <el-header class="header" height="60px">
        <div class="header-left">
          <div class="logo">
            <el-icon :size="32" color="#fff">
              <Operation />
            </el-icon>
            <h1>蓝核智眼 海洋数据库</h1>
          </div>
        </div>
        <div class="header-right">
          <!-- 角色切换（演示用） -->
          <el-dropdown style="margin-right: 16px;" @command="switchRole">
            <el-button>
              切换角色
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="admin">管理员</el-dropdown-item>
                <el-dropdown-item command="data_manager">数据管理员</el-dropdown-item>
                <el-dropdown-item command="user">普通用户</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <el-badge :value="3" class="item">
            <el-button circle @click="router.push('/info-center')">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          
          <el-dropdown style="margin-left: 16px;">
            <el-avatar :size="40" style="cursor: pointer;">
              <el-icon><User /></el-icon>
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-container style="height: calc(100vh - 60px);">
        <!-- 侧边栏 -->
        <el-aside width="240px" class="sidebar">
          <div class="sidebar-header">
            <img src="https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=200&fit=crop" 
                 alt="Ocean" class="sidebar-image" />
            <div class="sidebar-overlay">
              <h3>{{ currentUser.role === 'admin' ? '管理员' : currentUser.role === 'data_manager' ? '数据管理员' : '用户' }}</h3>
              <p>{{ currentUser.username }}</p>
            </div>
          </div>
          
          <el-menu
            :default-active="activeIndex"
            class="el-menu-vertical"
            @select="handleSelect"
            :unique-opened="true"
          >
            <!-- 所有用户都能看到 -->
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>

            <!-- 普通用户功能 -->
            <el-sub-menu index="user-menu">
              <template #title>
                <el-icon><UserFilled /></el-icon>
                <span>个人中心</span>
              </template>
              
              <el-menu-item index="/profile">
                <el-icon><User /></el-icon>
                <span>个人信息</span>
              </el-menu-item>
              
              <el-menu-item index="/info-center">
                <el-icon><Bell /></el-icon>
                <span>信息中心</span>
              </el-menu-item>
            </el-sub-menu>

            <!-- 数据查看功能（所有用户） -->
            <el-sub-menu index="data-view">
              <template #title>
                <el-icon><DataAnalysis /></el-icon>
                <span>数据查看</span>
              </template>
              
              <el-menu-item index="/data-map">
                <el-icon><MapLocation /></el-icon>
                <span>数据地图</span>
              </el-menu-item>
              
              <el-menu-item index="/data-analysis">
                <el-icon><TrendCharts /></el-icon>
                <span>数据分析</span>
              </el-menu-item>
            </el-sub-menu>

            <!-- 数据管理（仅管理员和数据管理员） -->
            <el-menu-item index="/data-management" v-if="hasPermission('data-management')">
              <el-icon><Operation /></el-icon>
              <span>数据管理</span>
            </el-menu-item>
            

            
            <!-- 管理员专属功能 -->
            <el-sub-menu index="admin-menu" v-if="hasPermission('audit') || hasPermission('users')">
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>系统管理</span>
              </template>
              
              <el-menu-item index="/audit" v-if="hasPermission('audit')">
                <el-icon><CircleCheck /></el-icon>
                <span>数据审核</span>
              </el-menu-item>
              
              <el-menu-item index="/users" v-if="hasPermission('users')">
                <el-icon><User /></el-icon>
                <span>用户管理</span>
              </el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>
        
        <!-- 主内容区 -->
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
    
    <!-- 背景装饰 -->
    <div class="ocean-particles"></div>
  </div>
</template>

<style scoped>
.app-container {
  width: 100%;
  position: relative;
}

/* 顶部导航栏样式 */
.header {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(to right, #fff, #93c5fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-right {
  display: flex;
  align-items: center;
}

/* 侧边栏样式 */
.sidebar {
  background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.08);
  overflow-y: auto;  /* ✅ 允许滚动 */
  height: 100%;
}

.sidebar-header {
  position: relative;
  height: 150px;
  overflow: hidden;
  margin-bottom: 20px;
}

.sidebar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.sidebar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(30, 60, 114, 0.6), rgba(42, 82, 152, 0.8));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.sidebar-overlay h3 {
  color: white;
  font-size: 20px;
  font-weight: 600;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  margin: 0;
}

.sidebar-overlay p {
  color: white;
  font-size: 14px;
  margin: 4px 0 0 0;
  opacity: 0.9;
}

.el-menu-vertical {
  border-right: none;
  background: transparent;
}

.el-menu-item {
  color: #475569;
  transition: all 0.3s;
}

.el-menu-item:hover {
  background: rgba(59, 130, 246, 0.1) !important;
  color: #1e40af !important;
}

.el-menu-item.is-active {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, transparent 100%) !important;
  color: #1e40af !important;
  border-right: 3px solid #3b82f6;
}

/* 主内容区样式 */
.main-content {
  background: #f1f5f9;
  padding: 24px;
  overflow-y: auto;  /* ✅ 允许滚动 */
  position: relative;
  height: 100%;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 海洋粒子背景 */
.ocean-particles {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(96, 165, 250, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 20%, rgba(147, 197, 253, 0.1) 0%, transparent 50%);
  animation: float 15s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>