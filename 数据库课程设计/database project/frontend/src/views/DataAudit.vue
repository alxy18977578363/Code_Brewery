<template>
  <div class="data-audit">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据审核</span>
          <el-radio-group v-model="auditStatus">
            <el-radio-button label="pending">待审核</el-radio-button>
            <el-radio-button label="approved">已通过</el-radio-button>
            <el-radio-button label="rejected">已拒绝</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-table :data="auditList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="type" label="目标表" width="150" />
        <el-table-column prop="operationType" label="操作类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.operationType === '添加' ? 'success' : 'danger'" size="small">
              {{ scope.row.operationType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="submitter" label="提交人" width="120" />
        <el-table-column prop="submitTime" label="提交时间" width="180" />
        <el-table-column prop="content" label="操作内容" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.status === 'pending'" type="warning">待审核</el-tag>
            <el-tag v-else-if="scope.row.status === 'approved'" type="success">已通过</el-tag>
            <el-tag v-else type="danger">已拒绝</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button 
              v-if="scope.row.status === 'pending'" 
              size="small" 
              type="success" 
              @click="handleApprove(scope.row)"
            >
              通过
            </el-button>
            <el-button 
              v-if="scope.row.status === 'pending'" 
              size="small" 
              type="danger" 
              @click="handleReject(scope.row)"
            >
              拒绝
            </el-button>
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { approvalAPI } from '../api/index'
import { currentUser } from '../store/user'

const auditStatus = ref('pending')
const loading = ref(false)
const auditList = ref([])

// 表名映射
const tableNameMap = {
  'Radionuclide': '放射性核素表',
  'OceanCurrent': '洋流表',
  'RadioactiveSource': '放射源表',
  'CurrentSourceRelation': '洋流-放射源关系表',
  'Station': '监测站点表',
  'Sample': '样本表',
  'MeasurementRecord': '检测记录表',
  'UserRecordRelation': '用户记录关系表'
}

// 加载审批列表
const loadApprovals = async () => {
  loading.value = true
  try {
    const response = await approvalAPI.getPending()
    const data = response.data || []
    
    // 转换数据格式
    auditList.value = data.map(item => ({
      id: item.RequestID,
      requestUserID: item.RequestUserID,
      type: tableNameMap[item.TargetTable] || item.TargetTable,
      tableName: item.TargetTable,
      submitter: item.RequestUserName,
      submitTime: item.RequestTime,
      operationType: item.OperationType === 'Add' ? '添加' : '删除',
      content: formatOperationData(item.OperationData),
      rawData: item.OperationData,
      status: item.Status.toLowerCase()
    }))
    
    ElMessage.success(`加载了 ${auditList.value.length} 条待审批记录`)
  } catch (error) {
    console.error('加载审批列表失败:', error)
    ElMessage.error('加载审批列表失败')
    auditList.value = []
  } finally {
    loading.value = false
  }
}

// 格式化操作数据
const formatOperationData = (jsonStr) => {
  try {
    const data = JSON.parse(jsonStr)
    const keys = Object.keys(data)
    if (keys.length > 3) {
      const preview = keys.slice(0, 3).map(k => `${k}: ${data[k]}`).join(', ')
      return `${preview}...`
    }
    return keys.map(k => `${k}: ${data[k]}`).join(', ')
  } catch (e) {
    return jsonStr
  }
}

watch(auditStatus, (newVal) => {
  // 根据状态筛选（暂时只显示待审核）
  if (newVal === 'pending') {
    loadApprovals()
  }
})

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定通过该数据审核吗？<br/><br/>
      <strong>操作类型：</strong>${row.operationType}<br/>
      <strong>目标表：</strong>${row.type}<br/>
      <strong>提交人：</strong>${row.submitter}`,
      '审核通过',
      {
        confirmButtonText: '通过',
        cancelButtonText: '取消',
        type: 'success',
        dangerouslyUseHTMLString: true
      }
    )
    
    loading.value = true
    await approvalAPI.approve(row.id, {
      approverName: currentUser.value.username,
      approverId: currentUser.value.id
    })
    
    ElMessage.success('审核通过，操作已执行')
    await loadApprovals()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核失败:', error)
      const errorMsg = error.response?.data?.error || error.message || '未知错误'
      ElMessage.error({
        message: '审核失败: ' + errorMsg,
        duration: 5000,
        showClose: true
      })
    }
  } finally {
    loading.value = false
  }
}

const handleReject = async (row) => {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      `请输入拒绝原因：<br/><br/>
      <strong>操作类型：</strong>${row.operationType}<br/>
      <strong>目标表：</strong>${row.type}<br/>
      <strong>提交人：</strong>${row.submitter}`,
      '拒绝审核',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.+/,
        inputErrorMessage: '请输入拒绝原因',
        dangerouslyUseHTMLString: true
      }
    )
    
    loading.value = true
    await approvalAPI.reject(row.id, {
      approverName: currentUser.value.username,
      approverId: currentUser.value.id,
      comment: reason
    })
    
    ElMessage.success('已拒绝该审批请求')
    await loadApprovals()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝失败:', error)
      ElMessage.error('拒绝失败: ' + (error.message || '未知错误'))
    }
  } finally {
    loading.value = false
  }
}

const handleView = (row) => {
  try {
    const data = JSON.parse(row.rawData)
    const content = Object.entries(data)
      .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
      .join('<br/>')
    
    ElMessageBox.alert(
      `<div style="text-align: left;">
        <p><strong>操作类型：</strong>${row.operationType}</p>
        <p><strong>目标表：</strong>${row.type}</p>
        <p><strong>提交人：</strong>${row.submitter}</p>
        <p><strong>提交时间：</strong>${row.submitTime}</p>
        <hr/>
        <p><strong>操作数据：</strong></p>
        ${content}
      </div>`,
      '审批详情',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '关闭'
      }
    )
  } catch (e) {
    ElMessage.error('解析数据失败')
  }
}

// 初始化
onMounted(() => {
  loadApprovals()
})
</script>

<style scoped>
.data-audit {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>