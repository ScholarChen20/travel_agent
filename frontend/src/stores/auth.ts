import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
  id: number
  username: string
  email: string
  nickname?: string
  avatar_url?: string
  role: 'user' | 'admin'
  is_verified: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // 直接从localStorage加载token
  const token = ref<string | null>(localStorage.getItem('token'))
  
  // 直接从localStorage加载user
  const user = ref<User | null>(null)
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      user.value = JSON.parse(userStr)
      // console.log('authStore: 从localStorage加载用户信息成功:', user.value)
    } else {
      console.log('authStore: localStorage中没有用户信息')
    }
  } catch (e) {
    console.error('authStore: 解析用户信息失败:', e)
    // 解析失败时，清空localStorage中的用户信息
    localStorage.removeItem('user')
  }
  
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  function setUser(newUser: User | null) {
    user.value = newUser
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser))
    } else {
      localStorage.removeItem('user')
    }
  }

  function logout() {
    setToken(null)
    setUser(null)
  }

  return {
    token,
    user,
    isLoading,
    isAuthenticated,
    isAdmin,
    setToken,
    setUser,
    logout
  }
})
