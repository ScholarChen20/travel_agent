import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  tool_calls?: any[]
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

  function updateSession(sessionId: string, updates: Partial<Session>) {
    const index = sessions.value.findIndex(s => s.id === sessionId)
    if (index !== -1) {
      sessions.value[index] = { ...sessions.value[index], ...updates }
    }
  }

  function removeSession(sessionId: string) {
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
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
    updateSession,
    removeSession
  }
})
