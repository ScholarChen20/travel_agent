import axios from '@/utils/axios'

interface ProfileDetail {
  full_name?: string
  gender?: string
  birth_date?: string
  location?: string
  travel_preferences: string[]
  visited_cities: string[]
  travel_stats: {
    total_trips?: number
    total_cities?: number
    favorite_trips?: number
    completed_trips?: number
  }
}

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
  profile: ProfileDetail
}

interface UpdateProfileRequest {
  username?: string
  email?: string
  full_name?: string
  gender?: string
  birth_date?: string
  location?: string
  travel_preferences?: string[]
}

interface UserStats {
  total_trips?: number
  completed_trips?: number
  favorite_trips?: number
  total_cities?: number
  plans_count?: number
  posts_count?: number
  followers_count?: number
  following_count?: number
  likes_received?: number
}

interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export const userService = {
  async getProfile(): Promise<UserProfile> {
    const response = await axios.get('/user/profile')
    return response.data.data
  },

  async updateProfile(data: UpdateProfileRequest): Promise<void> {
    await axios.put('/user/profile', data)
  },

  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post('/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data.data
  },

  async getStats(): Promise<UserStats> {
    const response = await axios.get('/user/stats')
    return response.data.data
  },

  async getVisitedCities(): Promise<string[]> {
    const response = await axios.get('/user/visited-cities')
    const data = response.data.data
    return data?.cities || data || []
  },

  async updateVisitedCities(cities: string[]): Promise<string[]> {
    const response = await axios.put('/user/visited-cities', { cities })
    const data = response.data.data
    return data?.cities || data || []
  },

  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await axios.post('/user/change-password', data)
  }
}
