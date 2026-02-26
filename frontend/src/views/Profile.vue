<template>
  <div class="profile-container">
    <a-page-header title="个人中心" style="background: white; margin-bottom: 16px" @back="router.push('/')" />

    <div style="padding: 0 24px; max-width: 1200px; margin: 0 auto">
      <a-row :gutter="16">
        <a-col :xs="24" :md="8">
          <a-card>
            <div style="text-align: center">
              <a-avatar :size="100" :src="profile?.avatar_url">
                {{ profile?.username[0] }}
              </a-avatar>
              <a-upload
                :show-upload-list="false"
                :before-upload="uploadAvatar"
                accept="image/*"
              >
                <a-button type="link" style="margin-top: 8px">
                  <UploadOutlined /> 更换头像
                </a-button>
              </a-upload>
              <h2 style="margin-top: 16px">{{ profile?.profile?.nickname || profile?.username }}</h2>
              <p style="color: #999">@{{ profile?.username }}</p>
              <a-tag v-if="profile?.role === 'admin'" color="red">管理员</a-tag>
              <a-tag v-if="profile?.is_verified" color="green">已验证</a-tag>
            </div>

            <a-divider />

            <a-descriptions :column="1" size="small">
              <a-descriptions-item label="邮箱">
                {{ profile?.email }}
              </a-descriptions-item>
              <a-descriptions-item label="位置">
                {{ profile?.profile?.location || '未设置' }}
              </a-descriptions-item>
              <a-descriptions-item label="注册时间">
                {{ profile?.created_at }}
              </a-descriptions-item>
            </a-descriptions>
          </a-card>

          <a-card title="统计数据" style="margin-top: 16px">
            <a-statistic
              v-if="stats"
              title="旅行计划"
              :value="stats.total_trips"
            />
            <a-row :gutter="16" style="margin-top: 16px">
              <a-col :span="12">
                <a-statistic title="已完成" :value="stats?.completed_trips" />
              </a-col>
              <a-col :span="12">
                <a-statistic title="收藏" :value="stats?.favorite_trips" />
              </a-col>
            </a-row>
            <a-row :gutter="16" style="margin-top: 16px">
              <a-col :span="12">
                <a-statistic title="访问城市" :value="stats?.total_cities" />
              </a-col>
            </a-row>
          </a-card>
        </a-col>

        <a-col :xs="24" :md="16">
          <a-card title="个人资料">
            <a-form :model="profileForm" layout="vertical">
              <a-form-item label="昵称">
                <a-input v-model:value="profileForm.nickname" />
              </a-form-item>
              <a-form-item label="个人简介">
                <a-textarea v-model:value="profileForm.bio" :rows="3" />
              </a-form-item>
              <a-form-item label="位置">
                <a-input v-model:value="profileForm.location" />
              </a-form-item>
              <a-form-item>
                <a-button type="primary" @click="updateProfile" :loading="updating">
                  保存
                </a-button>
              </a-form-item>
            </a-form>
          </a-card>

          <a-card title="访问过的城市" style="margin-top: 16px">
            <template #extra>
              <a-button
                type="link"
                @click="editingCities ? cancelEditCities() : startEditCities()"
              >
                {{ editingCities ? '取消' : '编辑' }}
              </a-button>
            </template>

            <div v-if="!editingCities">
              <div v-if="visitedCities.length === 0" class="empty-cities">
                <a-empty description="还没有访问记录">
                  <template #image>
                    <div class="empty-icon">🗺️</div>
                  </template>
                  <template #description>
                    <span style="color: #999;">还没有访问记录，快去创建旅行计划吧！</span>
                  </template>
                </a-empty>
              </div>
              <div v-else class="cities-grid">
                <div
                  v-for="(city, index) in visitedCities"
                  :key="city"
                  class="city-card"
                  :style="{ animationDelay: `${index * 0.1}s` }"
                >
                  <div class="city-icon">📍</div>
                  <div class="city-name">{{ city }}</div>
                  <div class="city-badge">已访问</div>
                </div>
              </div>
            </div>

            <div v-else class="edit-cities-section">
              <a-cascader
                v-model:value="selectedCities"
                :options="chinaCities"
                placeholder="请选择省份和城市"
                multiple
                :max-tag-count="5"
                style="width: 100%; margin-bottom: 16px"
                :show-search="{ filter }"
              />
              <div class="edit-actions">
                <a-button
                  type="primary"
                  @click="saveCities"
                  :loading="savingCities"
                  size="large"
                >
                  💾 保存
                </a-button>
                <a-button @click="cancelEditCities" size="large">
                  取消
                </a-button>
              </div>
            </div>
          </a-card>

          <a-card title="修改密码" style="margin-top: 16px">
            <a-form :model="passwordForm" layout="vertical">
              <a-form-item label="当前密码">
                <a-input-password v-model:value="passwordForm.old_password" />
              </a-form-item>
              <a-form-item label="新密码">
                <a-input-password v-model:value="passwordForm.new_password" />
              </a-form-item>
              <a-form-item>
                <a-button type="primary" @click="changePassword" :loading="changingPassword">
                  修改密码
                </a-button>
              </a-form-item>
            </a-form>
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
import { API_BASE_URL } from '@/utils/axios'
import { userService } from '@/services/user'
import { useAuthStore } from '@/stores/auth'
import { UploadOutlined } from '@ant-design/icons-vue'
import { chinaCities, findProvinceByCity } from '@/data/cities'

const profile = ref<any>(null)
const stats = ref<any>(null)
const visitedCities = ref<string[]>([])
const updating = ref(false)
const changingPassword = ref(false)
const editingCities = ref(false)
const savingCities = ref(false)
const selectedCities = ref<string[][]>([])

const profileForm = ref({
  nickname: '',
  bio: '',
  location: ''
})

const passwordForm = ref({
  old_password: '',
  new_password: ''
})

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  await loadProfile()
  await loadStats()
  await loadVisitedCities()
})

async function loadProfile() {
  try {
    const response = await userService.getProfile()
    
    // 解析travel_preferences数组，提取nickname、bio、location
    const preferences: { [key: string]: string } = {}
    if (response.profile?.travel_preferences) {
      response.profile.travel_preferences.forEach((pref: string) => {
        const [key, value] = pref.split(':')
        if (key && value) {
          preferences[key] = value
        }
      })
    }
    
    // 处理后的profile数据，添加解析后的属性和完整的头像URL
    let avatarUrl = response.avatar_url
    
    profile.value = {
      ...response,
      avatar_url: avatarUrl,
      profile: {
        ...response.profile,
        nickname: preferences.nickname,
        bio: preferences.bio,
        location: preferences.location
      }
    }
    
    profileForm.value = {
      nickname: preferences.nickname || '',
      bio: preferences.bio || '',
      location: preferences.location || ''
    }
    
    // 更新authStore中的用户信息，确保首页头像同步更新
    // console.log('Profile.vue: 更新authStore中的用户信息')
    // console.log('Profile.vue: 新的用户信息 - id:', response.id)
    // console.log('Profile.vue: 新的用户信息 - username:', response.username)
    // console.log('Profile.vue: 新的用户信息 - avatar_url:', avatarUrl)
    
    // 无论authStore.user.value是否存在，都更新用户信息
    authStore.setUser({
      id: response.id,
      username: response.username,
      email: response.email,
      nickname: preferences.nickname,
      avatar_url: avatarUrl,
      role: response.role,
      is_verified: response.is_verified
    })
    
    console.log('Profile.vue: 更新后的authStore.user.value:', authStore.user.value)
  } catch (error) {
    message.error('加载个人资料失败')
  }
}

async function loadStats() {
  try {
    stats.value = await userService.getStats()
  } catch (error) {
    message.error('加载统计数据失败')
  }
}

async function loadVisitedCities() {
  try {
    const response = await userService.getVisitedCities()
    visitedCities.value = response || []
  } catch (error) {
    message.error('加载访问城市失败')
  }
}

async function updateProfile() {
  updating.value = true
  try {
    // 后端只返回成功消息，不返回完整用户资料
    await userService.updateProfile(profileForm.value)
    // 重新加载完整用户资料
    await loadProfile()
    message.success('更新成功')
  } catch (error) {
    message.error('更新失败')
  } finally {
    updating.value = false
  }
}

async function uploadAvatar(file: File) {
  try {
    const result = await userService.uploadAvatar(file)
    // 重新加载完整用户资料以获取最新的头像URL
    await loadProfile()
    message.success('头像上传成功')
  } catch (error) {
    message.error('头像上传失败')
  }
  return false
}

async function changePassword() {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    message.error('请填写完整')
    return
  }
  if (passwordForm.value.new_password.length < 6) {
    message.error('新密码至少6位')
    return
  }

  changingPassword.value = true
  try {
    await userService.changePassword(passwordForm.value)
    message.success('密码修改成功')
    passwordForm.value = { old_password: '', new_password: '' }
  } catch (error) {
    message.error('密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 城市编辑相关函数
function cancelEditCities() {
  editingCities.value = false
  // 重置选择
  selectedCities.value = visitedCities.value.map(city => {
    const province = findProvinceByCity(city)
    return province ? [province, city] : []
  }).filter(item => item.length > 0)
}

async function saveCities() {
  savingCities.value = true
  try {
    // console.log('保存前的级联选择器数据:', selectedCities.value)

    // 从级联选择器的值中提取城市名称
    // 对于直辖市，数组只有一个元素 ['北京']
    // 对于其他城市，数组有两个元素 ['广东', '广州']
    const cities = selectedCities.value
      .map(item => {
        if (!item || !Array.isArray(item) || item.length === 0) {
          return null
        }
        // 如果只有一个元素，说明是直辖市，取第一个元素
        // 如果有两个元素，取第二个元素（城市名）
        const city = item.length === 1 ? item[0] : item[1]
        // console.log('处理项:', item, '提取城市:', city)
        return city
      })
      .filter(city => {
        const isValid = city && typeof city === 'string' && city.trim() !== ''
        // console.log('城市:', city, '是否有效:', isValid)
        return isValid
      })

    // console.log('最终要保存的城市列表:', cities)

    await userService.updateVisitedCities(cities)
    visitedCities.value = cities
    editingCities.value = false
    message.success('城市列表更新成功')

    // 重新加载统计数据
    await loadStats()
  } catch (error) {
    console.error('保存城市失败:', error)
    message.error('更新城市列表失败')
  } finally {
    savingCities.value = false
  }
}

// 级联选择器搜索过滤函数
function filter(inputValue: string, path: any[]) {
  return path.some(option =>
    option.label.toLowerCase().indexOf(inputValue.toLowerCase()) > -1
  )
}

// 监听编辑模式变化，初始化选择的城市
function startEditCities() {
  editingCities.value = true
  // 将现有城市转换为级联选择器格式 [省份, 城市]
  selectedCities.value = visitedCities.value
    .map(city => {
      const province = findProvinceByCity(city)
      if (!province) {
        console.warn(`无法找到城市 "${city}" 对应的省份`)
        return null
      }
      return [province, city]
    })
    .filter(item => item !== null) as string[][]

  // console.log('当前访问的城市:', visitedCities.value)
  // console.log('转换后的级联选择器数据:', selectedCities.value)
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #f0f2f5;
}

/* 城市网格布局 */
.cities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
  padding: 8px 0;
}

/* 城市卡片 */
.city-card {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.5s ease-out;
  overflow: hidden;
}

.city-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.city-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.city-card:hover::before {
  opacity: 1;
}

/* 城市图标 */
.city-icon {
  font-size: 32px;
  margin-bottom: 8px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

/* 城市名称 */
.city-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 城市徽章 */
.city-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  color: #fff;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 空状态 */
.empty-cities {
  padding: 40px 0;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

/* 编辑区域 */
.edit-cities-section {
  padding: 8px 0;
}

.edit-actions {
  display: flex;
  gap: 12px;
}

/* 淡入动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cities-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }

  .city-card {
    padding: 16px 12px;
  }

  .city-icon {
    font-size: 28px;
  }

  .city-name {
    font-size: 14px;
  }
}
</style>
