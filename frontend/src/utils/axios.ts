import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'

const API_BASE_URL = 'http://localhost:8000'

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add Authorization header
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle 401 and errors
axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    const authStore = useAuthStore()

    if (error.response?.status === 401) {
      authStore.logout()
      message.error('登录已过期，请重新登录')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (error.response?.status === 403) {
      message.error('没有权限访问此资源')
      return Promise.reject(error)
    }

    if (error.response?.status === 500) {
      message.error('服务器错误，请稍后重试')
      return Promise.reject(error)
    }

    const errorMessage = (error.response?.data as any)?.detail || error.message || '请求失败'
    message.error(errorMessage)
    return Promise.reject(error)
  }
)

export default axiosInstance
