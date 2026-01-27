import axios from '@/utils/axios'

interface CreateSessionResponse {
  session_id: string
  created_at: string
}

interface ChatRequest {
  message: string
}

interface ChatResponse {
  session_id: string
  message: string
  intent: string
  suggestions: string[]
}

interface Session {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  tool_calls?: any[]
}

export const dialogService = {
  async createSession(): Promise<CreateSessionResponse> {
    console.log('[Dialog] 创建会话...')
    try {
      const response = await axios.post('/api/dialog/sessions', {
        initial_context: {}
      })
      console.log('[Dialog] 会话创建成功:', response.data)
      return response.data
    } catch (error: any) {
      console.error('[Dialog] 创建会话失败:', error)
      throw error
    }
  },

  async chat(sessionId: string, data: ChatRequest): Promise<ChatResponse> {
    console.log('[Dialog] 发送消息:', { sessionId, message: data.message })
    try {
      const response = await axios.post('/api/dialog/chat', {
        session_id: sessionId,
        message: data.message
      })
      console.log('[Dialog] 收到回复:', response.data)
      return response.data
    } catch (error: any) {
      console.error('[Dialog] 发送消息失败:', error)
      throw error
    }
  },

  async getSessions(): Promise<Session[]> {
    console.log('[Dialog] 获取会话列表...')
    try {
      const response = await axios.get('/api/dialog/sessions')
      console.log('[Dialog] 会话列表:', response.data)
      return response.data.sessions || []
    } catch (error: any) {
      console.error('[Dialog] 获取会话列表失败:', error)
      throw error
    }
  },

  async getSession(sessionId: string): Promise<Session> {
    console.log('[Dialog] 获取会话详情:', sessionId)
    try {
      const response = await axios.get(`/api/dialog/sessions/${sessionId}`)
      console.log('[Dialog] 会话详情:', response.data)
      return response.data
    } catch (error: any) {
      console.error('[Dialog] 获取会话详情失败:', error)
      throw error
    }
  },

  async deleteSession(sessionId: string): Promise<void> {
    console.log('[Dialog] 删除会话:', sessionId)
    try {
      await axios.delete(`/api/dialog/sessions/${sessionId}`)
      console.log('[Dialog] 会话删除成功')
    } catch (error: any) {
      console.error('[Dialog] 删除会话失败:', error)
      throw error
    }
  },

  async getMessages(sessionId: string): Promise<Message[]> {
    console.log('[Dialog] 获取消息列表:', sessionId)
    try {
      const response = await axios.get(`/api/dialog/sessions/${sessionId}`)
      console.log('[Dialog] 消息列表:', response.data.messages)
      return response.data.messages || []
    } catch (error: any) {
      console.error('[Dialog] 获取消息列表失败:', error)
      throw error
    }
  },

  createWebSocket(sessionId: string, token: string): WebSocket {
    const wsUrl = `ws://localhost:8000/api/dialog/ws/${sessionId}?token=${token}`
    console.log('[Dialog] 创建WebSocket连接:', wsUrl)
    return new WebSocket(wsUrl)
  }
}
