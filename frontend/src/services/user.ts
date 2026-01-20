import axios from '@/utils/axios'

interface UserProfile {
  id: number
  username: string
  email: string
  role: 'user' | 'admin'
  avatar_url?: string
  is_verified: boolean
  is_active: boolean
  created_at: string
  last_login_at?: string
  profile: {
    travel_preferences: string[]
    visited_cities: string[]
    travel_stats: {
      total_trips: number
      total_cities: number
      favorite_trips: number
      completed_trips: number
    }
  }
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
    const response = await axios.get('/api/user/profile')
    return response.data
  },

  async updateProfile(data: UpdateProfileRequest): Promise<UserProfile> {
    // 转换为后端需要的数据结构
    const backendData = {
      travel_preferences: [
        data.nickname ? `nickname:${data.nickname}` : '',
        data.bio ? `bio:${data.bio}` : '',
        data.location ? `location:${data.location}` : ''
      ].filter(Boolean)
    }
    const response = await axios.put('/api/user/profile', backendData)
    return response.data
  },

  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post('/api/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async getStats(): Promise<UserStats> {
    const response = await axios.get('/api/user/stats')
    return response.data
  },

  async getVisitedCities(): Promise<string[]> {
    const response = await axios.get('/api/user/visited-cities')
    return response.data
  },

  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await axios.post('/api/user/change-password', data)
  }
}
