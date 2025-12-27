<!-- filepath: c:\Users\HS\Desktop\数据库\frontend\src\views\MeasurementManagement.vue -->
<template>
  <div class="measurement-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测量记录管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加记录
          </el-button>
        </div>
      </template>

      <el-table :data="measurements" style="width: 100%" v-loading="loading">
        <el-table-column prop="RecordID" label="记录ID" width="100" />
        <el-table-column prop="SampleID" label="样本ID" width="100" />
        <el-table-column prop="NuclideID" label="核素ID" width="100" />
        <el-table-column prop="Activity" label="活度" width="120" />
        <el-table-column prop="Uncertainty" label="不确定度" width="120" />
        <el-table-column prop="Unit" label="单位" width="100" />
        <el-table-column prop="MeasurementType" label="测量类型" width="120" />
        <el-table-column prop="TestingOrganization" label="检测机构" width="150" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="样本ID">
          <el-input v-model.number="form.SampleID" type="number" />
        </el-form-item>
        <el-form-item label="核素ID">
          <el-input v-model.number="form.NuclideID" type="number" />
        </el-form-item>
        <el-form-item label="活度">
          <el-input v-model.number="form.Activity" type="number" step="0.000000001" />
        </el-form-item>
        <el-form-item label="不确定度">
          <el-input v-model.number="form.Uncertainty" type="number" step="0.000000001" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="form.Unit" placeholder="如 Bq/kg, Bq/L" />
        </el-form-item>
        <el-form-item label="测量类型">
          <el-input v-model="form.MeasurementType" placeholder="如 γ能谱、液闪" />
        </el-form-item>
        <el-form-item label="检测机构">
          <el-input v-model="form.TestingOrganization" />
        </el-form-item>
        <el-form-item label="报告编号">
          <el-input v-model="form.ReportNumber" />
        </el-form-item>
        <el-form-item label="完成时间">
          <el-date-picker
            v-model="form.CompletionTime"
            type="datetime"
            placeholder="选择完成时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
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
import { measurementAPI } from '../api'

const measurements = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加记录')
const form = ref({
  RecordID: null,
  SampleID: null,
  NuclideID: null,
  Activity: null,
  Uncertainty: null,
  Unit: 'Bq/kg',
  MeasurementType: '',
  TestingOrganization: '',
  ReportNumber: '',
  CompletionTime: ''
})

const fetchMeasurements = async () => {
  loading.value = true
  try {
    const response = await measurementAPI.getAll()
    measurements.value = response.data
  } catch (error) {
    ElMessage.error('获取测量记录失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加记录'
  form.value = {
    RecordID: null,
    SampleID: null,
    NuclideID: null,
    Activity: null,
    Uncertainty: null,
    Unit: 'Bq/kg',
    MeasurementType: '',
    TestingOrganization: '',
    ReportNumber: '',
    CompletionTime: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑记录'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该记录吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await measurementAPI.delete(row.RecordID)
    ElMessage.success('删除成功')
    fetchMeasurements()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (form.value.RecordID) {
      await measurementAPI.update(form.value.RecordID, form.value)
      ElMessage.success('更新成功')
    } else {
      await measurementAPI.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchMeasurements()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchMeasurements()
})
</script>

<style scoped>
.measurement-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>