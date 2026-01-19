<template>
  <div class="admin-container">
    <a-page-header title="管理后台" style="background: white; margin-bottom: 16px" />

    <div style="padding: 0 24px">
      <a-tabs v-model:activeKey="activeTab">
        <a-tab-pane key="stats" tab="系统统计">
          <a-row :gutter="16">
            <a-col :xs="24" :sm="12" :lg="6">
              <a-card>
                <a-statistic
                  title="总用户数"
                  :value="systemStats?.users?.total"
                  :prefix="() => h(UserOutlined)"
                />
              </a-card>
            </a-col>
            <a-col :xs="24" :sm="12" :lg="6">
              <a-card>
                <a-statistic
                  title="活跃用户"
                  :value="systemStats?.users?.active"
                  :prefix="() => h(CheckCircleOutlined)"
                />
              </a-card>
            </a-col>
            <a-col :xs="24" :sm="12" :lg="6">
              <a-card>
                <a-statistic
                  title="总帖子数"
                  :value="systemStats?.posts?.total"
                  :prefix="() => h(FileTextOutlined)"
                />
              </a-card>
            </a-col>
            <a-col :xs="24" :sm="12" :lg="6">
              <a-card>
                <a-statistic
                  title="待审核"
                  :value="systemStats?.posts?.pending"
                  :prefix="() => h(ClockCircleOutlined)"
                />
              </a-card>
            </a-col>
          </a-row>

          <a-card title="系统健康" style="margin-top: 16px">
            <a-descriptions bordered :column="2">
              <a-descriptions-item label="整体状态">
                <a-tag :color="health?.overall_status === 'healthy' ? 'green' : 'red'">
                  {{ health?.overall_status }}
                </a-tag>
              </a-descriptions-item>
              <a-descriptions-item label="MySQL">
                <a-tag :color="health?.components?.mysql?.status === 'healthy' ? 'green' : 'red'">
                  {{ health?.components?.mysql?.status }}
                </a-tag>
                {{ health?.components?.mysql?.latency_ms }}ms
              </a-descriptions-item>
              <a-descriptions-item label="MongoDB">
                <a-tag :color="health?.components?.mongodb?.status === 'healthy' ? 'green' : 'red'">
                  {{ health?.components?.mongodb?.status }}
                </a-tag>
                {{ health?.components?.mongodb?.latency_ms }}ms
              </a-descriptions-item>
              <a-descriptions-item label="Redis">
                <a-tag :color="health?.components?.redis?.status === 'healthy' ? 'green' : 'red'">
                  {{ health?.components?.redis?.status }}
                </a-tag>
                {{ health?.components?.redis?.latency_ms }}ms
              </a-descriptions-item>
              <a-descriptions-item label="磁盘使用">
                <a-progress
                  :percent="health?.components?.disk?.usage_percent"
                  :status="health?.components?.disk?.usage_percent > 80 ? 'exception' : 'normal'"
                />
              </a-descriptions-item>
            </a-descriptions>
          </a-card>
        </a-tab-pane>

        <a-tab-pane key="users" tab="用户管理">
          <a-table
            :columns="userColumns"
            :data-source="users"
            :loading="loadingUsers"
            :pagination="{ pageSize: 20 }"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'is_active'">
                <a-tag :color="record.is_active ? 'green' : 'red'">
                  {{ record.is_active ? '活跃' : '禁用' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'role'">
                <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">
                  {{ record.role }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-button
                  type="link"
                  :danger="record.is_active"
                  @click="toggleUserStatus(record.id, !record.is_active)"
                >
                  {{ record.is_active ? '禁用' : '启用' }}
                </a-button>
              </template>
            </template>
          </a-table>
        </a-tab-pane>

        <a-tab-pane key="moderation" tab="内容审核">
          <a-list
            :data-source="pendingPosts"
            :loading="loadingPosts"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <template #actions>
                  <a-button type="primary" @click="moderatePost(item.id, 'approved')">
                    通过
                  </a-button>
                  <a-button danger @click="moderatePost(item.id, 'rejected')">
                    拒绝
                  </a-button>
                </template>
                <a-list-item-meta>
                  <template #title>{{ item.username }}</template>
                  <template #description>{{ item.created_at }}</template>
                </a-list-item-meta>
                <div>{{ item.content }}</div>
              </a-list-item>
            </template>
          </a-list>
        </a-tab-pane>
      </a-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  CheckCircleOutlined,
  FileTextOutlined,
  ClockCircleOutlined
} from '@ant-design/icons-vue'
import axios from '@/utils/axios'

const activeTab = ref('stats')
const systemStats = ref<any>(null)
const health = ref<any>(null)
const users = ref<any[]>([])
const pendingPosts = ref<any[]>([])
const loadingUsers = ref(false)
const loadingPosts = ref(false)

const userColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id' },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '角色', dataIndex: 'role', key: 'role' },
  { title: '状态', dataIndex: 'is_active', key: 'is_active' },
  { title: '操作', key: 'action' }
]

onMounted(async () => {
  await loadSystemStats()
  await loadHealth()
})

async function loadSystemStats() {
  try {
    const response = await axios.get('/api/admin/stats')
    systemStats.value = response.data
  } catch (error) {
    message.error('加载统计数据失败')
  }
}

async function loadHealth() {
  try {
    const response = await axios.get('/api/admin/health')
    health.value = response.data
  } catch (error) {
    message.error('加载健康状态失败')
  }
}

async function loadUsers() {
  loadingUsers.value = true
  try {
    const response = await axios.get('/api/admin/users')
    users.value = response.data
  } catch (error) {
    message.error('加载用户列表失败')
  } finally {
    loadingUsers.value = false
  }
}

async function loadPendingPosts() {
  loadingPosts.value = true
  try {
    const response = await axios.get('/api/admin/posts/moderation', {
      params: { status: 'pending' }
    })
    pendingPosts.value = response.data
  } catch (error) {
    message.error('加载待审核内容失败')
  } finally {
    loadingPosts.value = false
  }
}

async function toggleUserStatus(userId: number, isActive: boolean) {
  try {
    await axios.put(`/api/admin/users/${userId}/status`, { is_active: isActive })
    message.success('操作成功')
    await loadUsers()
  } catch (error) {
    message.error('操作失败')
  }
}

async function moderatePost(postId: string, status: 'approved' | 'rejected') {
  try {
    await axios.put(`/api/admin/posts/${postId}/moderate`, {
      status,
      reason: status === 'approved' ? '内容符合规范' : '内容不符合规范'
    })
    message.success('审核成功')
    await loadPendingPosts()
  } catch (error) {
    message.error('审核失败')
  }
}

// Load data when tab changes
function handleTabChange(key: string) {
  if (key === 'users' && users.value.length === 0) {
    loadUsers()
  } else if (key === 'moderation' && pendingPosts.value.length === 0) {
    loadPendingPosts()
  }
}
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
