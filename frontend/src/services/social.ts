import axios from '@/utils/axios'

interface Post {
  id: string
  user_id: number
  username: string
  user_avatar?: string
  content: string
  media_urls: string[]
  tags: string[]
  likes_count: number
  comments_count: number
  is_liked: boolean
  moderation_status: 'pending' | 'approved' | 'rejected'
  created_at: string
}

interface CreatePostRequest {
  content: string
  tags?: string[]
  media_urls?: string[]
}

interface Comment {
  id: string
  user_id: number
  username: string
  user_avatar?: string
  content: string
  created_at: string
}

export const socialService = {
  async getFeed(limit = 20, offset = 0): Promise<Post[]> {
    try {
      const response = await axios.get('/api/social/posts', {
        params: { limit, offset }
      })
      // 适配新的响应格式
      return response.data.data?.posts || response.data.posts || []
    } catch (error) {
      console.error('API请求失败:', error)
      throw error
    }
  },

  async createPost(data: CreatePostRequest): Promise<Post> {
    const response = await axios.post('/api/social/posts', data)
    return response.data.data || response.data
  },

  async getPost(postId: string): Promise<Post> {
    const response = await axios.get(`/api/social/posts/${postId}`)
    return response.data.data || response.data
  },

  async deletePost(postId: string): Promise<void> {
    await axios.delete(`/api/social/posts/${postId}`)
  },

  async likePost(postId: string): Promise<void> {
    await axios.post(`/api/social/posts/${postId}/like`)
  },

  async unlikePost(postId: string): Promise<void> {
    // Backend uses same endpoint to toggle like/unlike
    await axios.post(`/api/social/posts/${postId}/like`)
  },

  async getComments(postId: string, limit = 50, offset = 0): Promise<Comment[]> {
    const response = await axios.get(`/api/social/posts/${postId}/comments`, {
      params: { limit, offset }
    })
    // 适配新的响应格式
    return response.data.data?.comments || response.data.comments || []
  },

  async addComment(postId: string, content: string): Promise<Comment> {
    const response = await axios.post(`/api/social/posts/${postId}/comments`, {
      content
    })
    return response.data.data || response.data
  },

  async uploadMedia(file: File): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post('/api/social/posts/media', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data.data || response.data
  },

  async followUser(userId: number): Promise<void> {
    await axios.post(`/api/social/users/${userId}/follow`)
  },

  async unfollowUser(userId: number): Promise<void> {
    // Backend uses same endpoint to toggle follow/unfollow
    await axios.post(`/api/social/users/${userId}/follow`)
  },

  async getUserPosts(userId: number, limit = 20, offset = 0): Promise<Post[]> {
    const response = await axios.get(`/api/social/users/${userId}/posts`, {
      params: { limit, offset }
    })
    return response.data.data?.posts || response.data.posts || []
  },

  async getPopularTags(limit = 20): Promise<Array<{ tag: string; count: number }>> {
    const response = await axios.get('/api/social/tags', {
      params: { limit }
    })
    return response.data.data?.tags || response.data.tags || []
  }
}
