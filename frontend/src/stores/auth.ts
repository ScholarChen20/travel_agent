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
  // 从localStorage加载token和user信息
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))
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
