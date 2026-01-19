<template>
  <div class="chat-container">
    <a-layout style="height: 100vh">
      <a-layout-sider width="300" style="background: #fff; border-right: 1px solid #f0f0f0">
        <div style="padding: 16px; border-bottom: 1px solid #f0f0f0">
          <a-button type="primary" block @click="createNewSession">
            <PlusOutlined /> 新建对话
          </a-button>
        </div>
        <a-list :data-source="dialogStore.sessions" :loading="loading">
          <template #renderItem="{ item }">
            <a-list-item
              :class="{ active: item.id === dialogStore.currentSessionId }"
              @click="selectSession(item.id)"
              style="cursor: pointer"
            >
              <a-list-item-meta>
                <template #title>{{ item.title }}</template>
                <template #description>{{ item.message_count }} 条消息</template>
              </a-list-item-meta>
              <template #actions>
                <a-button type="text" danger size="small" @click.stop="deleteSession(item.id)">
                  <DeleteOutlined />
                </a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-layout-sider>

      <a-layout-content style="display: flex; flex-direction: column">
        <div class="messages-container" ref="messagesRef">
          <div v-for="msg in dialogStore.messages" :key="msg.id" :class="['message', msg.role]">
            <div class="message-content">
              <a-avatar v-if="msg.role === 'user'" style="background-color: #1890ff">
                <UserOutlined />
              </a-avatar>
              <a-avatar v-else style="background-color: #52c41a">
                <RobotOutlined />
              </a-avatar>
              <div class="message-text">{{ msg.content }}</div>
            </div>
          </div>
        </div>

        <div class="input-container">
          <a-input-search
            v-model:value="inputMessage"
            placeholder="输入消息..."
            :loading="sending"
            @search="sendMessage"
            size="large"
          >
            <template #enterButton>
              <a-button type="primary">
                <SendOutlined />
              </a-button>
            </template>
          </a-input-search>
        </div>
      </a-layout-content>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined, DeleteOutlined, UserOutlined, RobotOutlined, SendOutlined } from '@ant-design/icons-vue'
import { useDialogStore } from '@/stores/dialog'
import { useAuthStore } from '@/stores/auth'
import { dialogService } from '@/services/dialog'

const dialogStore = useDialogStore()
const authStore = useAuthStore()

const loading = ref(false)
const sending = ref(false)
const inputMessage = ref('')
const messagesRef = ref<HTMLElement>()
let ws: WebSocket | null = null

onMounted(async () => {
  await loadSessions()
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})

async function loadSessions() {
  loading.value = true
  try {
    const sessions = await dialogService.getSessions()
    dialogStore.setSessions(sessions)
    if (sessions.length > 0 && !dialogStore.currentSessionId) {
      await selectSession(sessions[0].id)
    }
  } catch (error) {
    message.error('加载会话失败')
  } finally {
    loading.value = false
  }
}

async function createNewSession() {
  try {
    const result = await dialogService.createSession()
    await loadSessions()
    await selectSession(result.session_id)
    message.success('创建会话成功')
  } catch (error) {
    message.error('创建会话失败')
  }
}

async function selectSession(sessionId: string) {
  dialogStore.setCurrentSession(sessionId)
  try {
    const messages = await dialogService.getMessages(sessionId)
    dialogStore.setMessages(messages)
    connectWebSocket(sessionId)
    await nextTick()
    scrollToBottom()
  } catch (error) {
    message.error('加载消息失败')
  }
}

async function deleteSession(sessionId: string) {
  try {
    await dialogService.deleteSession(sessionId)
    dialogStore.removeSession(sessionId)
    if (dialogStore.currentSessionId === sessionId) {
      dialogStore.setCurrentSession(null)
      if (ws) {
        ws.close()
      }
    }
    message.success('删除成功')
  } catch (error) {
    message.error('删除失败')
  }
}

function connectWebSocket(sessionId: string) {
  if (ws) {
    ws.close()
  }

  ws = dialogService.createWebSocket(sessionId, authStore.token!)

  ws.onopen = () => {
    dialogStore.isConnected = true
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'message') {
      dialogStore.addMessage(data.message)
      scrollToBottom()
    }
  }

  ws.onclose = () => {
    dialogStore.isConnected = false
  }

  ws.onerror = () => {
    message.error('WebSocket连接错误')
  }
}

async function sendMessage() {
  if (!inputMessage.value.trim() || !dialogStore.currentSessionId) return

  const userMessage = inputMessage.value
  inputMessage.value = ''
  sending.value = true

  try {
    dialogStore.addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    })
    scrollToBottom()

    const response = await dialogService.chat(dialogStore.currentSessionId, {
      message: userMessage
    })

    dialogStore.addMessage({
      id: Date.now().toString(),
      role: 'assistant',
      content: response.response,
      timestamp: response.timestamp,
      tool_calls: response.tool_calls
    })
    scrollToBottom()
  } catch (error) {
    message.error('发送���息失败')
  } finally {
    sending.value = false
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.chat-container {
  height: 100vh;
}

.active {
  background-color: #e6f7ff;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f5f5;
}

.message {
  margin-bottom: 16px;
}

.message-content {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message.user .message-content {
  flex-direction: row-reverse;
}

.message-text {
  max-width: 60%;
  padding: 12px 16px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message.user .message-text {
  background: #1890ff;
  color: white;
}

.input-container {
  padding: 16px;
  background: white;
  border-top: 1px solid #f0f0f0;
}
</style>
