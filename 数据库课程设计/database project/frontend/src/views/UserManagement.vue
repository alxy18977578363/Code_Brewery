<!-- filepath: c:\Users\HS\Desktop\数据库\frontend\src\views\UserManagement.vue -->
<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchText"
              placeholder="搜索用户名或邮箱"
              style="width: 240px; margin-right: 12px;"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              添加用户
            </el-button>
          </div>
        </div>
      </template>

      <!-- 角色比例图和筛选按钮 -->
      <div style="display: flex; align-items: center; gap: 32px; margin-bottom: 18px;">
        <UserRolePie :data="rolePieData" style="width: 320px; height: 220px;" />
        <div>
          <el-button-group>
            <el-button :type="roleFilter === '' ? 'primary' : 'default'" @click="roleFilter = ''">全部</el-button>
            <el-button :type="roleFilter === 'Admin' ? 'danger' : 'default'" @click="roleFilter = 'Admin'">管理员</el-button>
            <el-button :type="roleFilter === 'DataManager' ? 'warning' : 'default'" @click="roleFilter = 'DataManager'">数据管理员</el-button>
            <el-button :type="roleFilter === 'Viewer' ? 'info' : 'default'" @click="roleFilter = 'Viewer'">普通用户</el-button>
          </el-button-group>
        </div>
      </div>

      <el-table :data="filteredUsers" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="UserID" label="用户ID" width="100" />
        <el-table-column prop="Username" label="用户名" width="150">
          <template #default="scope">
            <div style="display: flex; align-items: center; gap: 12px; min-width: 120px;">
              <el-avatar :size="32" v-if="scope.row.Avatar" :src="scope.row.Avatar" style="flex-shrink: 0; box-shadow: 0 2px 8px #764ba233;" />
              <el-avatar v-else :size="32" style="flex-shrink: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; font-weight: bold; box-shadow: 0 2px 8px #764ba233;">
                {{ scope.row.Username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 120px; display: inline-block;">{{ scope.row.Username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="Role" label="角色" width="180">
          <template #default="scope">
            <el-tag v-if="scope.row.Role === 'Admin'" type="danger" effect="dark" size="large">
              <el-icon style="margin-right: 4px;"><Star /></el-icon>
              管理员
            </el-tag>
            <el-tag v-else-if="scope.row.Role === 'DataManager'" type="warning" effect="dark" size="large">
              <el-icon style="margin-right: 4px;"><Files /></el-icon>
              数据管理员
            </el-tag>
            <el-tag v-else type="info" effect="plain" size="large">
              <el-icon style="margin-right: 4px;"><User /></el-icon>
              普通用户
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="Email" label="邮箱" min-width="200">
          <template #default="scope">
            <div style="display: flex; align-items: center; gap: 6px; color: #64748b;">
              <el-icon><Message /></el-icon>
              <span>{{ scope.row.Email }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="CreatedAt" label="注册时间" width="180">
          <template #default="scope">
            <div style="display: flex; align-items: center; gap: 6px; color: #64748b;">
              <el-icon><Clock /></el-icon>
              <span>{{ scope.row.CreatedAt }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" link @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="users.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="Username">
          <el-input v-model="form.Username" placeholder="请输入用户名" :disabled="dialogTitle === '编辑用户'">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="角色" prop="Role">
          <el-select v-model="form.Role" placeholder="请选择角色" style="width: 100%;">
            <el-option label="管理员" value="Admin">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>管理员</span>
                <el-icon color="#f56c6c"><Star /></el-icon>
              </div>
            </el-option>
            <el-option label="数据管理员" value="DataManager">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>数据管理员</span>
                <el-icon color="#e6a23c"><Files /></el-icon>
              </div>
            </el-option>
            <el-option label="普通用户" value="Viewer">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>普通用户</span>
                <el-icon color="#909399"><User /></el-icon>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱" prop="Email">
          <el-input v-model="form.Email" type="email" placeholder="请输入邮箱">
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">
          <el-icon><Close /></el-icon>
          取消
        </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          <el-icon><Check /></el-icon>
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userAPI } from '../api'
import UserRolePie from '../components/UserRolePie.vue'

const users = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('添加用户')
const submitting = ref(false)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const formRef = ref(null)
const roleFilter = ref('')
const rolePieData = computed(() => {
  const counts = { Admin: 0, DataManager: 0, Viewer: 0 }
  users.value.forEach(u => {
    if (u.Role === 'Admin') counts.Admin++
    else if (u.Role === 'DataManager') counts.DataManager++
    else counts.Viewer++
  })
  return [
    { name: '管理员', value: counts.Admin },
    { name: '数据管理员', value: counts.DataManager },
    { name: '普通用户', value: counts.Viewer }
  ]
})

const filteredUsers = computed(() => {
  let filtered = users.value
  if (roleFilter.value) {
    filtered = filtered.filter(u => u.Role === roleFilter.value)
  }
  if (searchText.value) {
    const kw = searchText.value.toLowerCase()
    filtered = filtered.filter(user =>
      user.Username.toLowerCase().includes(kw) ||
      user.Email.toLowerCase().includes(kw)
    )
  }
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const rules = {
  Username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  Role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  Email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const handleSearch = () => {
  currentPage.value = 1
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await userAPI.getAll()
    users.value = response.data.data || []
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '添加用户'
  form.value = {
    UserID: null,
    Username: '',
    Role: '',
    Email: '',
    CreatedAt: new Date().toISOString()
  }
  if (formRef.value) {
    formRef.value.clearValidate()
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑用户'
  form.value = { ...row }
  if (formRef.value) {
    formRef.value.clearValidate()
  }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.Username}" 吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    await userAPI.delete(row.UserID)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (form.value.UserID) {
        await userAPI.update(form.value.UserID, form.value)
        ElMessage.success('更新成功')
      } else {
        await userAPI.create(form.value)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      fetchUsers()
    } catch (error) {
      ElMessage.error('操作失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table__header) {
  font-weight: 600;
}
</style>