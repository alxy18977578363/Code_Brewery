<template>
  <div class="info-center">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>通知中心</span>
          </template>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="系统通知" name="system">
              <el-timeline>
                <el-timeline-item
                  v-for="notice in systemNotices"
                  :key="notice.id"
                  :timestamp="notice.time"
                  placement="top"
                >
                  <el-card>
                    <h4>{{ notice.title }}</h4>
                    <p>{{ notice.content }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
            
            <el-tab-pane label="数据更新" name="data">
              <el-timeline>
                <el-timeline-item
                  v-for="update in dataUpdates"
                  :key="update.id"
                  :timestamp="update.time"
                  placement="top"
                >
                  <el-card>
                    <h4>{{ update.title }}</h4>
                    <p>{{ update.content }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
            
            <el-tab-pane label="我的消息" name="message">
              <el-timeline>
                <el-timeline-item
                  v-for="msg in messages"
                  :key="msg.id"
                  :timestamp="msg.time"
                  placement="top"
                >
                  <el-card>
                    <h4>{{ msg.title }}</h4>
                    <p>{{ msg.content }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeTab = ref('system')

const systemNotices = ref([
  {
    id: 1,
    title: '系统维护通知',
    content: '系统将于本周六凌晨2点进行维护，预计持续2小时',
    time: '2025-11-20 10:02'
  },
  {
    id: 2,
    title: '新功能上线',
    content: '数据可视化模块已上线，欢迎使用',
    time: '2025-11-30 15:30'
  }
])

const dataUpdates = ref([
  {
    id: 1,
    title: '样本数据更新',
    content: '新增100条海洋样本数据',
    time: '2025-12-10 14:25'
  },
  {
    id: 2,
    title: '测量记录更新',
    content: '更新了50条测量记录',
    time: '2025-12-12 09:36'
  }
])

const messages = ref([
  {
    id: 1,
    title: '审核通过',
    content: '您提交的样本数据已通过审核',
    time: '2025-12-18 11:32'
  }
])
</script>

<style scoped>
.info-center {
  padding: 20px;
}
</style>