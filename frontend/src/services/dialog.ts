import axios from '@/utils/axios'

interface CreateSessionResponse {
  session_id: string
  message: string
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
    const response = await axios.post('/api/dialog/sessions', { initial_context: {} })
    return response.data
  },

  async chat(sessionId: string, data: ChatRequest): Promise<ChatResponse> {
    const response = await axios.post('/api/dialog/chat', {
      session_id: sessionId,
      message: data.message
    })
    return response.data
  },

  async getSessions(): Promise<Session[]> {
    const response = await axios.get('/api/dialog/sessions')
    const raw: any[] = response.data.sessions || []
    return raw.map(s => ({
      ...s,
      id: s.id ?? s.session_id,
    }))
  },

  async getSession(sessionId: string): Promise<{ messages: Message[] }> {
    const response = await axios.get(`/api/dialog/sessions/${sessionId}`)
    return response.data
  },

  async deleteSession(sessionId: string): Promise<void> {
    await axios.delete(`/api/dialog/sessions/${sessionId}`)
  },

  async updateSessionTitle(sessionId: string, title: string): Promise<void> {
    await axios.patch(`/api/dialog/sessions/${sessionId}`, { title })
  },

  async getMessages(sessionId: string): Promise<Message[]> {
    const response = await axios.get(`/api/dialog/sessions/${sessionId}`)
    return response.data.messages || []
  },

  /**
   * 建立 SSE 连接。token 通过 query param 传递（EventSource 不支持自定义请求头）。
   */
  createSSE(sessionId: string, token: string): EventSource {
    const baseUrl = (axios.defaults.baseURL || '').replace(/\/$/, '')
    const url = `${baseUrl}/api/dialog/sse/${sessionId}?token=${encodeURIComponent(token)}`
    return new EventSource(url)
  }
}
