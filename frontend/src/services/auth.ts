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
  is_new_user?: boolean
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
    const response = await axios.get('/auth/captcha')
    return response.data.data
  },

  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await axios.post('/auth/login', data)
    return response.data.data
  },

  async register(data: RegisterRequest): Promise<LoginResponse> {
    const response = await axios.post('/auth/register', data)
    return response.data.data
  },

  async getCurrentUser() {
    const response = await axios.get('/auth/me')
    return response.data.data
  },

  async verifyEmail(token: string) {
    const response = await axios.get(`/auth/verify-email?token=${token}`)
    return response.data.data
  },

  async requestPasswordReset(email: string) {
    const response = await axios.post('/auth/forgot-password', { email })
    return response.data.data
  },

  async resetPassword(token: string, newPassword: string) {
    const response = await axios.post('/auth/reset-password', {
      token,
      new_password: newPassword
    })
    return response.data.data
  },

  async getFeishuAuthorizeUrl(): Promise<{ authorize_url: string }> {
    const response = await axios.get('/auth/feishu/authorize')
    return response.data.data
  },

  async feishuCallback(code: string, state: string): Promise<LoginResponse> {
    const response = await axios.post('/auth/feishu/callback', { code, state })
    return response.data.data
  }
}
