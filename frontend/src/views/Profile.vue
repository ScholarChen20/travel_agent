<template>
  <div class="profile-page">
    <!-- 顶部导航栏 -->
    <div class="profile-topbar">
      <div class="topbar-inner">
        <a-button type="text" class="back-btn" @click="router.push('/')">
          <LeftOutlined /> 返回首页
        </a-button>
        <span class="page-title">个人中心</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="profile-main">
      <a-row :gutter="[24, 24]">
        <!-- 左侧：用户信息卡片 -->
        <a-col :xs="24" :md="8" :lg="7">
          <a-card :bordered="false" class="user-card">
            <!-- 头像区域 -->
            <div class="avatar-section">
              <div class="avatar-container">
                <a-avatar :size="90" :src="profile?.avatar_url" class="user-avatar">
                  <template v-if="!profile?.avatar_url" #icon><UserOutlined /></template>
                </a-avatar>
              </div>
              <a-upload :show-upload-list="false" :before-upload="uploadAvatar" accept="image/*">
                <a-button type="link" size="small" class="avatar-upload-btn">
                  <CameraOutlined /> 更换头像
                </a-button>
              </a-upload>
              <h2 class="user-name">{{ profile?.profile?.full_name || profile?.username }}</h2>
              <p class="user-at">@{{ profile?.username }}</p>
              <div class="user-badges">
                <a-tag v-if="profile?.role === 'admin'" color="volcano">管理员</a-tag>
                <a-tag v-if="profile?.is_verified" color="success">已认证</a-tag>
                <a-tag v-if="profile?.is_verified === false" color="default">未认证</a-tag>
              </div>
            </div>

            <a-divider style="margin: 20px 0 16px" />

            <!-- 用户信息列表 -->
            <ul class="user-info-list">
              <li v-if="profile?.email">
                <MailOutlined class="list-icon" />
                <span>{{ profile.email }}</span>
              </li>
              <li v-if="profile?.profile?.location">
                <EnvironmentOutlined class="list-icon" />
                <span>{{ profile.profile.location }}</span>
              </li>
              <li v-if="profile?.profile?.gender">
                <TeamOutlined class="list-icon" />
                <span>{{ genderLabel(profile.profile.gender) }}</span>
              </li>
              <li v-if="profile?.profile?.birth_date">
                <CalendarOutlined class="list-icon" />
                <span>{{ formatBirthDate(profile.profile.birth_date) }}</span>
              </li>
              <li v-if="profile?.created_at">
                <ClockCircleOutlined class="list-icon" />
                <span>{{ formatJoinDate(profile.created_at) }} 加入</span>
              </li>
            </ul>

            <a-divider style="margin: 16px 0 20px" />

            <!-- 统计数据 -->
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-num">{{ stats?.total_trips || 0 }}</div>
                <div class="stat-lab">旅行计划</div>
              </div>
              <div class="stat-item">
                <div class="stat-num">{{ stats?.completed_trips || 0 }}</div>
                <div class="stat-lab">已完成</div>
              </div>
              <div class="stat-item">
                <div class="stat-num">{{ visitedCities.length }}</div>
                <div class="stat-lab">访问城市</div>
              </div>
              <div class="stat-item">
                <div class="stat-num">{{ stats?.favorite_trips || 0 }}</div>
                <div class="stat-lab">收藏</div>
              </div>
            </div>
          </a-card>
        </a-col>

        <!-- 右侧：标签页内容 -->
        <a-col :xs="24" :md="16" :lg="17">
          <a-card :bordered="false" class="content-card">
            <a-tabs v-model:activeKey="activeTab" size="large">

              <!-- Tab1: 基本资料 -->
              <a-tab-pane key="info">
                <template #tab>
                  <span><EditOutlined /> 基本资料</span>
                </template>
                <a-form :model="profileForm" layout="vertical" class="profile-form">
                  <a-row :gutter="16">
                    <a-col :xs="24" :sm="12">
                      <a-form-item label="昵称">
                        <a-input
                          v-model:value="profileForm.full_name"
                          placeholder="请输入昵称"
                          allow-clear
                          :maxlength="50"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :xs="24" :sm="12">
                      <a-form-item label="用户名">
                        <a-input
                          v-model:value="profileForm.username"
                          placeholder="请输入用户名"
                          allow-clear
                          :maxlength="50"
                        />
                      </a-form-item>
                    </a-col>
                  </a-row>

                  <a-row :gutter="16">
                    <a-col :xs="24" :sm="12">
                      <a-form-item label="邮箱">
                        <a-input
                          v-model:value="profileForm.email"
                          placeholder="请输入邮箱"
                          allow-clear
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :xs="24" :sm="12">
                      <a-form-item label="性别">
                        <a-select
                          v-model:value="profileForm.gender"
                          placeholder="请选择性别"
                          allow-clear
                        >
                          <a-select-option value="male">男</a-select-option>
                          <a-select-option value="female">女</a-select-option>
                          <a-select-option value="other">保密</a-select-option>
                        </a-select>
                      </a-form-item>
                    </a-col>
                  </a-row>

                  <a-row :gutter="16">
                    <a-col :xs="24" :sm="12">
                      <a-form-item label="出生日期">
                        <a-date-picker
                          v-model:value="profileForm.birth_date"
                          style="width: 100%"
                          placeholder="请选择出生日期"
                          :disabled-date="disabledFutureDate"
                        />
                      </a-form-item>
                    </a-col>
                    <a-col :xs="24" :sm="12">
                      <a-form-item label="所在城市">
                        <a-cascader
                          v-model:value="profileForm.locationCascader"
                          :options="chinaCities"
                          placeholder="请选择省份/城市"
                          :show-search="{ filter }"
                          allow-clear
                          style="width: 100%"
                        />
                      </a-form-item>
                    </a-col>
                  </a-row>

                  <a-form-item label="旅行偏好">
                    <a-select
                      v-model:value="profileForm.travel_preferences"
                      mode="tags"
                      :token-separators="[',']"
                      placeholder="输入偏好标签，按回车添加（如：山地徒步、海滨度假）"
                      style="width: 100%"
                    >
                      <a-select-option v-for="pref in suggestedPreferences" :key="pref" :value="pref">
                        {{ pref }}
                      </a-select-option>
                    </a-select>
                  </a-form-item>

                  <a-form-item>
                    <a-button
                      type="primary"
                      size="large"
                      @click="updateProfile"
                      :loading="updating"
                      style="min-width: 120px"
                    >
                      保存修改
                    </a-button>
                  </a-form-item>
                </a-form>
              </a-tab-pane>

              <!-- Tab2: 访问城市 -->
              <a-tab-pane key="cities">
                <template #tab>
                  <span><CompassOutlined /> 访问城市</span>
                </template>
                <div class="tab-header">
                  <span class="tab-desc">记录你走过的城市足迹（{{ visitedCities.length }} 个城市）</span>
                  <a-button
                    type="link"
                    @click="editingCities ? cancelEditCities() : startEditCities()"
                  >
                    {{ editingCities ? '取消编辑' : '编辑城市' }}
                  </a-button>
                </div>

                <div v-if="!editingCities">
                  <div v-if="visitedCities.length === 0" class="empty-cities">
                    <a-empty description="还没有访问记录，去探索吧！" />
                  </div>
                  <div v-else class="cities-grid">
                    <div
                      v-for="(city, index) in visitedCities"
                      :key="city"
                      class="city-card"
                      :style="{ animationDelay: `${index * 0.08}s` }"
                    >
                      <div class="city-icon">📍</div>
                      <div class="city-name">{{ city }}</div>
                      <div class="city-badge">已访问</div>
                    </div>
                  </div>
                </div>

                <div v-else class="edit-cities">
                  <a-cascader
                    v-model:value="selectedCities"
                    :options="chinaCities"
                    placeholder="请选择省份和城市"
                    multiple
                    :max-tag-count="5"
                    style="width: 100%; margin-bottom: 16px"
                    :show-search="{ filter }"
                  />
                  <a-space>
                    <a-button type="primary" @click="saveCities" :loading="savingCities">
                      💾 保存
                    </a-button>
                    <a-button @click="cancelEditCities">取消</a-button>
                  </a-space>
                </div>
              </a-tab-pane>

              <!-- Tab3: 账号安全 -->
              <a-tab-pane key="security">
                <template #tab>
                  <span><LockOutlined /> 账号安全</span>
                </template>
                <div class="security-section">
                  <a-alert
                    message="安全提示"
                    description="新密码长度至少8位，须包含大小写字母、数字、特殊字符中的至少3种。"
                    type="info"
                    show-icon
                    style="margin-bottom: 24px"
                  />
                  <a-form :model="passwordForm" layout="vertical" style="max-width: 420px">
                    <a-form-item label="当前密码">
                      <a-input-password
                        v-model:value="passwordForm.old_password"
                        placeholder="请输入当前密码"
                        autocomplete="current-password"
                      />
                    </a-form-item>
                    <a-form-item label="新密码">
                      <a-input-password
                        v-model:value="passwordForm.new_password"
                        placeholder="新密码至少8位"
                        autocomplete="new-password"
                      />
                    </a-form-item>
                    <a-form-item label="确认新密码">
                      <a-input-password
                        v-model:value="passwordForm.confirm_password"
                        placeholder="再次输入新密码"
                        autocomplete="new-password"
                      />
                    </a-form-item>
                    <a-form-item>
                      <a-button
                        type="primary"
                        danger
                        size="large"
                        @click="changePassword"
                        :loading="changingPassword"
                      >
                        确认修改密码
                      </a-button>
                    </a-form-item>
                  </a-form>
                </div>
              </a-tab-pane>

            </a-tabs>
          </a-card>
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { userService } from '@/services/user'
import { useAuthStore } from '@/stores/auth'
import { chinaCities, findProvinceByCity } from '@/data/cities'
import {
  UserOutlined,
  MailOutlined,
  EnvironmentOutlined,
  CalendarOutlined,
  CameraOutlined,
  LeftOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  EditOutlined,
  LockOutlined,
  CompassOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const profile = ref<any>(null)
const stats = ref<any>(null)
const visitedCities = ref<string[]>([])
const activeTab = ref('info')
const updating = ref(false)
const changingPassword = ref(false)
const editingCities = ref(false)
const savingCities = ref(false)
const selectedCities = ref<string[][]>([])

const profileForm = ref({
  full_name: '',
  username: '',
  email: '',
  gender: null as string | null,
  birth_date: null as any,
  locationCascader: [] as string[],
  travel_preferences: [] as string[]
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const suggestedPreferences = [
  '山地徒步', '海滨度假', '城市探索', '文化体验',
  '美食之旅', '自然风光', '古镇古迹', '亲子游',
  '自驾游', '背包旅行', '摄影旅行', '户外露营'
]

onMounted(async () => {
  await loadProfile()
  await loadStats()
  await loadVisitedCities()
})

async function loadProfile() {
  try {
    const data = await userService.getProfile()
    profile.value = data

    profileForm.value = {
      full_name: data.profile?.full_name || '',
      username: data.username || '',
      email: data.email || '',
      gender: data.profile?.gender || null,
      birth_date: data.profile?.birth_date ? dayjs(data.profile.birth_date) : null,
      locationCascader: buildLocationCascader(data.profile?.location),
      travel_preferences: data.profile?.travel_preferences?.filter((p: string) => p) || []
    }

    authStore.setUser({
      id: data.id,
      username: data.username,
      email: data.email,
      nickname: data.profile?.full_name,
      avatar_url: data.avatar_url,
      role: data.role,
      is_verified: data.is_verified
    })
  } catch (error) {
    message.error('加载个人资料失败')
  }
}

function buildLocationCascader(location: string | null | undefined): string[] {
  if (!location) return []
  const province = findProvinceByCity(location)
  if (province) return [province, location]
  return [location]
}

async function loadStats() {
  try {
    stats.value = await userService.getStats()
  } catch {
    // 静默失败
  }
}

async function loadVisitedCities() {
  try {
    visitedCities.value = await userService.getVisitedCities() || []
  } catch {
    // 静默失败
  }
}

async function updateProfile() {
  updating.value = true
  try {
    const locationArr = profileForm.value.locationCascader
    const location = locationArr.length > 0
      ? (locationArr.length === 1 ? locationArr[0] : locationArr[locationArr.length - 1])
      : undefined

    const payload: any = {}
    if (profileForm.value.full_name) payload.full_name = profileForm.value.full_name
    if (profileForm.value.username) payload.username = profileForm.value.username
    if (profileForm.value.email) payload.email = profileForm.value.email
    if (profileForm.value.gender) payload.gender = profileForm.value.gender
    if (profileForm.value.birth_date) {
      payload.birth_date = profileForm.value.birth_date.format('YYYY-MM-DD')
    }
    if (location !== undefined) payload.location = location
    if (profileForm.value.travel_preferences.length > 0) {
      payload.travel_preferences = profileForm.value.travel_preferences
    }

    await userService.updateProfile(payload)
    await loadProfile()
    message.success('个人资料已更新')
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '更新失败')
  } finally {
    updating.value = false
  }
}

async function uploadAvatar(file: File) {
  try {
    await userService.uploadAvatar(file)
    await loadProfile()
    message.success('头像上传成功')
  } catch {
    message.error('头像上传失败')
  }
  return false
}

async function changePassword() {
  const { old_password, new_password, confirm_password } = passwordForm.value
  if (!old_password || !new_password || !confirm_password) {
    message.warning('请填写所有密码字段')
    return
  }
  if (new_password.length < 8) {
    message.warning('新密码至少8位')
    return
  }
  if (new_password !== confirm_password) {
    message.error('两次输入的新密码不一致')
    return
  }
  changingPassword.value = true
  try {
    await userService.changePassword({ old_password, new_password })
    message.success('密码修改成功')
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (error: any) {
    message.error(error?.response?.data?.detail || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

function disabledFutureDate(current: any) {
  return current && current > dayjs().endOf('day')
}

function genderLabel(gender: string): string {
  const map: Record<string, string> = { male: '男', female: '女', other: '保密' }
  return map[gender] || gender
}

function formatJoinDate(dateStr: string): string {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY年MM月')
}

function formatBirthDate(dateStr: string): string {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY年MM月DD日')
}

function filter(inputValue: string, path: any[]) {
  return path.some(option =>
    option.label.toLowerCase().indexOf(inputValue.toLowerCase()) > -1
  )
}

function startEditCities() {
  editingCities.value = true
  selectedCities.value = visitedCities.value
    .map(city => {
      const province = findProvinceByCity(city)
      if (!province) return null
      return [province, city]
    })
    .filter(item => item !== null) as string[][]
}

function cancelEditCities() {
  editingCities.value = false
  selectedCities.value = visitedCities.value
    .map(city => {
      const province = findProvinceByCity(city)
      return province ? [province, city] : []
    })
    .filter(item => item.length > 0)
}

async function saveCities() {
  savingCities.value = true
  try {
    const cities = selectedCities.value
      .map(item => {
        if (!item || !Array.isArray(item) || item.length === 0) return null
        return item.length === 1 ? item[0] : item[1]
      })
      .filter(city => city && typeof city === 'string' && city.trim() !== '')

    await userService.updateVisitedCities(cities as string[])
    visitedCities.value = cities as string[]
    editingCities.value = false
    message.success('城市列表更新成功')
    await loadStats()
  } catch {
    message.error('更新城市列表失败')
  } finally {
    savingCities.value = false
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f7fa;
}

/* 顶部导航 */
.profile-topbar {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
}

.topbar-inner {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  color: rgba(0, 0, 0, 0.55);
  padding: 0;
  font-size: 14px;
}

.back-btn:hover {
  color: #1890ff;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
}

/* 主内容 */
.profile-main {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
}

/* 左侧用户卡片 */
.user-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.avatar-section {
  text-align: center;
  padding: 8px 0 4px;
}

.avatar-container {
  margin-bottom: 8px;
}

.user-avatar {
  background: linear-gradient(135deg, #1890ff, #096dd9);
}

.avatar-upload-btn {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 12px;
  display: inline-block;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  margin: 8px 0 4px;
}

.user-at {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.4);
  margin: 0 0 12px;
}

.user-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
}

/* 用户信息列表 */
.user-info-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.user-info-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.user-info-list li:last-child {
  border-bottom: none;
}

.list-icon {
  color: rgba(0, 0, 0, 0.3);
  font-size: 13px;
  flex-shrink: 0;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-item {
  text-align: center;
  padding: 14px 8px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  transition: background 0.2s;
}

.stat-item:hover {
  background: rgba(24, 144, 255, 0.06);
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #1890ff;
  line-height: 1;
}

.stat-lab {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  margin-top: 4px;
}

/* 右侧内容卡片 */
.content-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  min-height: 500px;
}

.profile-form {
  padding-top: 8px;
}

/* 城市标签页 */
.tab-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.tab-desc {
  color: rgba(0, 0, 0, 0.45);
  font-size: 13px;
}

.empty-cities {
  padding: 40px 0;
}

/* 城市网格 */
.cities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
  padding: 4px 0;
}

.city-card {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
  cursor: default;
  transition: all 0.25s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.4s ease-out both;
  overflow: hidden;
}

.city-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.city-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.city-name {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
}

.city-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.edit-cities {
  padding: 4px 0;
}

/* 安全设置 */
.security-section {
  padding-top: 4px;
  max-width: 520px;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .profile-main {
    padding: 0 16px;
    margin: 16px auto;
  }

  .cities-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }

  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .stat-num {
    font-size: 18px;
  }
}
</style>
