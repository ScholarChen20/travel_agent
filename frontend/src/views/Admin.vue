<template>
  <div class="admin-layout">
    <a-layout class="admin-main">
      <a-layout-sider v-model:collapsed="collapsed" :trigger="null" collapsible theme="dark" :width="220">
        <div class="logo">
          <span v-if="!collapsed">🛠️ 管理后台</span>
          <span v-else>🛠️</span>
        </div>
        <a-menu
          v-model:selectedKeys="selectedKeys"
          theme="dark"
          mode="inline"
          @click="handleMenuClick"
        >
          <a-menu-item key="stats">
            <template #icon><DashboardOutlined /></template>
            <span>系统概览</span>
          </a-menu-item>
          <a-menu-item key="users">
            <template #icon><TeamOutlined /></template>
            <span>用户管理</span>
          </a-menu-item>
          <a-menu-item key="content">
            <template #icon><FileTextOutlined /></template>
            <span>内容审核</span>
          </a-menu-item>
          <a-menu-item key="settings">
            <template #icon><SettingOutlined /></template>
            <span>系统设置</span>
          </a-menu-item>
        </a-menu>
      </a-layout-sider>
      
      <a-layout>
        <a-layout-header class="admin-header">
          <div class="header-left">
            <MenuUnfoldOutlined
              v-if="collapsed"
              class="trigger"
              @click="collapsed = !collapsed"
            />
            <MenuFoldOutlined
              v-else
              class="trigger"
              @click="collapsed = !collapsed"
            />
          </div>
          <div class="header-right">
            <a-dropdown>
              <a class="user-dropdown" @click.prevent>
                <a-avatar size="small" style="background-color: #1890ff">
                  <template #icon><UserOutlined /></template>
                </a-avatar>
                <span class="username">管理员</span>
              </a>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="logout" @click="handleLogout">
                    <LogoutOutlined />
                    退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </a-layout-header>
        
        <a-layout-content class="admin-content">
          <div class="page-container">
            <!-- 系统概览 -->
            <div v-show="selectedKeys[0] === 'stats'">
              <div class="page-header">
                <h2 class="page-title">系统概览</h2>
                <p class="page-desc">实时监控系统运行状态和数据统计</p>
              </div>
              
              <!-- 统计卡片 -->
              <a-row :gutter="[16, 16]" class="stats-row">
                <a-col :xs="24" :sm="12" :lg="6">
                  <div class="stat-card stat-card-blue">
                    <div class="stat-icon">
                      <UserOutlined />
                    </div>
                    <div class="stat-content">
                      <div class="stat-label">总用户数</div>
                      <div class="stat-value">{{ systemStats?.users?.total || 0 }}</div>
                    </div>
                  </div>
                </a-col>
                <a-col :xs="24" :sm="12" :lg="6">
                  <div class="stat-card stat-card-green">
                    <div class="stat-icon">
                      <CheckCircleOutlined />
                    </div>
                    <div class="stat-content">
                      <div class="stat-label">活跃用户</div>
                      <div class="stat-value">{{ systemStats?.users?.active || 0 }}</div>
                    </div>
                  </div>
                </a-col>
                <a-col :xs="24" :sm="12" :lg="6">
                  <div class="stat-card stat-card-orange">
                    <div class="stat-icon">
                      <FileTextOutlined />
                    </div>
                    <div class="stat-content">
                      <div class="stat-label">总帖子数</div>
                      <div class="stat-value">{{ systemStats?.posts?.total || 0 }}</div>
                    </div>
                  </div>
                </a-col>
                <a-col :xs="24" :sm="12" :lg="6">
                  <div class="stat-card stat-card-red">
                    <div class="stat-icon">
                      <ClockCircleOutlined />
                    </div>
                    <div class="stat-content">
                      <div class="stat-label">待审核</div>
                      <div class="stat-value">{{ systemStats?.posts?.pending || 0 }}</div>
                    </div>
                  </div>
                </a-col>
              </a-row>

              <!-- 系统健康状态 -->
              <a-card class="health-card" :bordered="false">
                <template #title>
                  <div class="card-title">
                    <HeartOutlined />
                    <span>系统健康状态</span>
                  </div>
                </template>
                <a-row :gutter="[16, 16]">
                  <a-col :xs="24" :sm="12" :lg="8">
                    <div class="health-item">
                      <div class="health-header">
                        <span class="health-label">整体状态</span>
                        <a-tag :color="health?.overall_status === 'healthy' ? 'success' : 'error'">
                          {{ health?.overall_status === 'healthy' ? '正常' : '异常' }}
                        </a-tag>
                      </div>
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12" :lg="8">
                    <div class="health-item">
                      <div class="health-header">
                        <span class="health-label">MySQL</span>
                        <a-tag :color="health?.components?.mysql?.status === 'healthy' ? 'success' : 'error'">
                          {{ health?.components?.mysql?.status === 'healthy' ? '正常' : '异常' }}
                        </a-tag>
                      </div>
                      <div class="health-latency">
                        延迟: {{ health?.components?.mysql?.latency_ms || 0 }}ms
                      </div>
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12" :lg="8">
                    <div class="health-item">
                      <div class="health-header">
                        <span class="health-label">MongoDB</span>
                        <a-tag :color="health?.components?.mongodb?.status === 'healthy' ? 'success' : 'error'">
                          {{ health?.components?.mongodb?.status === 'healthy' ? '正常' : '异常' }}
                        </a-tag>
                      </div>
                      <div class="health-latency">
                        延迟: {{ health?.components?.mongodb?.latency_ms || 0 }}ms
                      </div>
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12" :lg="8">
                    <div class="health-item">
                      <div class="health-header">
                        <span class="health-label">Redis</span>
                        <a-tag :color="health?.components?.redis?.status === 'healthy' ? 'success' : 'error'">
                          {{ health?.components?.redis?.status === 'healthy' ? '正常' : '异常' }}
                        </a-tag>
                      </div>
                      <div class="health-latency">
                        延迟: {{ health?.components?.redis?.latency_ms || 0 }}ms
                      </div>
                    </div>
                  </a-col>
                  <a-col :xs="24" :sm="12" :lg="8">
                    <div class="health-item">
                      <div class="health-header">
                        <span class="health-label">磁盘使用</span>
                      </div>
                      <a-progress
                        :percent="health?.components?.disk?.usage_percent || 0"
                        :status="(health?.components?.disk?.usage_percent || 0) > 80 ? 'exception' : 'normal'"
                        :stroke-color="getDiskColor(health?.components?.disk?.usage_percent)"
                      />
                    </div>
                  </a-col>
                </a-row>
              </a-card>
            </div>

            <!-- 用户管理 -->
            <div v-show="selectedKeys[0] === 'users'">
              <div class="page-header">
                <h2 class="page-title">用户管理</h2>
                <p class="page-desc">管理平台用户账号和权限</p>
              </div>
              <a-card :bordered="false" class="table-card">
                <a-table
                  :columns="userColumns"
                  :data-source="users"
                  :loading="loadingUsers"
                  :pagination="{ pageSize: 20, showTotal: (total: number) => `共 ${total} 条` }"
                  row-key="id"
                >
                  <template #bodyCell="{ column, record }">
                    <template v-if="column.key === 'is_active'">
                      <a-switch
                        :checked="record.is_active"
                        @change="(checked: boolean) => toggleUserStatus(record.id, checked)"
                        checked-children="启用"
                        un-checked-children="禁用"
                      />
                    </template>
                    <template v-if="column.key === 'role'">
                      <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">
                        {{ record.role === 'admin' ? '管理员' : '普通用户' }}
                      </a-tag>
                    </template>
                    <template v-if="column.key === 'created_at'">
                      {{ formatDate(record.created_at) }}
                    </template>
                  </template>
                </a-table>
              </a-card>
            </div>

            <!-- 内容审核 -->
            <div v-show="selectedKeys[0] === 'content'">
              <div class="page-header">
                <h2 class="page-title">内容审核</h2>
                <p class="page-desc">审核用户发布的待审内容</p>
              </div>
              <a-card :bordered="false" class="table-card">
                <a-list
                  :data-source="pendingPosts"
                  :loading="loadingPosts"
                >
                  <template #renderItem="{ item }">
                    <a-list-item class="post-item">
                      <a-list-item-meta>
                        <template #avatar>
                          <a-avatar style="background-color: #1890ff">
                            {{ item.username?.charAt(0)?.toUpperCase() }}
                          </a-avatar>
                        </template>
                        <template #title>
                          <span class="post-author">{{ item.username }}</span>
                          <span class="post-time">{{ formatDate(item.created_at) }}</span>
                        </template>
                      </a-list-item-meta>
                      <div class="post-content">{{ item.content || item.text }}</div>
                      <template #actions>
                        <a-button type="primary" size="small" @click="moderatePost(item.id || item.post_id, 'approved')">
                          <CheckOutlined /> 通过
                        </a-button>
                        <a-button danger size="small" @click="moderatePost(item.id || item.post_id, 'rejected')">
                          <CloseOutlined /> 拒绝
                        </a-button>
                      </template>
                    </a-list-item>
                  </template>
                  <template #empty>
                    <a-empty description="暂无待审核内容" />
                  </template>
                </a-list>
              </a-card>
            </div>

            <!-- 系统设置 -->
            <div v-show="selectedKeys[0] === 'settings'">
              <div class="page-header">
                <h2 class="page-title">系统设置</h2>
                <p class="page-desc">配置系统参数和功能</p>
              </div>
              <a-card :bordered="false">
                <a-result
                  status="info"
                  title="系统设置"
                  sub-title="该功能正在开发中..."
                >
                  <template #extra>
                    <a-button type="primary">敬请期待</a-button>
                  </template>
                </a-result>
              </a-card>
            </div>
          </div>
        </a-layout-content>
      </a-layout>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  DashboardOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  LogoutOutlined,
  HeartOutlined,
  CheckOutlined,
  CloseOutlined
} from '@ant-design/icons-vue'
import axios from '@/utils/axios'

const router = useRouter()
const collapsed = ref(false)
const selectedKeys = ref<string[]>(['stats'])
const systemStats = ref<any>(null)
const health = ref<any>(null)
const users = ref<any[]>([])
const pendingPosts = ref<any[]>([])
const loadingUsers = ref(false)
const loadingPosts = ref(false)

const userColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '角色', dataIndex: 'role', key: 'role', width: 100 },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 100 },
  { title: '注册时间', dataIndex: 'created_at', key: 'created_at' }
]

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getDiskColor(percent?: number) {
  if (!percent) return '#52c41a'
  if (percent > 80) return '#ff4d4f'
  if (percent > 60) return '#faad14'
  return '#52c41a'
}

function handleMenuClick({ key }: { key: string }) {
  if (key === 'users') {
    loadUsers(true)
  } else if (key === 'content') {
    loadPendingPosts(true)
  }
}

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

onMounted(async () => {
  await loadSystemStats()
  await loadHealth()
})

async function loadSystemStats() {
  try {
    const response = await axios.get('/admin/stats')
    systemStats.value = response.data.data
  } catch (error) {
    message.error('加载统计数据失败')
  }
}

async function loadHealth() {
  try {
    const response = await axios.get('/admin/health')
    health.value = response.data.data
  } catch (error) {
    message.error('加载健康状态失败')
  }
}

async function loadUsers(force = false) {
  if (users.value.length > 0 && !force) return
  loadingUsers.value = true
  try {
    const response = await axios.get('/admin/users')
    users.value = response.data.data?.users || []
  } catch (error) {
    message.error('加载用户列表失败')
  } finally {
    loadingUsers.value = false
  }
}

async function loadPendingPosts(force = false) {
  if (pendingPosts.value.length > 0 && !force) return
  loadingPosts.value = true
  try {
    const response = await axios.get('/admin/posts/moderation', {
      params: { status: 'pending' }
    })
    pendingPosts.value = response.data.data?.posts || []
  } catch (error) {
    message.error('加载待审核内容失败')
  } finally {
    loadingPosts.value = false
  }
}

async function toggleUserStatus(userId: number, isActive: boolean) {
  try {
    await axios.put(`/admin/users/${userId}/status`, { is_active: isActive })
    message.success(isActive ? '用户已启用' : '用户已禁用')
    await loadUsers(true)
  } catch (error) {
    message.error('操作失败')
  }
}

async function moderatePost(postId: string, status: 'approved' | 'rejected') {
  try {
    await axios.put(`/admin/posts/${postId}/moderate`, {
      status,
      reason: status === 'approved' ? '内容符合规范' : '内容不符合规范'
    })
    message.success(status === 'approved' ? '审核通过' : '已拒绝')
    await loadPendingPosts(true)
  } catch (error) {
    message.error('审核失败')
  }
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.admin-main {
  min-height: 100vh;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.admin-header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  margin-left: 8px;
}

.admin-content {
  margin: 16px;
  min-height: calc(100vh - 64px - 32px);
}

.page-container {
  background: transparent;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  margin: 0;
}

.page-desc {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  margin: 8px 0 0;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-card-blue .stat-icon {
  background: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.stat-card-green .stat-icon {
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.stat-card-orange .stat-icon {
  background: rgba(250, 173, 20, 0.1);
  color: #faad14;
}

.stat-card-red .stat-icon {
  background: rgba(255, 77, 79, 0.1);
  color: #ff4d4f;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
}

.health-card {
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.health-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
}

.health-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.health-label {
  font-weight: 500;
}

.health-latency {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.post-item {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 16px;
}

.post-author {
  font-weight: 500;
  margin-right: 8px;
}

.post-time {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.post-content {
  margin: 12px 0;
  color: rgba(0, 0, 0, 0.65);
  line-height: 1.6;
}

:deep(.ant-layout-sider) {
  background: #001529;
}

:deep(.ant-menu-dark) {
  background: #001529;
}

:deep(.ant-menu-dark .ant-menu-item-selected) {
  background: #1890ff;
}
</style>
