<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api, { approvalAPI } from '../api/index'
import { currentUser } from '../store/user'

// 当前选择的表
const currentTable = ref('Radionuclide')
const tableData = ref([])
const searchText = ref('')
const loading = ref(false)
const editMode = ref(false)
const dialogVisible = ref(false)
const dialogType = ref('add') // 'add' | 'edit'
const currentRow = ref({})
const pendingOperations = ref([])
const currentRowReadonlyMap = ref({}) // 新增：记录当前行各字段是否只读

// filter相关状态
const filter = ref({
  nuclide: '',
  sampleType: '',
  depthRange: [null, null],
  dateRange: []
})

// 适配不同表的filter显示
const showNuclideFilter = computed(() => currentTable.value === 'MeasurementRecord')
const showSampleTypeFilter = computed(() => currentTable.value === 'Sample' || currentTable.value === 'MeasurementRecord')
const showDepthFilter = computed(() => currentTable.value === 'Sample' || currentTable.value === 'MeasurementRecord')
const showDateFilter = computed(() => currentTable.value === 'Sample' || currentTable.value === 'MeasurementRecord')

// 核素类型选项（自动提取）
const nuclideOptions = computed(() => {
  if (currentTable.value === 'MeasurementRecord') {
    const set = new Set(tableData.value.map(row => row.NuclideName || row.Nuclide || row.nuclide))
    return Array.from(set).filter(Boolean)
  }
  return []
})
// 样本类型选项
const sampleTypeOptions = ['洋流', '沉积物', '生物']

// 深度范围（自动计算）
const depthArr = computed(() => {
  if (currentTable.value === 'Sample' || currentTable.value === 'MeasurementRecord') {
    return tableData.value.map(row => Number(row.SamplingDepth || row.Depth || row.depth)).filter(v => !isNaN(v))
  }
  return []
})
const depthMin = computed(() => depthArr.value.length ? Math.min(...depthArr.value) : 0)
const depthMax = computed(() => depthArr.value.length ? Math.max(...depthArr.value) : 3000)

// 表定义（根据demo.sql）
const tables = [
  { value: 'Radionuclide', label: '放射性核素表', api: 'Radionuclide' },
  { value: 'OceanCurrent', label: '洋流表', api: 'OceanCurrent' },
  { value: 'RadioactiveSource', label: '放射源表', api: 'RadioactiveSource' },
  { value: 'CurrentSourceRelation', label: '洋流-放射源关系表', api: 'CurrentSourceRelation' },
  { value: 'Station', label: '监测站点表', api: 'Station' },
  { value: 'Sample', label: '样本表', api: 'Sample' },
  { value: 'MeasurementRecord', label: '检测记录表', api: 'MeasurementRecord' },
  { value: 'UserRecordRelation', label: '用户记录关系表', api: 'UserRecordRelation' }
]

// 表结构定义 - 用于动态生成表单（根据demo.sql）
const tableSchemas = {
  Radionuclide: {
    fields: [
      { key: 'NuclideID', label: '核素ID', type: 'number', required: false, readonly: true },
      { key: 'Name', label: '名称', type: 'text', required: true },
      { key: 'Symbol', label: '符号标识', type: 'text', required: true },
      { key: 'HalfLife', label: '半衰期', type: 'text' },
      { key: 'RadioactiveType', label: '放射性类型', type: 'text' }
    ]
  },
  OceanCurrent: {
    fields: [
      { key: 'CurrentName', label: '洋流名称', type: 'text', required: true },
      { key: 'Direction', label: '流向', type: 'text' },
      { key: 'FlowRate', label: '流量(Sv)', type: 'number' },
      { key: 'Velocity', label: '流速(m/s)', type: 'number' }
    ]
  },
  RadioactiveSource: {
    fields: [
      { key: 'SourceID', label: '放射源ID', type: 'number', required: false, readonly: true },
      { key: 'SourceOrigin', label: '来源', type: 'text', required: true },
      { key: 'DiscoveryTime', label: '发现时间', type: 'datetime' },
      { key: 'OperationStatus', label: '运行状态', type: 'select', options: ['Active', 'Inactive', 'Monitoring', 'Decommissioned'] },
      { key: 'Longitude', label: '经度', type: 'number', required: true },
      { key: 'Latitude', label: '纬度', type: 'number', required: true },
      { key: 'CountryISO', label: '国家ISO编码', type: 'text' },
      { key: 'NuclideID', label: '核素ID', type: 'number', required: true }
    ]
  },
  CurrentSourceRelation: {
    fields: [
      { key: 'RelationID', label: '关系ID', type: 'number', required: false, readonly: true },
      { key: 'CurrentName', label: '洋流名称', type: 'text', required: true },
      { key: 'SourceID', label: '放射源ID', type: 'number', required: true },
      { key: 'ImpactLevel', label: '影响等级', type: 'select', options: ['Low', 'Medium', 'High'] }
    ]
  },
  Station: {
    fields: [
      { key: 'StationID', label: '站点ID', type: 'number', required: false, readonly: true },
      { key: 'StationName', label: '站点名称', type: 'text', required: true },
      { key: 'Longitude', label: '经度', type: 'number', required: true },
      { key: 'Latitude', label: '纬度', type: 'number', required: true },
      { key: 'OceanDepth', label: '海洋深度(m)', type: 'number' },
      { key: 'RegionDescription', label: '区域描述', type: 'text' },
      { key: 'StationType', label: '站点类型', type: 'text' }
    ]
  },
  Sample: {
    fields: [
      { key: 'SampleID', label: '样本ID', type: 'number', required: false, readonly: true },
      { key: 'SampleType', label: '样本类型', type: 'select', required: true, options: ['Biota', 'Seawater', 'Sediment', 'Suspended Matter'] },
      { key: 'SamplingTime', label: '采样时间', type: 'datetime', required: true },
      { key: 'SamplingDepth', label: '采样深度(m)', type: 'number' },
      { key: 'LocationDescription', label: '位置描述', type: 'text' },
      { key: 'StationID', label: '站点ID', type: 'number', required: true }
    ]
  },
  MeasurementRecord: {
    fields: [
      { key: 'RecordID', label: '记录ID', type: 'number', required: false, readonly: true },
      { key: 'Activity', label: '活度值', type: 'number', required: true },
      { key: 'Uncertainty', label: '不确定度', type: 'number' },
      { key: 'Unit', label: '单位', type: 'text', required: true },
      { key: 'MeasurementType', label: '测量类型', type: 'text' },
      { key: 'TestingOrganization', label: '检测机构', type: 'text' },
      { key: 'ReportNumber', label: '报告编号', type: 'text' },
      { key: 'CompletionTime', label: '完成时间', type: 'datetime' },
      { key: 'SampleID', label: '样本ID', type: 'number', required: true },
      { key: 'NuclideID', label: '核素ID', type: 'number', required: true }
    ]
  },
  UserRecordRelation: {
    fields: [
      { key: 'RelationID', label: '关系ID', type: 'number', required: false, readonly: true },
      { key: 'UserID', label: '用户ID', type: 'number', required: true },
      { key: 'RecordID', label: '记录ID', type: 'number', required: true },
      { key: 'ActionType', label: '操作类型', type: 'select', required: true, options: ['View', 'Audit', 'Edit', 'Delete'] },
      { key: 'ActionTime', label: '操作时间', type: 'datetime' }
    ]
  }
}

// 当前表的字段配置
const currentSchema = computed(() => {
  return tableSchemas[currentTable.value] || { fields: [] }
})

// 通用filter字段自动生成
const autoFilters = computed(() => {
  const schema = currentSchema.value?.fields || []
  return schema.map(field => {
    if (field.type === 'select' && field.options) {
      // select类型
      return { key: field.key, label: field.label, type: 'select', options: field.options }
    } else if (field.type === 'number') {
      // 数值区间
      const arr = tableData.value ? tableData.value.map(row => Number(row[field.key])).filter(v => !isNaN(v)) : []
      return { key: field.key, label: field.label, type: 'number', min: arr.length ? Math.min(...arr) : 0, max: arr.length ? Math.max(...arr) : 100 }
    } else if (field.type === 'datetime' || field.type === 'date') {
      // 日期区间
      const arr = tableData.value ? tableData.value.map(row => row[field.key]).filter(Boolean) : []
      arr.sort()
      return { key: field.key, label: field.label, type: 'date', min: arr[0], max: arr[arr.length-1] }
    } else if (field.type === 'text') {
      // 自动生成数据库唯一值选项
      const set = new Set(tableData.value.map(row => row[field.key]).filter(Boolean))
      const options = Array.from(set)
      return { key: field.key, label: field.label, type: 'dropdown', options }
    }
    return null
  }).filter(Boolean)
})

// 通用filter状态
const autoFilterState = ref({})

// 每次表切换或数据加载后，自动重置filter区间为最大最小值
watch([currentTable, tableData], () => {
  autoFilterState.value = {}
  autoFilters.value.forEach(f => {
    if (f.type === 'number') {
      autoFilterState.value[f.key] = [f.min, f.max]
    } else if (f.type === 'date') {
      autoFilterState.value[f.key] = f.min && f.max ? [f.min, f.max] : []
    } else {
      autoFilterState.value[f.key] = ''
    }
  })
}, { immediate: true })

// 通用filter筛选逻辑
function applyAutoFilter(data) {
  let d = data
  autoFilters.value.forEach(f => {
    const val = autoFilterState.value[f.key]
    if (val === undefined || val === '' || (Array.isArray(val) && val.length === 0)) return
    if (f.type === 'select' || f.type === 'dropdown') {
      d = d.filter(row => row[f.key] === val)
    } else if (f.type === 'number' && Array.isArray(val)) {
      d = d.filter(row => {
        const v = Number(row[f.key])
        return !isNaN(v) && v >= val[0] && v <= val[1]
      })
    } else if (f.type === 'date' && Array.isArray(val)) {
      d = d.filter(row => {
        const t = row[f.key]
        return t && t >= val[0] && t <= val[1]
      })
    }
  })
  return d
}

// 查询过滤后的数据
const filteredTableData = computed(() => {
  let data = tableData.value
  data = applyAutoFilter(data)
  // 1.核素类型
  if (showNuclideFilter.value && filter.value.nuclide) {
    data = data.filter(row => (row.NuclideName || row.Nuclide || row.nuclide) === filter.value.nuclide)
  }
  // 2.样本类型
  if (showSampleTypeFilter.value && filter.value.sampleType) {
    data = data.filter(row => (row.SampleType || row.sampleType) === filter.value.sampleType)
  }
  // 3.深度范围
  if (showDepthFilter.value && filter.value.depthRange[0] !== null && filter.value.depthRange[1] !== null) {
    data = data.filter(row => {
      const d = Number(row.SamplingDepth || row.Depth || row.depth)
      return !isNaN(d) && d >= filter.value.depthRange[0] && d <= filter.value.depthRange[1]
    })
  }
  // 4.事件范围
  if (showDateFilter.value && filter.value.dateRange.length === 2) {
    const [start, end] = filter.value.dateRange
    data = data.filter(row => {
      const t = row.SamplingTime || row.CompletionTime || row.time || row.采样时间
      if (!t) return false
      return t >= start && t <= end
    })
  }
  // 5.关键字
  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    data = data.filter(row => Object.values(row).some(val => val && String(val).toLowerCase().includes(keyword)))
  }
  return data
})

// 加载表数据
const loadTableData = async () => {
  loading.value = true
  try {
    const table = tables.find(t => t.value === currentTable.value)
    const response = await api.get(`/data-management/table/${table.api}`)
    tableData.value = response.data || []
    ElMessage.success(`加载${table.label}成功`)
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
    tableData.value = []
  } finally {
    loading.value = false
  }
}

// 切换表
const handleTableChange = () => {
  editMode.value = false
  loadTableData()
}

// 开启编辑模式
const toggleEditMode = () => {
  if (!editMode.value) {
    // 进入编辑模式
    if (currentUser.value.role !== 'admin' && currentUser.value.role !== 'data_manager') {
      ElMessage.warning('您没有权限编辑数据')
      return
    }
    editMode.value = true
    ElMessage.info('已进入编辑模式，添加或删除操作将直接提交审核')
  } else {
    // 退出编辑模式
    editMode.value = false
    loadTableData()
  }
}

// 打开添加对话框
const handleAdd = () => {
  dialogType.value = 'add'
  currentRow.value = {}
  currentSchema.value.fields.forEach(field => {
    if (field.type === 'number') {
      currentRow.value[field.key] = null
    } else {
      currentRow.value[field.key] = ''
    }
  })
  dialogVisible.value = true
}

// 添加记录并直接提交审批
const confirmAdd = async () => {
  // 验证必填字段
  const requiredFields = currentSchema.value.fields.filter(f => f.required)
  for (const field of requiredFields) {
    if (!currentRow.value[field.key]) {
      ElMessage.warning(`请填写${field.label}`)
      return
    }
  }

  const operation = {
    type: 'add',
    data: { ...currentRow.value },
    time: new Date().toLocaleString()
  }
  
  dialogVisible.value = false
  
  // 直接提交审批
  await submitSingleOperation(operation)
}

// 打开编辑对话框，标记不可编辑字段
const handleEdit = (row) => {
  dialogType.value = 'edit'
  currentRow.value = {}
  currentSchema.value.fields.forEach(field => {
    if (field.type === 'number') {
      currentRow.value[field.key] = row[field.key] ?? null
    } else {
      currentRow.value[field.key] = row[field.key] ?? ''
    }
  })
  // 标记哪些字段不可编辑（数据库依赖字段）
  const schema = currentSchema.value.fields
  currentRowReadonlyMap.value = {}
  schema.forEach(field => {
    if (field.readonly || field.key.endsWith('ID')) {
      currentRowReadonlyMap.value[field.key] = true
    } else {
      currentRowReadonlyMap.value[field.key] = false
    }
  })
  dialogVisible.value = true
}

// 新增：编辑记录并直接提交审批
const confirmEdit = async () => {
  // 验证必填字段
  const requiredFields = currentSchema.value.fields.filter(f => f.required)
  for (const field of requiredFields) {
    if (!currentRow.value[field.key]) {
      ElMessage.warning(`请填写${field.label}`)
      return
    }
  }
  // 检查不可编辑字段是否被修改（可扩展为后端校验）
  const readonlyFields = Object.keys(currentRowReadonlyMap.value).filter(key => currentRowReadonlyMap.value[key])
  for (const key of readonlyFields) {
    if (currentRow.value[key] !== undefined && currentRow.value[key] !== null) {
      ElMessage.warning(`${key} 字段不可编辑`)
      return
    }
  }
  const operation = {
    type: 'edit',
    data: { ...currentRow.value },
    time: new Date().toLocaleString()
  }
  dialogVisible.value = false
  await submitSingleOperation(operation)
}

// 删除记录并直接提交审批
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条记录吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const operation = {
      type: 'delete',
      data: { ...row },
      time: new Date().toLocaleString()
    }
    
    // 直接提交审批
    await submitSingleOperation(operation)
  } catch (error) {
    // 用户取消删除
  }
}

// 提交单个操作到审批
const submitSingleOperation = async (operation) => {
  loading.value = true
  try {
    // 如果当前用户是管理员，直接执行
    if (currentUser.value.role === 'admin') {
      await executeOperations([operation])
    } else {
      // 数据管理员提交给管理员审批
      const requestBody = {
        table: currentTable.value,
        operations: [operation],
        requestUser: currentUser.value.username,
        requestUserID: currentUser.value.id
      }
      
      await approvalAPI.submit(requestBody)
      ElMessage.success('已提交审批请求，请等待管理员审批')
    }
    
    // 刷新数据
    await loadTableData()
  } catch (error) {
    console.error('提交审批失败:', error)
    ElMessage.error('提交审批失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 提交审批（批量操作 - 已废弃）
const submitForApproval = async () => {
  if (pendingOperations.value.length === 0) {
    ElMessage.warning('没有待提交的操作')
    return
  }

  // 如果当前用户是管理员，直接执行
  if (currentUser.value.role === 'admin') {
    ElMessageBox.confirm(
      `您有${pendingOperations.value.length}个操作待执行，确定要立即执行吗？`,
      '管理员确认',
      {
        confirmButtonText: '立即执行',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true,
        message: `
          <div style="margin-bottom: 10px;">
            <strong>操作数量：</strong>${pendingOperations.value.length}个<br/>
            <strong>目标表：</strong>${tables.find(t => t.value === currentTable.value).label}<br/>
            <strong>提示：</strong>操作将立即生效，请谨慎确认
          </div>
        `
      }
    ).then(async () => {
      await executeOperations()
    })
  } else {
    // 数据管理员提交给管理员审批
    ElMessageBox.confirm(
      `您有${pendingOperations.value.length}个操作待提交，这些操作需要管理员审批后才能执行`,
      '提交审批',
      {
        confirmButtonText: '提交',
        cancelButtonText: '取消',
        type: 'info',
        dangerouslyUseHTMLString: true,
        message: `
          <div style="margin-bottom: 10px;">
            <strong>操作数量：</strong>${pendingOperations.value.length}个<br/>
            <strong>目标表：</strong>${tables.find(t => t.value === currentTable.value).label}<br/>
            <strong>提示：</strong>提交后需等待管理员审批
          </div>
        `
      }
    ).then(async () => {
      try {
        // 调用API提交审批请求
        const requestBody = {
          table: currentTable.value,
          operations: pendingOperations.value,
          requestUser: currentUser.value.username,
          requestUserID: currentUser.value.id
        }
        
        await approvalAPI.submit(requestBody)
        ElMessage.success('已提交审批请求，请等待管理员审批')
        pendingOperations.value = []
        editMode.value = false
      } catch (error) {
        console.error('提交审批失败:', error)
        ElMessage.error('提交审批失败: ' + (error.message || '未知错误'))
      }
    })
  }
}

// 执行操作（管理员）
const executeOperations = async (operations = pendingOperations.value) => {
  loading.value = true
  try {
    const table = tables.find(t => t.value === currentTable.value)
    
    // 构建批量操作请求
    const requestBody = {
      table: table.api,
      operations: operations
    }
    
    const response = await api.post('/data-management/execute', requestBody)
    
    ElMessage.success(`操作执行成功: 成功${response.data.success}个，失败${response.data.failed}个`)
    
    if (response.data.errors && response.data.errors.length > 0) {
      console.error('部分操作失败:', response.data.errors)
    }
    
    pendingOperations.value = []
    editMode.value = false
    await loadTableData()
  } catch (error) {
    console.error('执行操作失败:', error)
    ElMessage.error('执行操作失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 移除待处理操作
const removePendingOperation = (index) => {
  pendingOperations.value.splice(index, 1)
  ElMessage.info('已移除该操作')
}

// 初始化
onMounted(() => {
  loadTableData()
})
</script>

<template>
  <div class="data-management">
    <el-card class="header-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon :size="24" color="#1e40af">
              <Operation />
            </el-icon>
            <span class="title">数据管理</span>
            <el-tag v-if="currentUser.role === 'admin'" type="danger" effect="dark">管理员</el-tag>
            <el-tag v-else-if="currentUser.role === 'data_manager'" type="warning" effect="dark">数据管理员</el-tag>
          </div>
          <div class="header-right">
            <el-select 
              v-model="currentTable" 
              @change="handleTableChange"
              style="width: 200px; margin-right: 12px;"
            >
              <el-option
                v-for="table in tables"
                :key="table.value"
                :label="table.label"
                :value="table.value"
              />
            </el-select>
            <el-button 
              :type="editMode ? 'warning' : 'primary'" 
              @click="toggleEditMode"
              :icon="editMode ? 'Close' : 'Edit'"
            >
              {{ editMode ? '退出编辑' : '编辑模式' }}
            </el-button>
          </div>
        </div>
      </template>

      <!-- 通用filter区（所有表均有） -->
      <div class="filter-bar">
        <el-form :inline="true" size="default" style="flex-wrap: wrap;">
          <template v-for="f in autoFilters" :key="f.key">
            <el-form-item v-if="f.type==='select'" :label="f.label">
              <el-select v-model="autoFilterState[f.key]" clearable :placeholder="'全部'+f.label" style="width: 160px;">
                <el-option v-for="item in f.options" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
            <el-form-item v-else-if="f.type==='number'" :label="f.label+'区间'">
              <template v-if="f.min !== f.max && f.min !== undefined && f.max !== undefined && f.min !== null && f.max !== null">
                <el-slider
                  v-model="autoFilterState[f.key]"
                  range
                  :min="f.min"
                  :max="f.max"
                  :step="1"
                  style="width: 220px;"
                  :marks="{ [f.min]: f.min+'', [f.max]: f.max+'' }"
                />
              </template>
              <template v-else>
                <el-input :value="f.min ?? ''" disabled style="width: 120px; text-align: center;" />
              </template>
            </el-form-item>
            <el-form-item v-else-if="f.type==='date'" :label="f.label+'范围'">
              <el-date-picker
                v-model="autoFilterState[f.key]"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 260px;"
              />
            </el-form-item>
            <el-form-item v-else-if="f.type==='dropdown'" :label="f.label">
              <el-select
                v-model="autoFilterState[f.key]"
                clearable
                filterable
                :placeholder="'全部'+f.label"
                style="width: 160px;"
                popper-class="filter-dropdown-popper"
                :max-collapse-tags="8"
                >
                <el-option v-for="item in f.options" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </template>
        </el-form>
      </div>
      <div class="table-container">
        <div style="margin-bottom: 12px; display: flex; justify-content: flex-end;">
          <el-input
            v-model="searchText"
            placeholder="请输入关键字查询"
            clearable
            style="width: 260px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <el-table 
          :data="filteredTableData" 
          :loading="loading"
          stripe
          border
          style="width: 100%"
          height="500"
        >
          <el-table-column 
            v-for="field in currentSchema.fields" 
            :key="field.key"
            :prop="field.key"
            :label="field.label"
            :min-width="120"
          />
          <el-table-column 
            v-if="editMode"
            label="操作" 
            width="160"
            fixed="right"
          >
            <template #default="{ row }">
              <div style="display: flex; align-items: center; gap: 8px;">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleEdit(row)"
                  :icon="'Edit'"
                >
                  修改
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="handleDelete(row)"
                  :icon="'Delete'"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 编辑模式工具栏 -->
      <div v-if="editMode" class="edit-toolbar">
        <div class="toolbar-left">
          <el-button type="success" @click="handleAdd" :icon="'Plus'">
            添加记录
          </el-button>
          <el-tag type="success">
            操作将直接提交审核
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 待处理操作列表（已移除） -->
    <el-card v-if="false" class="pending-card">
      <template #header>
        <div class="card-header">
          <span class="title">待处理操作</span>
          <el-tag type="warning">{{ pendingOperations.length }}个操作</el-tag>
        </div>
      </template>

      <el-timeline>
        <el-timeline-item
          v-for="(operation, index) in pendingOperations"
          :key="index"
          :timestamp="operation.time"
          placement="top"
        >
          <el-card>
            <div class="operation-item">
              <div class="operation-info">
                <el-tag :type="operation.type === 'add' ? 'success' : 'danger'" size="small">
                  {{ operation.type === 'add' ? '添加' : '删除' }}
                </el-tag>
                <span class="operation-data">
                  {{ JSON.stringify(operation.data, null, 2) }}
                </span>
              </div>
              <el-button 
                type="danger" 
                size="small" 
                @click="removePendingOperation(index)"
                :icon="'Close'"
              >
                移除
              </el-button>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加记录' : '编辑记录'"
      width="600px"
    >
      <el-form :model="currentRow" label-width="120px">
        <el-form-item 
          v-for="field in currentSchema.fields" 
          :key="field.key"
          :label="field.label"
          :required="field.required"
          :class="{ 'readonly-field': currentRowReadonlyMap.value && typeof currentRowReadonlyMap.value === 'object' ? currentRowReadonlyMap.value[field.key] : false }"
        >
          <el-input 
            v-if="field.type === 'text'"
            v-model="currentRow[field.key]"
            :placeholder="`请输入${field.label}`"
            :disabled="currentRowReadonlyMap.value && typeof currentRowReadonlyMap.value === 'object' && currentRowReadonlyMap.value[field.key] && dialogType === 'edit'"
          />
          <el-input-number 
            v-else-if="field.type === 'number'"
            v-model="currentRow[field.key]"
            :placeholder="`请输入${field.label}`"
            style="width: 100%"
            :disabled="currentRowReadonlyMap.value && typeof currentRowReadonlyMap.value === 'object' && currentRowReadonlyMap.value[field.key] && dialogType === 'edit'"
          />
          <el-date-picker
            v-else-if="field.type === 'date'"
            v-model="currentRow[field.key]"
            type="date"
            :placeholder="`请选择${field.label}`"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
          <el-date-picker
            v-else-if="field.type === 'datetime'"
            v-model="currentRow[field.key]"
            type="datetime"
            :placeholder="`请选择${field.label}`"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
          <el-select
            v-else-if="field.type === 'select'"
            v-model="currentRow[field.key]"
            :placeholder="`请选择${field.label}`"
            style="width: 100%"
            :disabled="currentRowReadonlyMap.value && typeof currentRowReadonlyMap.value === 'object' && currentRowReadonlyMap.value[field.key] && dialogType === 'edit'"
          >
            <el-option
              v-for="option in field.options"
              :key="option"
              :label="option"
              :value="option"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogType === 'add' ? confirmAdd() : confirmEdit()">{{ dialogType === 'add' ? '提交' : '保存' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.data-management {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #1e40af;
}

.table-container {
  margin-bottom: 20px;
}

.edit-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  margin-top: 16px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pending-card {
  margin-top: 20px;
}

.operation-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.operation-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
}

.operation-data {
  font-family: monospace;
  font-size: 12px;
  color: #475569;
  white-space: pre-wrap;
  word-break: break-all;
}

.readonly-field .el-input,
.readonly-field .el-input-number,
.readonly-field .el-select {
  border-color: #f56c6c !important;
  box-shadow: 0 0 0 2px #f56c6c22;
}

.db-cards-row {
  /* ...existing code... */
}
.filter-bar {
  margin-bottom: 18px;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 18px 24px;
  position: relative;
  z-index: 1;
  background: #f6f8fa;
  border-radius: 12px;
  box-shadow: 0 2px 8px #2196f111;
}
.filter-bar .el-form-item {
  margin-bottom: 0 !important;
  min-width: 180px;
  max-width: 320px;
  position: relative;
  z-index: 2;
  background: transparent;
}
.filter-bar .el-slider {
  width: 160px !important;
  min-width: 120px;
  max-width: 180px;
  margin-left: 8px;
  margin-right: 8px;
  background: transparent;
  z-index: 3;
  border-radius: 8px;
  box-shadow: none;
}
.filter-dropdown-popper {
  max-height: 220px;
  overflow-y: auto;
  background: #f6f8fa !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 8px #2196f122 !important;
  z-index: 3000 !important;
}
.el-overlay, .el-popper, .el-select-dropdown {
  z-index: 3000 !important;
}
</style>
