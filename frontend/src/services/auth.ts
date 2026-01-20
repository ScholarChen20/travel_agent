import axios from '@/utils/axios'

interface LoginRequest {
  username: string
  password: string
  captcha_code: string
  captcha_session_id: string
  device_id?: string
}

interface RegisterRequest {
  username: string
  email: string
  password: string
  nickname?: string
  captcha_code: string
  captcha_session_id: string
}

interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    username: string
    email: string
    nickname?: string
    avatar_url?: string
    role: 'user' | 'admin'
    is_verified: boolean
  }
}

export const authService = {
  async getCaptcha() {
    const response = await axios.get('/api/auth/captcha')
    return response.data
  },

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await axios.post('/api/auth/login', data)
    return response.data
  },

  async register(data: RegisterRequest): Promise<LoginResponse> {
    const response = await axios.post('/api/auth/register', data)
    return response.data
  },

  async getCurrentUser() {
    const response = await axios.get('/api/auth/me')
    return response.data
  },

  async verifyEmail(token: string) {
    const response = await axios.get(`/api/auth/verify-email?token=${token}`)
    return response.data
  },

  async requestPasswordReset(email: string) {
    const response = await axios.post('/api/auth/forgot-password', { email })
    return response.data
  },

  async resetPassword(token: string, newPassword: string) {
    const response = await axios.post('/api/auth/reset-password', {
      token,
      new_password: newPassword
    })
    return response.data
  }
}
