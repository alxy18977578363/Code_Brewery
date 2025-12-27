<!-- filepath: c:\Users\HS\Desktop\数据库\frontend\src\views\SampleManagement.vue -->
<template>
  <div class="sample-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>样本管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加样本
          </el-button>
        </div>
      </template>

      <el-table :data="samples" style="width: 100%" v-loading="loading">
        <el-table-column prop="SampleID" label="样本ID" width="100" />
        <el-table-column prop="SampleType" label="样本类型" width="150" />
        <el-table-column prop="SamplingTime" label="采样时间" width="180" />
        <el-table-column prop="SamplingDepth" label="采样深度(米)" width="120" />
        <el-table-column prop="LocationDescription" label="位置描述" width="200" />
        <el-table-column prop="StationID" label="站点ID" width="100" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="样本类型">
          <el-select v-model="form.SampleType" placeholder="请选择样本类型" style="width: 100%">
            <el-option label="生物样本" value="Biota" />
            <el-option label="海水" value="Seawater" />
            <el-option label="沉积物" value="Sediment" />
            <el-option label="悬浮物" value="Suspended Matter" />
          </el-select>
        </el-form-item>
        <el-form-item label="采样时间">
          <el-date-picker
            v-model="form.SamplingTime"
            type="datetime"
            placeholder="选择采样时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="采样深度(米)">
          <el-input v-model.number="form.SamplingDepth" type="number" />
        </el-form-item>
        <el-form-item label="位置描述">
          <el-input v-model="form.LocationDescription" type="textarea" />
        </el-form-item>
        <el-form-item label="站点ID">
          <el-input v-model.number="form.StationID" type="number" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { sampleAPI } from '../api'

const samples = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加样本')
const form = ref({
  SampleID: null,
  SampleType: '',
  SamplingTime: '',
  SamplingDepth: null,
  LocationDescription: '',
  StationID: null
})

const fetchSamples = async () => {
  loading.value = true
  try {
    const response = await sampleAPI.getAll()
    samples.value = response.data
  } catch (error) {
    ElMessage.error('获取样本列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加样本'
  form.value = {
    SampleID: null,
    SampleType: '',
    SamplingTime: '',
    SamplingDepth: null,
    LocationDescription: '',
    StationID: null
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑样本'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该样本吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await sampleAPI.delete(row.SampleID)
    ElMessage.success('删除成功')
    fetchSamples()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (form.value.SampleID) {
      await sampleAPI.update(form.value.SampleID, form.value)
      ElMessage.success('更新成功')
    } else {
      await sampleAPI.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchSamples()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchSamples()
})
</script>

<style scoped>
.sample-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>