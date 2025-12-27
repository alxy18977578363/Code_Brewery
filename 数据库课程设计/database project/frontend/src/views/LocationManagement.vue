<!-- filepath: c:\Users\HS\Desktop\数据库\frontend\src\views\LocationManagement.vue -->
<template>
  <div class="location-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采样地点管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加地点
          </el-button>
        </div>
      </template>

      <el-table :data="locations" style="width: 100%" v-loading="loading">
        <el-table-column prop="LocationID" label="地点ID" width="100" />
        <el-table-column prop="LocationName" label="地点名称" width="200" />
        <el-table-column prop="Longitude" label="经度" width="120" />
        <el-table-column prop="Latitude" label="纬度" width="120" />
        <el-table-column prop="RegionCode" label="区域编码" width="120" />
        <el-table-column prop="LocationType" label="地点类型" width="120" />
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
        <el-form-item label="地点名称">
          <el-input v-model="form.LocationName" />
        </el-form-item>
        <el-form-item label="经度">
          <el-input v-model.number="form.Longitude" type="number" />
        </el-form-item>
        <el-form-item label="纬度">
          <el-input v-model.number="form.Latitude" type="number" />
        </el-form-item>
        <el-form-item label="区域编码">
          <el-input v-model="form.RegionCode" />
        </el-form-item>
        <el-form-item label="地点类型">
          <el-input v-model="form.LocationType" />
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
import { locationAPI } from '../api'

const locations = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加地点')
const form = ref({
  LocationID: null,
  LocationName: '',
  Longitude: null,
  Latitude: null,
  RegionCode: '',
  LocationType: ''
})

const fetchLocations = async () => {
  loading.value = true
  try {
    const response = await locationAPI.getAll()
    locations.value = response.data
  } catch (error) {
    ElMessage.error('获取地点列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加地点'
  form.value = {
    LocationID: null,
    LocationName: '',
    Longitude: null,
    Latitude: null,
    RegionCode: '',
    LocationType: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑地点'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该地点吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await locationAPI.delete(row.LocationID)
    ElMessage.success('删除成功')
    fetchLocations()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (form.value.LocationID) {
      await locationAPI.update(form.value.LocationID, form.value)
      ElMessage.success('更新成功')
    } else {
      await locationAPI.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchLocations()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchLocations()
})
</script>

<style scoped>
.location-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>