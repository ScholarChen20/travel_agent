<template>
  <div class="register-container">
    <a-card title="注册" style="width: 400px">
      <a-form :model="form" @finish="handleRegister">
        <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="form.username" placeholder="用户名">
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>

        <a-form-item name="email" :rules="[{ required: true, type: 'email', message: '请输入有效的邮箱' }]">
          <a-input v-model:value="form.email" placeholder="邮箱">
            <template #prefix><MailOutlined /></template>
          </a-input>
        </a-form-item>

        <a-form-item name="password" :rules="[{ required: true, min: 6, message: '密码至少6位' }]">
          <a-input-password v-model:value="form.password" placeholder="密码">
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>

        <a-form-item name="nickname">
          <a-input v-model:value="form.nickname" placeholder="昵称（可选）">
            <template #prefix><SmileOutlined /></template>
          </a-input>
        </a-form-item>

        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading" block>
            注册
          </a-button>
        </a-form-item>

        <a-form-item>
          <router-link to="/login">已有账号？立即登录</router-link>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, MailOutlined, SmileOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  nickname: ''
})

const loading = ref(false)

async function handleRegister() {
  loading.value = true
  try {
    const result = await authService.register(form.value)
    authStore.setToken(result.access_token)
    authStore.setUser(result.user)
    message.success('注册成功')
    router.push('/')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
