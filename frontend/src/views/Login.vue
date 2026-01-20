<template>
  <div class="login-container">
    <a-card title="登录" style="width: 400px">
      <a-form :model="form" @finish="handleLogin">
        <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="form.username" placeholder="用户名">
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>

        <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
          <a-input-password v-model:value="form.password" placeholder="密码">
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>

        <a-form-item name="captcha_code" :rules="[{ required: true, message: '请输入验证码' }]">
          <a-row :gutter="8">
            <a-col :span="14">
              <a-input v-model:value="form.captcha_code" placeholder="验证码">
                <template #prefix><SafetyOutlined /></template>
              </a-input>
            </a-col>
            <a-col :span="10">
              <img
                v-if="captchaImage"
                :src="captchaImage"
                @click="loadCaptcha"
                style="width: 100%; height: 40px; cursor: pointer; border-radius: 4px; border: 1px solid #d9d9d9"
                alt="验证码"
                title="点击刷新"
              />
              <a-button v-else @click="loadCaptcha" block>获取验证码</a-button>
            </a-col>
          </a-row>
        </a-form-item>

        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading" block>
            登录
          </a-button>
        </a-form-item>

        <a-form-item>
          <router-link to="/register">还��有账号？立即注册</router-link>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
  captcha_code: '',
  captcha_session_id: ''
})

const loading = ref(false)
const captchaImage = ref('')

onMounted(() => {
  loadCaptcha()
})

async function loadCaptcha() {
  try {
    const result = await authService.getCaptcha()
    captchaImage.value = result.image_base64
    form.value.captcha_session_id = result.session_id
  } catch (error) {
    message.error('获取验证码失败')
  }
}

async function handleLogin() {
  if (!form.value.captcha_session_id) {
    message.error('请先获取验证码')
    return
  }

  loading.value = true
  try {
    const result = await authService.login(form.value)
    authStore.setToken(result.access_token)
    authStore.setUser(result.user)
    message.success('登录成功')

    const redirect = route.query.redirect as string || '/'
    router.push(redirect)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '登录失败')
    loadCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
