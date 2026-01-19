import axios from '@/utils/axios'

interface CreateSessionResponse {
  session_id: string
  created_at: string
}

interface ChatRequest {
  message: string
}

interface ChatResponse {
  response: string
  tool_calls?: any[]
  timestamp: string
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
    const response = await axios.post('/api/dialog/sessions')
    return response.data
  },

  async chat(sessionId: string, data: ChatRequest): Promise<ChatResponse> {
    const response = await axios.post(`/api/dialog/sessions/${sessionId}/chat`, data)
    return response.data
  },

  async getSessions(): Promise<Session[]> {
    const response = await axios.get('/api/dialog/sessions')
    return response.data
  },

  async getSession(sessionId: string): Promise<Session> {
    const response = await axios.get(`/api/dialog/sessions/${sessionId}`)
    return response.data
  },

  async deleteSession(sessionId: string): Promise<void> {
    await axios.delete(`/api/dialog/sessions/${sessionId}`)
  },

  async getMessages(sessionId: string): Promise<Message[]> {
    const response = await axios.get(`/api/dialog/sessions/${sessionId}/messages`)
    return response.data
  },

  createWebSocket(sessionId: string, token: string): WebSocket {
    const wsUrl = `ws://localhost:8000/api/dialog/ws/${sessionId}?token=${token}`
    return new WebSocket(wsUrl)
  }
}
