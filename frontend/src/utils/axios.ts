import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'

export const API_BASE_URL = 'http://localhost:8000'

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
    // 直接从localStorage获取令牌，因为useAuthStore只能在Vue组件中使用
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle 401 and errors
axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    // 直接操作localStorage，因为useAuthStore只能在Vue组件中使用
    if (error.response?.status === 401) {
      // 清除localStorage中的用户数据
      localStorage.removeItem('token')
      localStorage.removeItem('user')
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

    return Promise.reject(error)
  }
)

export default axiosInstance
