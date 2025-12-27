<template>
  <div class="profile-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户ID">{{ userInfo.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag v-if="userInfo.role === 'admin'" type="danger">管理员</el-tag>
          <el-tag v-else-if="userInfo.role === 'data_manager'" type="warning">数据管理员</el-tag>
          <el-tag v-else type="info">普通用户</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userInfo.email }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userInfo.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="最后登录">{{ userInfo.lastLogin }}</el-descriptions-item>
      </el-descriptions>

      <div style="margin-top: 20px;">
        <el-button type="primary" @click="editProfile">编辑资料</el-button>
        <el-button @click="changePassword">修改密码</el-button>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" title="编辑个人信息" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" type="email" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { currentUser } from '../store/user'

const userInfo = ref({
  id: currentUser.value.id,
  username: currentUser.value.username,
  role: currentUser.value.role,
  email: currentUser.value.email,
  createdAt: '2025-12-12 10:00:00',
  lastLogin: '2025-12-12 15:30:00'
})

const dialogVisible = ref(false)
const form = ref({
  username: userInfo.value.username,
  email: userInfo.value.email
})

const editProfile = () => {
  form.value = {
    username: userInfo.value.username,
    email: userInfo.value.email
  }
  dialogVisible.value = true
}

const saveProfile = () => {
  userInfo.value.username = form.value.username
  userInfo.value.email = form.value.email
  dialogVisible.value = false
  ElMessage.success('保存成功')
}

const changePassword = () => {
  ElMessage.info('修改密码功能开发中')
}
</script>

<style scoped>
.profile-page {
  padding: 20px;
}

.card-header {
  font-weight: 600;
  font-size: 18px;
}
</style>