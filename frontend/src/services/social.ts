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
    const response = await axios.get('/api/social/feed', {
      params: { limit, offset }
    })
    return response.data
  },

  async createPost(data: CreatePostRequest): Promise<Post> {
    const response = await axios.post('/api/social/posts', data)
    return response.data
  },

  async getPost(postId: string): Promise<Post> {
    const response = await axios.get(`/api/social/posts/${postId}`)
    return response.data
  },

  async deletePost(postId: string): Promise<void> {
    await axios.delete(`/api/social/posts/${postId}`)
  },

  async likePost(postId: string): Promise<void> {
    await axios.post(`/api/social/posts/${postId}/like`)
  },

  async unlikePost(postId: string): Promise<void> {
    await axios.delete(`/api/social/posts/${postId}/like`)
  },

  async getComments(postId: string, limit = 50, offset = 0): Promise<Comment[]> {
    const response = await axios.get(`/api/social/posts/${postId}/comments`, {
      params: { limit, offset }
    })
    return response.data
  },

  async addComment(postId: string, content: string): Promise<Comment> {
    const response = await axios.post(`/api/social/posts/${postId}/comments`, {
      content
    })
    return response.data
  },

  async uploadMedia(file: File): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post('/api/social/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  async followUser(userId: number): Promise<void> {
    await axios.post(`/api/social/users/${userId}/follow`)
  },

  async unfollowUser(userId: number): Promise<void> {
    await axios.delete(`/api/social/users/${userId}/follow`)
  },

  async getUserPosts(userId: number, limit = 20, offset = 0): Promise<Post[]> {
    const response = await axios.get(`/api/social/users/${userId}/posts`, {
      params: { limit, offset }
    })
    return response.data
  },

  async getPopularTags(limit = 20): Promise<Array<{ tag: string; count: number }>> {
    const response = await axios.get('/api/social/tags/popular', {
      params: { limit }
    })
    return response.data
  }
}
