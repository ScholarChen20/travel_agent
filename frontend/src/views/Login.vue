<template>
  <div class="auth-container">
    <div class="auth-content animate-fade-in-up">
      <div class="auth-header">
        <div class="logo-icon">✈️</div>
        <h2 class="auth-title">欢迎回来</h2>
        <p class="auth-subtitle">登录您的账号，继续精彩旅程</p>
      </div>

      <a-card class="auth-card" :bordered="false">
        <a-form :model="form" @finish="handleLogin" layout="vertical">
          <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
            <a-input v-model:value="form.username" placeholder="用户名" size="large" class="custom-input">
              <template #prefix><UserOutlined class="input-icon" /></template>
            </a-input>
          </a-form-item>

          <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
            <a-input-password v-model:value="form.password" placeholder="密码" size="large" class="custom-input">
              <template #prefix><LockOutlined class="input-icon" /></template>
            </a-input-password>
          </a-form-item>

          <a-form-item name="captcha_code" :rules="[{ required: true, message: '请输入验证码' }]">
            <div class="captcha-wrapper">
              <a-input v-model:value="form.captcha_code" placeholder="验证码" size="large" class="custom-input captcha-input">
                <template #prefix><SafetyOutlined class="input-icon" /></template>
              </a-input>
              <div class="captcha-image-box" @click="loadCaptcha" title="点击刷新">
                <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
                <div v-else class="captcha-placeholder">
                  <a-spin size="small" />
                </div>
              </div>
            </div>
          </a-form-item>

          <a-form-item>
            <a-button type="primary" html-type="submit" :loading="loading" block size="large" class="submit-btn">
              登录
            </a-button>
          </a-form-item>

          <div class="auth-footer">
            <span class="footer-text">还没有账号？</span>
            <router-link to="/register" class="link-text">立即注册</router-link>
          </div>
        </a-form>
      </a-card>
    </div>

    <!-- Background decoration -->
    <div class="bg-circles">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
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
.auth-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-light-gradient);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.auth-content {
  width: 100%;
  max-width: 420px;
  z-index: 10;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 16px;
  animation: float 6s ease-in-out infinite;
}

.auth-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.auth-subtitle {
  font-size: 16px;
  color: var(--text-tertiary);
  margin: 0;
}

.auth-card {
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.9);
  padding: 12px;
}

.custom-input :deep(.ant-input) {
  border-radius: var(--border-radius-md);
  background: var(--bg-secondary);
  border: 1px solid transparent;
  transition: all 0.3s;
}

.custom-input :deep(.ant-input:focus),
.custom-input :deep(.ant-input-focused) {
  background: #fff;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.custom-input :deep(.ant-input-affix-wrapper) {
  border-radius: var(--border-radius-md);
  background: var(--bg-secondary);
  border: 1px solid transparent;
  padding-top: 8px;
  padding-bottom: 8px;
}

.custom-input :deep(.ant-input-affix-wrapper:focus),
.custom-input :deep(.ant-input-affix-wrapper-focused) {
  background: #fff;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.input-icon {
  color: var(--text-tertiary);
  font-size: 16px;
}

.captcha-wrapper {
  display: flex;
  gap: 12px;
}

.captcha-input {
  flex: 1;
}

.captcha-image-box {
  width: 120px;
  height: 40px;
  border-radius: var(--border-radius-md);
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  transition: all 0.3s;
}

.captcha-image-box:hover {
  border-color: var(--primary-color);
}

.captcha-image-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.captcha-placeholder {
  color: var(--text-tertiary);
  font-size: 12px;
}

.submit-btn {
  height: 48px;
  border-radius: var(--border-radius-full);
  background: var(--bg-gradient);
  border: none;
  font-size: 16px;
  font-weight: 600;
  box-shadow: var(--shadow-primary);
  transition: all 0.3s;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.6);
}

.auth-footer {
  text-align: center;
  margin-top: 16px;
}

.footer-text {
  color: var(--text-tertiary);
}

.link-text {
  color: var(--primary-color);
  font-weight: 600;
  margin-left: 4px;
  text-decoration: none;
  transition: color 0.3s;
}

.link-text:hover {
  color: var(--secondary-color);
  text-decoration: underline;
}

/* Background circles */
.bg-circles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
  filter: blur(60px);
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: rgba(102, 126, 234, 0.2);
  top: -100px;
  left: -100px;
  animation: float 8s ease-in-out infinite;
}

.circle-2 {
  width: 300px;
  height: 300px;
  background: rgba(240, 147, 251, 0.2);
  bottom: -50px;
  right: -50px;
  animation: float 10s ease-in-out infinite reverse;
}

.circle-3 {
  width: 200px;
  height: 200px;
  background: rgba(82, 196, 26, 0.1);
  top: 40%;
  left: 20%;
  animation: float 12s ease-in-out infinite 2s;
}
</style>