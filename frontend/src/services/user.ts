import axios from '@/utils/axios'

interface UserProfile {
  id: number
  username: string
  email: string
  nickname?: string
  avatar?: string
  bio?: string
  location?: string
  role: 'user' | 'admin'
  is_verified: boolean
  created_at: string
}

interface UpdateProfileRequest {
  nickname?: string
  bio?: string
  location?: string
}

interface UserStats {
  plans_count: number
  posts_count: number
  followers_count: number
  following_count: number
  likes_received: number
}

interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export const userService = {
  async getProfile(): Promise<UserProfile> {
    const response = await axios.get('/api/users/profile')
    return response.data
  },

  async updateProfile(data: UpdateProfileRequest): Promise<UserProfile> {
    const response = await axios.put('/api/users/profile', data)
    return response.data
  },

  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post('/api/users/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async getStats(): Promise<UserStats> {
    const response = await axios.get('/api/users/stats')
    return response.data
  },

  async getVisitedCities(): Promise<string[]> {
    const response = await axios.get('/api/users/visited-cities')
    return response.data
  },

  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await axios.post('/api/users/change-password', data)
  }
}
