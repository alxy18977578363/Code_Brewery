<!-- filepath: c:\Users\HS\Desktop\数据库\frontend\src\views\NuclideManagement.vue -->
<template>
  <div class="nuclide-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>核素信息管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加核素
          </el-button>
        </div>
      </template>

      <el-table :data="nuclides" style="width: 100%" v-loading="loading">
        <el-table-column prop="NuclideID" label="核素ID" width="100" />
        <el-table-column prop="Name" label="核素名称" width="150" />
        <el-table-column prop="Symbol" label="符号" width="100" />
        <el-table-column prop="HalfLife" label="半衰期" width="150" />
        <el-table-column prop="RadioactiveType" label="放射性类型" width="120" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="核素名称">
          <el-input v-model="form.Name" />
        </el-form-item>
        <el-form-item label="符号">
          <el-input v-model="form.Symbol" placeholder="如 Cs-137" />
        </el-form-item>
        <el-form-item label="半衰期">
          <el-input v-model="form.HalfLife" placeholder="如 30.17年" />
        </el-form-item>
        <el-form-item label="放射性类型">
          <el-select v-model="form.RadioactiveType" placeholder="请选择" style="width: 100%">
            <el-option label="α" value="α" />
            <el-option label="β" value="β" />
            <el-option label="γ" value="γ" />
            <el-option label="α、β" value="α、β" />
            <el-option label="β、γ" value="β、γ" />
          </el-select>
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
import { nuclideAPI } from '../api'

const nuclides = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加核素')
const form = ref({
  NuclideID: null,
  Name: '',
  Symbol: '',
  HalfLife: '',
  RadioactiveType: ''
})

const fetchNuclides = async () => {
  loading.value = true
  try {
    const response = await nuclideAPI.getAll()
    nuclides.value = response.data
  } catch (error) {
    ElMessage.error('获取核素列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加核素'
  form.value = {
    NuclideID: null,
    Name: '',
    Symbol: '',
    HalfLife: '',
    RadioactiveType: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑核素'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该核素吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await nuclideAPI.delete(row.NuclideID)
    ElMessage.success('删除成功')
    fetchNuclides()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (form.value.NuclideID) {
      await nuclideAPI.update(form.value.NuclideID, form.value)
      ElMessage.success('更新成功')
    } else {
      await nuclideAPI.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchNuclides()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchNuclides()
})
</script>

<style scoped>
.nuclide-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>