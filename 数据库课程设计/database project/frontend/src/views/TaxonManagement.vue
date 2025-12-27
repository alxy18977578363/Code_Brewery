<!-- filepath: c:\Users\HS\Desktop\数据库\frontend\src\views\TaxonManagement.vue -->
<template>
  <div class="taxon-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>物种信息管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加物种
          </el-button>
        </div>
      </template>

      <el-table :data="taxons" style="width: 100%" v-loading="loading">
        <el-table-column prop="TaxonID" label="物种ID" width="100" />
        <el-table-column prop="TaxonName" label="物种名称" width="200" />
        <el-table-column prop="ClassificationLevel" label="分类等级" width="120" />
        <el-table-column prop="BiologicalGroup" label="生物群组" width="150" />
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
        <el-form-item label="物种名称">
          <el-input v-model="form.TaxonName" />
        </el-form-item>
        <el-form-item label="分类等级">
          <el-input v-model.number="form.ClassificationLevel" type="number" />
        </el-form-item>
        <el-form-item label="生物群组">
          <el-input v-model="form.BiologicalGroup" />
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
import { taxonAPI } from '../api'

const taxons = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加物种')
const form = ref({
  TaxonID: null,
  TaxonName: '',
  ClassificationLevel: null,
  BiologicalGroup: ''
})

const fetchTaxons = async () => {
  loading.value = true
  try {
    const response = await taxonAPI.getAll()
    taxons.value = response.data
  } catch (error) {
    ElMessage.error('获取物种列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加物种'
  form.value = {
    TaxonID: null,
    TaxonName: '',
    ClassificationLevel: null,
    BiologicalGroup: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑物种'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该物种吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await taxonAPI.delete(row.TaxonID)
    ElMessage.success('删除成功')
    fetchTaxons()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (form.value.TaxonID) {
      await taxonAPI.update(form.value.TaxonID, form.value)
      ElMessage.success('更新成功')
    } else {
      await taxonAPI.create(form.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchTaxons()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchTaxons()
})
</script>

<style scoped>
.taxon-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>