<template>
  <div class="profile-container">
    <a-page-header title="个人中心" style="background: white; margin-bottom: 16px" />

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
            <a-tag v-for="city in visitedCities" :key="city" color="blue" style="margin: 4px">
              {{ city }}
            </a-tag>
            <a-empty v-if="visitedCities.length === 0" description="还没有访问记录" />
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
import { message } from 'ant-design-vue'
import { API_BASE_URL } from '@/utils/axios'
import { userService } from '@/services/user'
import { useAuthStore } from '@/stores/auth'
import { UploadOutlined } from '@ant-design/icons-vue'

const profile = ref<any>(null)
const stats = ref<any>(null)
const visitedCities = ref<string[]>([])
const updating = ref(false)
const changingPassword = ref(false)

const profileForm = ref({
  nickname: '',
  bio: '',
  location: ''
})

const passwordForm = ref({
  old_password: '',
  new_password: ''
})

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
    // 如果头像URL是相对路径，添加API_BASE_URL前缀
    if (avatarUrl && avatarUrl.startsWith('/')) {
      avatarUrl = API_BASE_URL + avatarUrl
    }
    
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
    if (authStore.user.value) {
      authStore.setUser({
        id: response.id,
        username: response.username,
        email: response.email,
        nickname: preferences.nickname,
        avatar_url: avatarUrl,
        role: response.role,
        is_verified: response.is_verified
      })
    }
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
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
