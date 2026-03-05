import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'

export const API_BASE_URL = '/api'

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
    const data = error.response?.data as any
    const status = error.response?.status
    const url = error.config?.url || ''
    
    // 提取错误消息的通用函数
    const getErrorMessage = () => {
      // 优先使用 msg 字段
      if (data?.msg) {
        return data.msg
      }
      
      // 其次使用 detail 字段
      if (data?.detail) {
        if (typeof data.detail === 'string') {
          return data.detail
        }
        
        // FastAPI 验证错误，detail 是数组
        if (Array.isArray(data.detail) && data.detail.length > 0) {
          const firstError = data.detail[0]
          if (firstError?.msg) {
            // 根据字段类型提供更友好的中文提示
            const field = firstError.loc?.[1]
            if (field === 'username') {
              if (firstError.type === 'string_too_short') {
                return '用户名至少需要3个字符'
              } else if (firstError.type === 'string_too_long') {
                return '用户名不能超过50个字符'
              }
            } else if (field === 'email') {
              if (firstError.type === 'value_error.email') {
                return '邮箱格式不正确'
              }
            } else if (field === 'password') {
              if (firstError.type === 'string_too_short') {
                return '密码至少需要8个字符'
              }
            } else if (field === 'captcha_code') {
              if (firstError.type === 'string_too_short') {
                return '验证码格式不正确'
              }
            }
            return firstError.msg
          }
        }
      }
      
      // 默认错误消息
      return '请求失败，请稍后重试'
    }
    
    // 400 Bad Request - 请求参数错误
    if (status === 400) {
      message.error(getErrorMessage())
      return Promise.reject(error)
    }
    
    // 401 Unauthorized - 未授权
    if (status === 401) {
      // 登录/注册/飞书回调接口本身返回401，不做跳转，让业务层处理
      if (
        url.includes('/auth/login') ||
        url.includes('/auth/register') ||
        url.includes('/auth/feishu/')
      ) {
        return Promise.reject(error)
      }
      // 其他接口401 = token过期，清除并跳转登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      message.error('登录已过期，请重新登录')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    // 403 Forbidden - 禁止访问
    if (status === 403) {
      message.error(getErrorMessage())
      return Promise.reject(error)
    }

    // 404 Not Found - 资源不存在
    if (status === 404) {
      message.error(getErrorMessage())
      return Promise.reject(error)
    }

    // 422 Unprocessable Entity - 请求参数验证失败
    if (status === 422) {
      message.error(getErrorMessage())
      return Promise.reject(error)
    }

    // 429 Too Many Requests - 请求过于频繁
    if (status === 429) {
      message.error(getErrorMessage())
      return Promise.reject(error)
    }

    // 500 Internal Server Error - 服务器内部错误
    if (status === 500) {
      message.error(getErrorMessage())
      return Promise.reject(error)
    }

    // 其他未处理的状态码
    message.error(getErrorMessage())
    return Promise.reject(error)
  }
)

export default axiosInstance
