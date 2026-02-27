import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
// @ts-ignore
import 'ant-design-vue/dist/reset.css'
import '@/assets/styles/design-tokens.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth'

const app = createApp(App)
const pinia = createPinia()

// @ts-ignore
app.use(pinia)
app.use(router)
app.use(Antd)

// 初始化authStore
const authStore = useAuthStore()


// 只有当token存在且user不存在时，才尝试获取用户信息
if (authStore.isAuthenticated && !authStore.user) {
  console.log('main.ts: 有token但没有user信息，尝试从API获取...')
  authService.getCurrentUser()
    .then(user => {
      console.log('main.ts: 从API获取用户信息成功:', user)
      authStore.setUser(user)
    })
    .catch(error => {
      console.error('main.ts: 获取用户信息失败:', error)
      // 如果获取失败，不要清除已有的token和user信息
      // 保留localStorage中的用户信息（如果有）
    })
}

app.mount('#app')

