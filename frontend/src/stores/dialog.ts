import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  tool_calls?: any[]
  suggestions?: string[]
  thinking?: boolean
}

interface Session {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export const useDialogStore = defineStore('dialog', () => {
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const isConnected = ref(false)

  function setCurrentSession(sessionId: string | null) {
    currentSessionId.value = sessionId
    if (!sessionId) {
      messages.value = []
    }
  }

  function addMessage(message: Message) {
    messages.value.push(message)
  }

  function setMessages(newMessages: Message[]) {
    messages.value = newMessages
  }

  function setSessions(newSessions: Session[]) {
    sessions.value = newSessions
  }

  function addSession(session: Session) {
    sessions.value.unshift(session)
  }

  function updateSession(sessionId: string, updates: Partial<Session>) {
    const index = sessions.value.findIndex(s => s.id === sessionId)
    if (index !== -1) {
      sessions.value[index] = { ...sessions.value[index], ...updates }
    }
  }

  function removeSession(sessionId: string) {
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
  }

  function replaceMessage(id: string, newMessage: Message) {
    const index = messages.value.findIndex(m => m.id === id)
    if (index !== -1) {
      messages.value[index] = newMessage
    }
  }

  function removeMessageById(id: string) {
    messages.value = messages.value.filter(m => m.id !== id)
  }

  return {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    isConnected,
    setCurrentSession,
    addMessage,
    setMessages,
    setSessions,
    addSession,
    updateSession,
    removeSession,
    replaceMessage,
    removeMessageById
  }
})
