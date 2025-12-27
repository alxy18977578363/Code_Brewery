import { ref } from 'vue'

// 模拟当前登录用户（实际应该从后端获取）
export const currentUser = ref({
  id: 1,
  username: 'admin',
  role: 'admin', // 'admin' | 'data_manager' | 'user'
  email: 'admin@example.com'
})

// 设置当前用户
export const setCurrentUser = (user) => {
  currentUser.value = user
}

// 获取当前用户角色
export const getUserRole = () => {
  return currentUser.value.role
}

// 角色权限映射
export const rolePermissions = {
  admin: ['dashboard', 'samples', 'measurements', 'locations', 'taxons', 'nuclides', 'users', 'audit', 'data-management', 'profile', 'info-center', 'data-map', 'data-analysis'],
  data_manager: ['dashboard', 'samples', 'measurements', 'locations', 'taxons', 'nuclides', 'data-management', 'profile', 'info-center', 'data-map', 'data-analysis'],
  user: ['dashboard', 'profile', 'info-center', 'data-map', 'data-analysis']
}

// 检查用户是否有某个权限
export const hasPermission = (permission) => {
  const role = getUserRole()
  return rolePermissions[role]?.includes(permission) || false
}