import { createRouter, createWebHistory } from 'vue-router'
import { hasPermission } from '../store/user'
import { ElMessage } from 'element-plus'
import Home from '../views/Home.vue'
import UserManagement from '../views/UserManagement.vue'
import SampleManagement from '../views/SampleManagement.vue'
import MeasurementManagement from '../views/MeasurementManagement.vue'
import LocationManagement from '../views/LocationManagement.vue'
import NuclideManagement from '../views/NuclideManagement.vue'
import Profile from '../views/Profile.vue'
import InfoCenter from '../views/InfoCenter.vue'
import DataMap from '../views/DataMap.vue'
import DataAnalysis from '../views/DataAnalysis.vue'
import DataAudit from '../views/DataAudit.vue'
import DataManagement from '../views/DataManagement.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { permission: 'dashboard' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { permission: 'profile' }
  },
  {
    path: '/info-center',
    name: 'InfoCenter',
    component: InfoCenter,
    meta: { permission: 'info-center' }
  },
  {
    path: '/data-map',
    name: 'DataMap',
    component: DataMap,
    meta: { permission: 'data-map' }
  },
  {
    path: '/data-analysis',
    name: 'DataAnalysis',
    component: DataAnalysis,
    meta: { permission: 'data-analysis' }
  },
  {
    path: '/users',
    name: 'Users',
    component: UserManagement,
    meta: { permission: 'users' }
  },
  {
    path: '/audit',
    name: 'Audit',
    component: DataAudit,
    meta: { permission: 'audit' }
  },
  {
    path: '/data-management',
    name: 'DataManagement',
    component: DataManagement,
    meta: { permission: 'data-management' }
  },
  {
    path: '/samples',
    name: 'Samples',
    component: SampleManagement,
    meta: { permission: 'samples' }
  },
  {
    path: '/measurements',
    name: 'Measurements',
    component: MeasurementManagement,
    meta: { permission: 'measurements' }
  },
  {
    path: '/locations',
    name: 'Locations',
    component: LocationManagement,
    meta: { permission: 'locations' }
  },
  {
    path: '/nuclides',
    name: 'Nuclides',
    component: NuclideManagement,
    meta: { permission: 'nuclides' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查权限
router.beforeEach((to, from, next) => {
  const permission = to.meta.permission
  if (permission && !hasPermission(permission)) {
    ElMessage.warning('您没有权限访问该页面')
    next('/')
  } else {
    next()
  }
})

export default router