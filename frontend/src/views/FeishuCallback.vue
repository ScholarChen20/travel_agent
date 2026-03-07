<template>
  <div class="callback-container">
    <div class="callback-content">
      <a-spin size="large" />
      <p class="callback-tip">正在完成飞书授权登录，请稍候...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  const code = route.query.code as string
  const state = route.query.state as string

  if (!code || !state) {
    message.error('授权参数缺失，请重新登录')
    router.replace('/login')
    return
  }

  try {
    const result = await authService.feishuCallback(code, state)
    authStore.setToken(result.access_token)
    authStore.setUser(result.user)

    if (result.is_new_user) {
      message.success('飞书授权成功，欢迎加入！')
    } else {
      message.success('飞书授权登录成功')
    }

    const redirect = (route.query.redirect as string) || '/'
    router.replace(redirect)
  } catch (error: any) {
    const detail = error.response?.data?.detail || '飞书授权失败，请重试'
    message.error(detail)
    router.replace('/login')
  }
})
</script>

<style scoped>
.callback-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-light-gradient);
}

.callback-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.callback-tip {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}
</style>
