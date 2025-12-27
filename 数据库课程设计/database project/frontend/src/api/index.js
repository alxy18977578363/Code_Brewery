import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:3000/api',  // ⚠️ 确保端口与backend/app.py一致
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加响应拦截器,查看具体错误
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API错误:', error.response || error)
    return Promise.reject(error)
  }
)

// 用户相关
export const userAPI = {
  getAll: () => api.get('/users'),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`)
}

// 样本相关
export const sampleAPI = {
  getAll: () => api.get('/samples'),
  getById: (id) => api.get(`/samples/${id}`),
  create: (data) => api.post('/samples', data),
  update: (id, data) => api.put(`/samples/${id}`, data),
  delete: (id) => api.delete(`/samples/${id}`)
}

// 测量记录相关
export const measurementAPI = {
  getAll: () => api.get('/measurements'),
  getById: (id) => api.get(`/measurements/${id}`),
  create: (data) => api.post('/measurements', data),
  update: (id, data) => api.put(`/measurements/${id}`, data),
  delete: (id) => api.delete(`/measurements/${id}`)
}

// 地点相关
export const locationAPI = {
  getAll: () => api.get('/locations'),
  getById: (id) => api.get(`/locations/${id}`),
  create: (data) => api.post('/locations', data),
  update: (id, data) => api.put(`/locations/${id}`, data),
  delete: (id) => api.delete(`/locations/${id}`)
}

// 放射源相关
export const radioactiveSourceAPI = {
  getAll: () => api.get('/data-management/table/RadioactiveSource')
}

// 物种相关
export const taxonAPI = {
  getAll: () => api.get('/taxons'),
  getById: (id) => api.get(`/taxons/${id}`),
  create: (data) => api.post('/taxons', data),
  update: (id, data) => api.put(`/taxons/${id}`, data),
  delete: (id) => api.delete(`/taxons/${id}`)
}

// 核素相关
export const nuclideAPI = {
  getAll: () => api.get('/nuclides'),
  getById: (id) => api.get(`/nuclides/${id}`),
  create: (data) => api.post('/nuclides', data),
  update: (id, data) => api.put(`/nuclides/${id}`, data),
  delete: (id) => api.delete(`/nuclides/${id}`)
}

// 统计相关
export const statsAPI = {
  getStats: () => api.get('/stats'),
  getRadioactivityTrend: () => api.get('/stats/radioactivity-trend'),
  getBioRadioactivity: () => api.get('/stats/bio-radioactivity'),
  getNuclideDistribution: () => api.get('/stats/nuclide-distribution'),
  getRecentEvents: () => api.get('/stats/recent-events'),
  getGeographicDistribution: () => api.get('/stats/geographic-distribution')
}

// 审批相关
export const approvalAPI = {
  // 提交审批请求
  submit: (data) => api.post('/approval/submit', data),
  // 获取待审批列表
  getPending: () => api.get('/approval/pending'),
  // 批准审批
  approve: (id, data) => api.post(`/approval/${id}/approve`, data),
  // 拒绝审批
  reject: (id, data) => api.post(`/approval/${id}/reject`, data)
}

export default api