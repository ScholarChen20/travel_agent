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
          <a-menu-item key="analytics">
            <template #icon><BarChartOutlined /></template>
            <span>数据可视化</span>
          </a-menu-item>
          <a-menu-item key="users">
            <template #icon><TeamOutlined /></template>
            <span>用户管理</span>
          </a-menu-item>
          <a-menu-item key="comments">
            <template #icon><MessageOutlined /></template>
            <span>评论管理</span>
          </a-menu-item>
          <a-menu-item key="content">
            <template #icon><FileTextOutlined /></template>
            <span>内容审核</span>
          </a-menu-item>
          <a-menu-item key="logs">
            <template #icon><FileSearchOutlined /></template>
            <span>日志查看</span>
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

            <!-- 数据可视化 -->
            <div v-show="selectedKeys[0] === 'analytics'">
              <div class="page-header">
                <h2 class="page-title">数据可视化</h2>
                <p class="page-desc">平台数据统计分析图表</p>
              </div>
              
              <a-row :gutter="[16, 16]" class="charts-row">
                <a-col :xs="24" :lg="12">
                  <a-card class="chart-card" :bordered="false">
                    <template #title>
                      <div class="card-title">
                        <UserOutlined />
                        <span>用户注册趋势</span>
                      </div>
                    </template>
                    <div ref="userTrendChartRef" style="height: 320px"></div>
                  </a-card>
                </a-col>
                <a-col :xs="24" :lg="12">
                  <a-card class="chart-card" :bordered="false">
                    <template #title>
                      <div class="card-title">
                        <FileTextOutlined />
                        <span>帖子发布趋势</span>
                      </div>
                    </template>
                    <div ref="postTrendChartRef" style="height: 320px"></div>
                  </a-card>
                </a-col>
                <a-col :xs="24" :lg="12">
                  <a-card class="chart-card" :bordered="false">
                    <template #title>
                      <div class="card-title">
                        <CheckCircleOutlined />
                        <span>内容审核状态分布</span>
                      </div>
                    </template>
                    <div ref="moderationChartRef" style="height: 320px"></div>
                  </a-card>
                </a-col>
                <a-col :xs="24" :lg="12">
                  <a-card class="chart-card" :bordered="false">
                    <template #title>
                      <div class="card-title">
                        <TeamOutlined />
                        <span>内容类型分布</span>
                      </div>
                    </template>
                    <div ref="contentTypeChartRef" style="height: 320px"></div>
                  </a-card>
                </a-col>
                <a-col :xs="24">
                  <a-card class="chart-card" :bordered="false">
                    <template #title>
                      <div class="card-title">
                        <MessageOutlined />
                        <span>互动数据雷达图</span>
                      </div>
                    </template>
                    <div ref="interactionChartRef" style="height: 350px"></div>
                  </a-card>
                </a-col>
              </a-row>
            </div>

            <!-- 用户管理 -->
            <div v-show="selectedKeys[0] === 'users'">
              <div class="page-header">
                <h2 class="page-title">用户管理</h2>
                <p class="page-desc">管理平台用户账号和权限</p>
              </div>
              <a-card :bordered="false" class="table-card">
                <div class="search-bar">
                  <a-space wrap>
                    <a-input
                      v-model:value="userSearchKeyword"
                      placeholder="用户名"
                      style="width: 150px"
                      allow-clear
                    />
                    <a-input
                      v-model:value="userSearchEmail"
                      placeholder="邮箱"
                      style="width: 180px"
                      allow-clear
                    />
                    <a-select
                      v-model:value="userSearchRole"
                      placeholder="角色"
                      style="width: 100px"
                      allow-clear
                    >
                      <a-select-option value="admin">管理员</a-select-option>
                      <a-select-option value="user">普通用户</a-select-option>
                    </a-select>
                    <a-select
                      v-model:value="userSearchActive"
                      placeholder="状态"
                      style="width: 100px"
                      allow-clear
                    >
                      <a-select-option :value="true">启用</a-select-option>
                      <a-select-option :value="false">禁用</a-select-option>
                    </a-select>
                    <a-select
                      v-model:value="userSearchVerified"
                      placeholder="认证"
                      style="width: 100px"
                      allow-clear
                    >
                      <a-select-option :value="true">已认证</a-select-option>
                      <a-select-option :value="false">未认证</a-select-option>
                    </a-select>
                    <a-button type="primary" @click="searchUsers">
                      搜索
                    </a-button>
                    <a-button @click="clearUserSearch">
                      重置
                    </a-button>
                  </a-space>
                </div>
                <a-table
                  :columns="userColumns"
                  :data-source="users"
                  :loading="loadingUsers"
                  :pagination="{ pageSize: 10, showTotal: (total: number) => `共 ${total} 条` }"
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
                    <template v-if="column.key === 'is_verified'">
                      <a-tag :color="record.is_verified ? 'green' : 'default'">
                        {{ record.is_verified ? '已认证' : '未认证' }}
                      </a-tag>
                    </template>
                    <template v-if="column.key === 'feishu_open_id'">
                      {{ record.feishu_open_id || '-' }}
                    </template>
                    <template v-if="column.key === 'feishu_union_id'">
                      {{ record.feishu_union_id || '-' }}
                    </template>
                    <template v-if="column.key === 'last_login_at'">
                      {{ formatDate(record.last_login_at) }}
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
                <a-table
                  :columns="postColumns"
                  :data-source="pendingPosts"
                  :loading="loadingPosts"
                  :pagination="{ pageSize: 10, showTotal: (total: number) => `共 ${total} 条` }"
                  row-key="post_id"
                >
                  <template #bodyCell="{ column, record }">
                    <template v-if="column.key === 'title'">
                      <a-tooltip :title="record.title">
                        {{ record.title || '-' }}
                      </a-tooltip>
                    </template>
                    <template v-if="column.key === 'content'">
                      <a-tooltip :title="record.content">
                        {{ record.content || record.text || '-' }}
                      </a-tooltip>
                    </template>
                    <template v-if="column.key === 'created_at'">
                      {{ formatDate(record.created_at) }}
                    </template>
                    <template v-if="column.key === 'action'">
                      <a-space>
                        <a-button type="primary" size="small" @click="moderatePost(record.post_id || record.id, 'approved')">
                          <CheckOutlined /> 通过
                        </a-button>
                        <a-button danger size="small" @click="moderatePost(record.post_id || record.id, 'rejected')">
                          <CloseOutlined /> 拒绝
                        </a-button>
                      </a-space>
                    </template>
                  </template>
                  <template #empty>
                    <a-empty description="暂无待审核内容" />
                  </template>
                </a-table>
              </a-card>
            </div>

            <!-- 评论管理 -->
            <div v-show="selectedKeys[0] === 'comments'">
              <div class="page-header">
                <h2 class="page-title">评论管理</h2>
                <p class="page-desc">管理用户发布的评论，支持删除和搜索</p>
              </div>
              <a-card :bordered="false" class="table-card">
                <div class="search-bar">
                  <a-space wrap>
                    <a-input
                      v-model:value="commentSearchContent"
                      placeholder="评论内容"
                      style="width: 200px"
                      allow-clear
                    />
                    <a-input
                      v-model:value="commentSearchPostId"
                      placeholder="帖子ID"
                      style="width: 150px"
                      allow-clear
                    />
                    <a-input-number
                      v-model:value="commentSearchUserId"
                      placeholder="用户ID"
                      :min="1"
                      style="width: 120px"
                      allow-clear
                    />
                    <a-button type="primary" @click="searchComments">
                      搜索
                    </a-button>
                    <a-button @click="clearCommentSearch">
                      重置
                    </a-button>
                  </a-space>
                </div>
                <a-table
                  :columns="commentColumns"
                  :data-source="comments"
                  :loading="loadingComments"
                  :pagination="{ pageSize: 10, showTotal: (total: number) => `共 ${total} 条` }"
                  row-key="comment_id"
                >
                  <template #bodyCell="{ column, record }">
                    <template v-if="column.key === 'content'">
                      <div class="comment-content">{{ record.content }}</div>
                    </template>
                    <template v-if="column.key === 'created_at'">
                      {{ formatDate(record.created_at) }}
                    </template>
                    <template v-if="column.key === 'action'">
                      <a-popconfirm
                        title="确定删除这条评论吗？"
                        ok-text="确定"
                        cancel-text="取消"
                        @confirm="deleteComment(record.comment_id)"
                      >
                        <a-button type="text" danger>
                          <DeleteOutlined /> 删除
                        </a-button>
                      </a-popconfirm>
                    </template>
                  </template>
                </a-table>
              </a-card>
            </div>

            <!-- 日志查看 -->
            <div v-show="selectedKeys[0] === 'logs'">
              <div class="page-header">
                <h2 class="page-title">日志审查</h2>
                <p class="page-desc">查看系统操作审计日志</p>
              </div>
              <a-card :bordered="false" class="table-card">
                <div class="search-bar">
                  <a-space wrap>
                    <a-input
                      v-model:value="logSearchPath"
                      placeholder="接口路径"
                      style="width: 180px"
                      allow-clear
                    />
                    <a-select
                      v-model:value="logSearchMethod"
                      placeholder="HTTP方法"
                      style="width: 110px"
                      allow-clear
                    >
                      <a-select-option value="GET">GET</a-select-option>
                      <a-select-option value="POST">POST</a-select-option>
                      <a-select-option value="PUT">PUT</a-select-option>
                      <a-select-option value="DELETE">DELETE</a-select-option>
                    </a-select>
                    <a-select
                      v-model:value="logSearchStatus"
                      placeholder="状态码"
                      style="width: 100px"
                      allow-clear
                    >
                      <a-select-option :value="2">2xx 成功</a-select-option>
                      <a-select-option :value="4">4xx 客户端错误</a-select-option>
                      <a-select-option :value="5">5xx 服务端错误</a-select-option>
                    </a-select>
                    <a-input-number
                      v-model:value="logSearchUserId"
                      placeholder="用户ID"
                      :min="1"
                      style="width: 110px"
                      allow-clear
                    />
                    <a-select
                      v-model:value="logSearchAction"
                      placeholder="操作类型"
                      style="width: 110px"
                      allow-clear
                    >
                      <a-select-option v-for="opt in actionOptions" :key="opt.value" :value="opt.value">
                        {{ opt.label }}
                      </a-select-option>
                    </a-select>
                    <a-button type="primary" @click="searchAuditLogs">
                      搜索
                    </a-button>
                    <a-button @click="clearLogSearch">
                      重置
                    </a-button>
                  </a-space>
                </div>
                <a-table
                  :columns="logColumns"
                  :data-source="auditLogs"
                  :loading="loadingLogs"
                  :pagination="{ pageSize: 10, showTotal: (total: number) => `共 ${total} 条` }"
                  row-key="id"
                >
                  <template #bodyCell="{ column, record }">
                    <template v-if="column.key === 'method'">
                      <a-tag :color="getMethodColor(record.method)">{{ record.method || '-' }}</a-tag>
                    </template>
                    <template v-if="column.key === 'status_code'">
                      <a-tag :color="getStatusColor(record.status_code)">{{ record.status_code || '-' }}</a-tag>
                    </template>
                    <template v-if="column.key === 'action'">
                      <a-tag :color="getActionColor(record.action)">
                        {{ record.action }}
                      </a-tag>
                    </template>
                    <template v-if="column.key === 'ip_address'">
                      {{ record.ip_address || '-' }}
                    </template>
                    <template v-if="column.key === 'created_at'">
                      {{ formatDate(record.created_at) }}
                    </template>
                    <template v-if="column.key === 'details'">
                      <a-button type="link" size="small" @click="showLogDetails(record)">
                        查看
                      </a-button>
                    </template>
                  </template>
                </a-table>
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

  <a-modal
    v-model:open="logDetailsVisible"
    title="日志详情"
    :footer="null"
    width="760px"
  >
    <div v-if="currentLogDetails">
      <!-- 基础信息 -->
      <a-descriptions bordered :column="2" size="small">
        <a-descriptions-item label="日志ID" :span="1">{{ currentLogDetails.id }}</a-descriptions-item>
        <a-descriptions-item label="操作时间" :span="1">{{ formatDate(currentLogDetails.created_at) }}</a-descriptions-item>
        <a-descriptions-item label="用户名" :span="1">{{ currentLogDetails.username || '-' }}</a-descriptions-item>
        <a-descriptions-item label="用户ID" :span="1">{{ currentLogDetails.user_id || '-' }}</a-descriptions-item>
        <a-descriptions-item label="HTTP方法" :span="1">
          <a-tag :color="getMethodColor(currentLogDetails.method)">{{ currentLogDetails.method || '-' }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="状态码" :span="1">
          <a-tag :color="getStatusColor(currentLogDetails.status_code)">{{ currentLogDetails.status_code || '-' }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="接口路径" :span="2">
          <span style="color: #1890ff; word-break: break-all;">{{ currentLogDetails.path || '-' }}</span>
        </a-descriptions-item>
        <a-descriptions-item label="耗时" :span="1">{{ currentLogDetails.duration_ms != null ? currentLogDetails.duration_ms + ' ms' : '-' }}</a-descriptions-item>
        <a-descriptions-item label="IP地址" :span="1">{{ currentLogDetails.ip_address || '-' }}</a-descriptions-item>
        <a-descriptions-item label="User-Agent" :span="2">
          <div style="word-break: break-all; font-size: 12px; color: #666;">{{ currentLogDetails.user_agent || '-' }}</div>
        </a-descriptions-item>
      </a-descriptions>

      <!-- 请求体 -->
      <div class="detail-section" v-if="currentLogDetails.details?.request">
        <div class="detail-section-title">请求体</div>
        <pre class="detail-pre">{{ JSON.stringify(currentLogDetails.details.request, null, 2) }}</pre>
      </div>

      <!-- 响应结果 -->
      <div class="detail-section" v-if="currentLogDetails.details?.response">
        <div class="detail-section-title" :style="{ color: (currentLogDetails.status_code || 0) >= 400 ? '#ff4d4f' : '#52c41a' }">
          {{ (currentLogDetails.status_code || 0) >= 400 ? '响应错误' : '响应结果' }}
        </div>
        <pre class="detail-pre" :style="{ borderLeft: (currentLogDetails.status_code || 0) >= 400 ? '3px solid #ff4d4f' : '3px solid #52c41a' }">{{ JSON.stringify(currentLogDetails.details.response, null, 2) }}</pre>
      </div>

      <!-- 无详情兜底 -->
      <a-empty v-if="!currentLogDetails.details?.request && !currentLogDetails.details?.response"
        description="暂无请求/响应详情" style="padding: 24px 0;" />
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import * as echarts from 'echarts'
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
  CloseOutlined,
  MessageOutlined,
  FileSearchOutlined,
  DeleteOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue'
import axios from '@/utils/axios'

const router = useRouter()
const collapsed = ref(false)
const selectedKeys = ref<string[]>(['stats'])
const systemStats = ref<any>(null)
const health = ref<any>(null)
const visualizationData = ref<any>(null)
const users = ref<any[]>([])
const pendingPosts = ref<any[]>([])
const comments = ref<any[]>([])
const auditLogs = ref<any[]>([])

const userTrendChartRef = ref<HTMLDivElement>()
const postTrendChartRef = ref<HTMLDivElement>()
const moderationChartRef = ref<HTMLDivElement>()
const contentTypeChartRef = ref<HTMLDivElement>()
const interactionChartRef = ref<HTMLDivElement>()
const loadingUsers = ref(false)
const loadingPosts = ref(false)
const loadingComments = ref(false)
const loadingLogs = ref(false)

const userSearchKeyword = ref('')
const userSearchEmail = ref('')
const userSearchRole = ref<string | null>(null)
const userSearchActive = ref<boolean | null>(null)
const userSearchVerified = ref<boolean | null>(null)

const commentSearchContent = ref('')
const commentSearchPostId = ref('')
const commentSearchUserId = ref<number | null>(null)

const logSearchResourceId = ref('')
const logSearchUserId = ref<number | null>(null)
const logSearchAction = ref<string | null>(null)
const logSearchResource = ref('')
const logSearchMethod = ref<string | null>(null)
const logSearchPath = ref('')
const logSearchStatus = ref<number | null>(null)

const actionOptions = [
  { label: '创建', value: '创建' },
  { label: '更新', value: '更新' },
  { label: '删除', value: '删除' },
  { label: '激活', value: '激活' },
  { label: '禁用', value: '禁用' }
]

const userColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
  { title: '用户名', dataIndex: 'username', key: 'username', width: 100 },
  { title: '邮箱', dataIndex: 'email', key: 'email', width: 180 },
  { title: '角色', dataIndex: 'role', key: 'role', width: 80 },
  { title: '状态', dataIndex: 'is_active', key: 'is_active', width: 70 },
  { title: '认证', dataIndex: 'is_verified', key: 'is_verified', width: 70 },
  { title: '飞书OpenID', dataIndex: 'feishu_open_id', key: 'feishu_open_id', width: 150, ellipsis: true },
  { title: '飞书UnionID', dataIndex: 'feishu_union_id', key: 'feishu_union_id', width: 150, ellipsis: true },
  { title: '最后登录', dataIndex: 'last_login_at', key: 'last_login_at', width: 150 },
  { title: '注册时间', dataIndex: 'created_at', key: 'created_at', width: 150 }
]

const postColumns = [
  { title: 'ID', dataIndex: 'post_id', key: 'post_id', width: 180 },
  { title: '用户ID', dataIndex: 'user_id', key: 'user_id', width: 70 },
  { title: '标题', dataIndex: 'title', key: 'title', width: 180, ellipsis: true },
  { title: '内容', dataIndex: 'content', key: 'content', width: 200, ellipsis: true },
  { title: '位置', dataIndex: 'location', key: 'location', width: 100 },
  { title: '发布时间', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'action', width: 140 }
]

const commentColumns = [
  { title: 'ID', dataIndex: 'comment_id', key: 'comment_id', width: 180 },
  { title: '帖子ID', dataIndex: 'post_id', key: 'post_id', width: 140 },
  { title: '用户ID', dataIndex: 'user_id', key: 'user_id', width: 70 },
  { title: '评论内容', dataIndex: 'content', key: 'content', width: 250, ellipsis: true },
  { title: '点赞', dataIndex: 'like_count', key: 'like_count', width: 60 },
  { title: '发布时间', dataIndex: 'created_at', key: 'created_at', width: 150 },
  { title: '操作', key: 'action', width: 80 }
]

const logColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '用户名', dataIndex: 'username', key: 'username', width: 90 },
  { title: '用户ID', dataIndex: 'user_id', key: 'user_id', width: 60 },
  { title: 'HTTP方法', dataIndex: 'method', key: 'method', width: 85 },
  { title: '接口路径', dataIndex: 'path', key: 'path', width: 200, ellipsis: true },
  { title: '状态码', dataIndex: 'status_code', key: 'status_code', width: 70 },
  { title: '耗时(ms)', dataIndex: 'duration_ms', key: 'duration_ms', width: 80 },
  { title: '操作类型', dataIndex: 'action', key: 'action', width: 80 },
  { title: 'IP地址', dataIndex: 'ip_address', key: 'ip_address', width: 110 },
  { title: '操作时间', dataIndex: 'created_at', key: 'created_at', width: 140 },
  { title: '详情', key: 'details', width: 60 }
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

function getActionColor(action?: string): string {
  if (!action) return 'default'
  const actionLower = action.toLowerCase()
  if (actionLower.includes('删除') || actionLower.includes('delete')) return 'red'
  if (actionLower.includes('创建') || actionLower.includes('新增') || actionLower.includes('create')) return 'green'
  if (actionLower.includes('更新') || actionLower.includes('修改') || actionLower.includes('update')) return 'blue'
  if (actionLower.includes('禁用') || actionLower.includes('停用')) return 'orange'
  if (actionLower.includes('激活') || actionLower.includes('启用')) return 'cyan'
  return 'default'
}

function getMethodColor(method?: string): string {
  const m = (method || '').toUpperCase()
  if (m === 'GET') return 'blue'
  if (m === 'POST') return 'green'
  if (m === 'PUT' || m === 'PATCH') return 'orange'
  if (m === 'DELETE') return 'red'
  return 'default'
}

function getStatusColor(code?: number): string {
  if (!code) return 'default'
  if (code >= 500) return 'red'
  if (code >= 400) return 'orange'
  if (code >= 200 && code < 300) return 'green'
  return 'default'
}

const logDetailsVisible = ref(false)
const currentLogDetails = ref<any>(null)

function showLogDetails(record: any) {
  currentLogDetails.value = record
  logDetailsVisible.value = true
}

function handleMenuClick({ key }: { key: string }) {
  if (key === 'users') {
    loadUsers(true)
  } else if (key === 'comments') {
    loadComments(true)
  } else if (key === 'content') {
    loadPendingPosts(true)
  } else if (key === 'logs') {
    loadAuditLogs(true)
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
  if (selectedKeys.value[0] === 'analytics') {
    await loadVisualizationData()
  }
})

watch(selectedKeys, async (newKeys) => {
  if (newKeys[0] === 'analytics' && !visualizationData.value) {
    await loadVisualizationData()
  }
})

async function loadSystemStats() {
  try {
    const response = await axios.get('/admin/stats')
    systemStats.value = response.data.data
  } catch (error) {
    message.error('加载统计数据失败')
  }
}

async function loadVisualizationData() {
  try {
    const response = await axios.get('/admin/stats/visualization')
    visualizationData.value = response.data.data
    await nextTick()
    setTimeout(() => {
      initCharts()
      updateCharts()
    }, 200)
  } catch (error) {
    console.error('加载可视化数据失败', error)
  }
}

function initCharts() {
  if (userTrendChartRef.value) {
    const existingChart = echarts.getInstanceByDom(userTrendChartRef.value)
    if (!existingChart) {
      echarts.init(userTrendChartRef.value)
    }
  }
  if (postTrendChartRef.value) {
    const existingChart = echarts.getInstanceByDom(postTrendChartRef.value)
    if (!existingChart) {
      echarts.init(postTrendChartRef.value)
    }
  }
  if (moderationChartRef.value) {
    const existingChart = echarts.getInstanceByDom(moderationChartRef.value)
    if (!existingChart) {
      echarts.init(moderationChartRef.value)
    }
  }
  if (contentTypeChartRef.value) {
    const existingChart = echarts.getInstanceByDom(contentTypeChartRef.value)
    if (!existingChart) {
      echarts.init(contentTypeChartRef.value)
    }
  }
  if (interactionChartRef.value) {
    const existingChart = echarts.getInstanceByDom(interactionChartRef.value)
    if (!existingChart) {
      echarts.init(interactionChartRef.value)
    }
  }
  window.addEventListener('resize', handleResize)
}

function handleResize() {
  if (userTrendChartRef.value) {
    echarts.getInstanceByDom(userTrendChartRef.value)?.resize()
  }
  if (postTrendChartRef.value) {
    echarts.getInstanceByDom(postTrendChartRef.value)?.resize()
  }
  if (moderationChartRef.value) {
    echarts.getInstanceByDom(moderationChartRef.value)?.resize()
  }
  if (contentTypeChartRef.value) {
    echarts.getInstanceByDom(contentTypeChartRef.value)?.resize()
  }
  if (interactionChartRef.value) {
    echarts.getInstanceByDom(interactionChartRef.value)?.resize()
  }
}

function updateCharts() {
  if (!visualizationData.value) return

  const userTrend = visualizationData.value?.user_trend || []
  const postTrend = visualizationData.value?.post_trend || []
  const moderationDist = visualizationData.value?.moderation_distribution || []
  const contentTypeDist = visualizationData.value?.content_type_distribution || []
  const interactionStats = visualizationData.value?.interaction_stats || {}

  if (userTrendChartRef.value) {
    const chart = echarts.getInstanceByDom(userTrendChartRef.value)
    if (chart) {
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: userTrend.map((i: any) => i.date.slice(5)) },
        yAxis: { type: 'value' },
        series: [{
          data: userTrend.map((i: any) => i.count),
          type: 'line',
          smooth: true,
          areaStyle: { color: 'rgba(64, 158, 255, 0.2)' },
          itemStyle: { color: '#40a9ff' },
          lineStyle: { width: 3 }
        }]
      }, true)
    }
  }

  if (postTrendChartRef.value) {
    const chart = echarts.getInstanceByDom(postTrendChartRef.value)
    if (chart) {
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: postTrend.map((i: any) => i.date.slice(5)) },
        yAxis: { type: 'value' },
        series: [{
          data: postTrend.map((i: any) => i.count),
          type: 'bar',
          barWidth: '50%',
          itemStyle: { 
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#73d13d' },
              { offset: 1, color: '#52c41a' }
            ]),
            borderRadius: [4, 4, 0, 0]
          }
        }]
      }, true)
    }
  }

  if (moderationChartRef.value) {
    const chart = echarts.getInstanceByDom(moderationChartRef.value)
    if (chart) {
      chart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { orient: 'vertical', right: 10, top: 'center' },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['40%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          label: { show: false },
          emphasis: {
            label: { show: true, fontSize: 14, fontWeight: 'bold' }
          },
          data: moderationDist.map((i: any) => ({ value: i.value, name: i.name, itemStyle: { color: i.color } }))
        }]
      }, true)
    }
  }

  if (contentTypeChartRef.value) {
    const chart = echarts.getInstanceByDom(contentTypeChartRef.value)
    if (chart) {
      chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: contentTypeDist.map((i: any) => i.name).reverse() },
        series: [{
          type: 'bar',
          data: contentTypeDist.map((i: any, idx: number) => ({
            value: i.value,
            itemStyle: { color: i.color || ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'][idx % 5] }
          })).reverse(),
          barWidth: '60%',
          itemStyle: { borderRadius: [0, 4, 4, 0] }
        }]
      }, true)
    }
  }

  if (interactionChartRef.value) {
    const chart = echarts.getInstanceByDom(interactionChartRef.value)
    if (chart) {
      chart.setOption({
        tooltip: { trigger: 'item' },
        legend: { top: '5%' },
        series: [{
          type: 'radar',
          radius: '65%',
          indicator: [
            { name: '总点赞', max: Math.max(interactionStats.total_likes || 10, 10) },
            { name: '总浏览', max: Math.max(interactionStats.total_views || 10, 10) },
            { name: '总评论', max: Math.max(interactionStats.total_comments || 10, 10) },
            { name: '平均点赞', max: Math.max((interactionStats.avg_likes_per_post || 1) * 10, 10) },
            { name: '平均浏览', max: Math.max((interactionStats.avg_views_per_post || 1) * 10, 10) }
          ],
          data: [{
            value: [
              interactionStats.total_likes || 0,
              interactionStats.total_views || 0,
              interactionStats.total_comments || 0,
              (interactionStats.avg_likes_per_post || 0) * 10,
              (interactionStats.avg_views_per_post || 0) * 10
            ],
            name: '互动数据',
            itemStyle: { color: '#722ed1' },
            areaStyle: { color: 'rgba(114, 46, 209, 0.3)' }
          }],
          axisName: { color: '#666' }
        }]
      }, true)
    }
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

async function loadComments(force = false) {
  if (comments.value.length > 0 && !force) return
  loadingComments.value = true
  try {
    const response = await axios.get('/admin/comments')
    comments.value = response.data.data?.comments || []
  } catch (error) {
    message.error('加载评论列表失败')
  } finally {
    loadingComments.value = false
  }
}

async function searchComments() {
  loadingComments.value = true
  try {
    const params: any = {}
    if (commentSearchContent.value) params.content = commentSearchContent.value
    if (commentSearchPostId.value) params.post_id = commentSearchPostId.value
    if (commentSearchUserId.value) params.user_id = commentSearchUserId.value
    
    const response = await axios.get('/admin/comments', { params })
    comments.value = response.data.data?.comments || []
  } catch (error) {
    message.error('搜索评论失败')
  } finally {
    loadingComments.value = false
  }
}

function clearCommentSearch() {
  commentSearchContent.value = ''
  commentSearchPostId.value = ''
  commentSearchUserId.value = null
  loadComments(true)
}

async function deleteComment(commentId: string) {
  try {
    await axios.delete(`/admin/comments/${commentId}`)
    message.success('评论已删除')
    await loadComments(true)
  } catch (error) {
    message.error('删除评论失败')
  }
}

async function loadAuditLogs(force = false) {
  if (auditLogs.value.length > 0 && !force) return
  loadingLogs.value = true
  try {
    const response = await axios.get('/admin/logs/audit')
    auditLogs.value = response.data.data?.logs || []
  } catch (error) {
    message.error('加载审计日志失败')
  } finally {
    loadingLogs.value = false
  }
}

async function searchAuditLogs() {
  loadingLogs.value = true
  try {
    const params: any = {}
    if (logSearchResourceId.value) params.resource_id = logSearchResourceId.value
    if (logSearchUserId.value) params.user_id = logSearchUserId.value
    if (logSearchAction.value !== null) params.action = logSearchAction.value
    if (logSearchResource.value) params.resource = logSearchResource.value
    if (logSearchMethod.value) params.method = logSearchMethod.value
    if (logSearchPath.value) params.path_keyword = logSearchPath.value
    if (logSearchStatus.value !== null) params.status_code = logSearchStatus.value

    const response = await axios.get('/admin/logs/audit', { params })
    auditLogs.value = response.data.data?.logs || []
  } catch (error) {
    message.error('搜索日志失败')
  } finally {
    loadingLogs.value = false
  }
}

function clearLogSearch() {
  logSearchResourceId.value = ''
  logSearchUserId.value = null
  logSearchAction.value = null
  logSearchResource.value = ''
  logSearchMethod.value = null
  logSearchPath.value = ''
  logSearchStatus.value = null
  loadAuditLogs(true)
}

async function searchUsers() {
  loadingUsers.value = true
  try {
    const params: any = {}
    if (userSearchKeyword.value) params.username = userSearchKeyword.value
    if (userSearchEmail.value) params.email = userSearchEmail.value
    if (userSearchRole.value) params.role = userSearchRole.value
    if (userSearchActive.value !== null) params.is_active = userSearchActive.value
    if (userSearchVerified.value !== null) params.is_verified = userSearchVerified.value
    
    const response = await axios.get('/admin/users', { params })
    users.value = response.data.data?.users || []
  } catch (error) {
    message.error('搜索用户失败')
  } finally {
    loadingUsers.value = false
  }
}

function clearUserSearch() {
  userSearchKeyword.value = ''
  userSearchEmail.value = ''
  userSearchRole.value = null
  userSearchActive.value = null
  userSearchVerified.value = null
  loadUsers(true)
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
  height: calc(100vh - 64px - 80px);
  overflow-y: auto;
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

.search-bar {
  margin-bottom: 16px;
}

.comment-content {
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.chart-card {
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  margin-bottom: 16px;
}

.charts-row {
  margin-top: 16px;
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

.detail-section {
  margin-top: 16px;
}

.detail-section-title {
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  padding-left: 4px;
}

.detail-pre {
  white-space: pre-wrap;
  word-break: break-all;
  background: #f6f8fa;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.6;
  max-height: 260px;
  overflow-y: auto;
  margin: 0;
  border-left: 3px solid #d9d9d9;
}
</style>
