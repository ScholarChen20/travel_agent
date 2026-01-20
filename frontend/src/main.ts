import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
// @ts-ignore
import 'ant-design-vue/dist/reset.css'
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
if (authStore.isAuthenticated && !authStore.user) {
  // 如果有token但没有用户信息，自动获取用户信息
  authService.getCurrentUser()
    .then(user => {
      authStore.setUser(user)
    })
    .catch(error => {
      console.error('获取用户信息失败:', error)
      // 如果获取失败，清除token
      authStore.logout()
    })
}

app.mount('#app')

