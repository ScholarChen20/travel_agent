<template>
  <div class="chat-container">
    <a-layout style="height: 100vh">
      <!-- 左侧会话列表 -->
      <a-layout-sider width="280" style="background: #fff; border-right: 1px solid #f0f0f0; display: flex; flex-direction: column">
        <div style="padding: 16px; border-bottom: 1px solid #f0f0f0">
          <a-button type="text" size="small" class="back-home-btn" @click="router.push('/')">
            <LeftOutlined /> 返回首页
          </a-button>
          <a-button type="primary" block @click="createNewSession">
            <PlusOutlined /> 新建对话
          </a-button>
        </div>
        <a-list :data-source="dialogStore.sessions" :loading="loading" style="flex: 1; overflow-y: auto">
          <template #renderItem="{ item }">
            <a-list-item
              :class="{ active: item.id === dialogStore.currentSessionId }"
              @click="editingSessionId !== item.id && selectSession(item.id)"
              style="cursor: pointer; padding: 8px 16px"
              class="session-item"
            >
              <!-- 编辑模式：显示输入框 -->
              <div v-if="editingSessionId === item.id" class="session-edit-wrap" @click.stop>
                <a-input
                  ref="editInputRef"
                  v-model:value="editingTitle"
                  size="small"
                  @keyup.enter="saveTitle(item.id)"
                  @blur="saveTitle(item.id)"
                />
              </div>
              <!-- 展示模式 -->
              <a-list-item-meta v-else>
                <template #title>{{ item.title || '新对话' }}</template>
                <template #description>{{ item.message_count }} 条消息</template>
              </a-list-item-meta>
              <template #actions>
                <a-button
                  v-if="editingSessionId !== item.id"
                  type="text"
                  size="small"
                  class="edit-btn"
                  @click.stop="startEdit($event, item)"
                >
                  <EditOutlined />
                </a-button>
                <a-button type="text" danger size="small" @click.stop="deleteSession(item.id)">
                  <DeleteOutlined />
                </a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-layout-sider>

      <!-- 右侧对话区域 -->
      <a-layout-content style="display: flex; flex-direction: column; background: #f5f7fa">
        <!-- 顶部状态栏 -->
        <div class="chat-header">
          <span class="header-title">
            {{ currentSessionTitle || '智能旅行助手' }}
          </span>
          <a-badge :status="sseConnected ? 'success' : 'default'" :text="sseConnected ? '已连接' : '未连接'" />
        </div>

        <!-- 消息列表 -->
        <div class="messages-container" ref="messagesRef">
          <!-- 空状态 -->
          <div v-if="dialogStore.messages.length === 0" class="empty-chat">
            <div class="empty-icon">🤖</div>
            <h3>我是智能旅行规划助手</h3>
            <p>您可以问我景点介绍、城市攻略、行程规划等旅行相关问题</p>
            <div class="quick-start">
              <a-button v-for="tip in quickStartTips" :key="tip" size="small" @click="sendQuick(tip)">
                {{ tip }}
              </a-button>
            </div>
          </div>

          <div v-for="msg in dialogStore.messages" :key="msg.id" :class="['message', msg.role]">
            <div class="message-content">
              <a-avatar v-if="msg.role === 'user'" style="background-color: #1890ff; flex-shrink: 0">
                <UserOutlined />
              </a-avatar>
              <a-avatar v-else style="background-color: #52c41a; flex-shrink: 0">
                <RobotOutlined />
              </a-avatar>
              <div class="bubble-wrap">
                <div class="message-text" :class="{ 'message-text--thinking': msg.thinking }">
                  <a-spin v-if="msg.thinking" size="small" />
                  <span v-else>{{ msg.content }}</span>
                </div>
                <!-- 快捷建议按钮 -->
                <div v-if="msg.suggestions && msg.suggestions.length > 0 && !msg.thinking" class="suggestions">
                  <a-button
                    v-for="s in msg.suggestions"
                    :key="s"
                    size="small"
                    class="suggestion-btn"
                    @click="sendQuick(s)"
                  >
                    {{ s }}
                  </a-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="input-container">
          <a-input-search
            v-model:value="inputMessage"
            placeholder="输入消息，回车发送..."
            :loading="sending"
            :disabled="!dialogStore.currentSessionId"
            @search="sendMessage"
            size="large"
            @keyup.enter.prevent="sendMessage"
          >
            <template #enterButton>
              <a-button type="primary" :disabled="!dialogStore.currentSessionId">
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  PlusOutlined, DeleteOutlined, UserOutlined,
  RobotOutlined, SendOutlined, LeftOutlined, EditOutlined
} from '@ant-design/icons-vue'
import { useDialogStore } from '@/stores/dialog'
import { useAuthStore } from '@/stores/auth'
import { dialogService } from '@/services/dialog'

const router = useRouter()
const dialogStore = useDialogStore()
const authStore = useAuthStore()

const loading = ref(false)
const sending = ref(false)
const sseConnected = ref(false)
const inputMessage = ref('')
const messagesRef = ref<HTMLElement>()
let eventSource: EventSource | null = null

// 会话名编辑
const editingSessionId = ref<string | null>(null)
const editingTitle = ref('')
const editInputRef = ref<any>()

const quickStartTips = ['故宫有什么好玩的？', '帮我规划北京3日游', '三亚旅游攻略', '成都美食推荐']

const currentSessionTitle = computed(() => {
  const session = dialogStore.sessions.find(s => s.id === dialogStore.currentSessionId)
  return session?.title || ''
})

onMounted(async () => {
  await loadSessions()
})

onUnmounted(() => {
  closeSSE()
})

async function loadSessions() {
  loading.value = true
  try {
    const sessions = await dialogService.getSessions()
    dialogStore.setSessions(sessions)
    if (sessions.length > 0 && !dialogStore.currentSessionId) {
      await selectSession(sessions[0].id)
    }
  } catch (error: any) {
    console.error('加载会话失败:', error)
    message.error(error.response?.data?.detail || '加载会话失败')
  } finally {
    loading.value = false
  }
}

async function createNewSession() {
  try {
    const result = await dialogService.createSession()
    // 直接写入 store，不重新拉取（避免 Redis 缓存未失效导致新会话不显示）
    dialogStore.addSession({
      id: result.session_id,
      title: '',
      message_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })
    await selectSession(result.session_id)
    message.success('创建成功')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '创建会话失败')
  }
}

function startEdit(e: Event, session: any) {
  editingSessionId.value = session.id
  editingTitle.value = session.title || '新对话'
  nextTick(() => editInputRef.value?.focus())
}

async function saveTitle(sessionId: string) {
  if (editingSessionId.value !== sessionId) return
  const title = editingTitle.value.trim() || '新对话'
  editingSessionId.value = null
  dialogStore.updateSession(sessionId, { title })
  try {
    await dialogService.updateSessionTitle(sessionId, title)
  } catch {
    message.error('保存名称失败')
  }
}

async function selectSession(sessionId: string) {
  dialogStore.setCurrentSession(sessionId)
  try {
    const messages = await dialogService.getMessages(sessionId)
    dialogStore.setMessages(messages)
    connectSSE(sessionId)
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
      closeSSE()
    }
    message.success('删除成功')
  } catch {
    message.error('删除失败')
  }
}

function connectSSE(sessionId: string) {
  closeSSE()
  if (!authStore.token) return

  eventSource = dialogService.createSSE(sessionId, authStore.token)

  eventSource.onopen = () => {
    sseConnected.value = true
  }

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'connected') {
        sseConnected.value = true
      }
      // heartbeat 不处理
    } catch (e) {
      console.error('SSE 消息解析失败:', e)
    }
  }

  eventSource.onerror = () => {
    sseConnected.value = false
  }
}

function closeSSE() {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
  sseConnected.value = false
}

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text || !dialogStore.currentSessionId) return

  const isFirstMessage = dialogStore.messages.length === 0
  const sessionId = dialogStore.currentSessionId

  inputMessage.value = ''
  sending.value = true

  // 立即显示用户消息
  dialogStore.addMessage({
    id: Date.now().toString(),
    role: 'user',
    content: text,
    timestamp: new Date().toISOString()
  })
  scrollToBottom()

  // 显示"思考中"占位
  const thinkingId = `thinking-${Date.now()}`
  dialogStore.addMessage({
    id: thinkingId,
    role: 'assistant',
    content: '',
    timestamp: new Date().toISOString(),
    thinking: true
  } as any)
  scrollToBottom()

  try {
    const response = await dialogService.chat(sessionId, { message: text })

    // 用真实回复替换"思考中"占位
    dialogStore.replaceMessage(thinkingId, {
      id: Date.now().toString(),
      role: 'assistant',
      content: response.message,
      timestamp: new Date().toISOString(),
      suggestions: response.suggestions
    } as any)

    // 更新侧边栏消息计数
    const sess = dialogStore.sessions.find(s => s.id === sessionId)
    if (sess) {
      dialogStore.updateSession(sessionId, { message_count: sess.message_count + 2 })
    }

    // 首条消息：用用户输入内容设为会话标题，持久化到后端
    if (isFirstMessage) {
      const title = text.length > 20 ? text.slice(0, 20) + '…' : text
      dialogStore.updateSession(sessionId, { title })
      try {
        await dialogService.updateSessionTitle(sessionId, title)
      } catch {
        // 标题保存失败不影响主流程
      }
    }

    scrollToBottom()
  } catch (error) {
    dialogStore.removeMessageById(thinkingId)
    message.error('发送消息失败')
  } finally {
    sending.value = false
  }
}

function sendQuick(text: string) {
  inputMessage.value = text
  sendMessage()
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

.back-home-btn {
  display: block;
  width: 100%;
  margin-bottom: 8px;
  text-align: left;
  color: #666;
}
.back-home-btn:hover { color: #1890ff; }

.active {
  background-color: #e6f7ff;
}

/* 会话列表项：hover 时才显示编辑按钮 */
.session-item .edit-btn {
  opacity: 0;
  transition: opacity 0.15s;
}
.session-item:hover .edit-btn {
  opacity: 1;
}

/* 编辑模式输入框 */
.session-edit-wrap {
  flex: 1;
  padding-right: 4px;
}

.chat-header {
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-title {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-chat {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-chat h3 { color: #333; margin-bottom: 8px; }
.quick-start { margin-top: 20px; display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }

.message {
  margin-bottom: 20px;
}

.message-content {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.message.user .message-content {
  flex-direction: row-reverse;
}

.bubble-wrap {
  max-width: 65%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message.user .bubble-wrap {
  align-items: flex-end;
}

.message-text {
  padding: 10px 14px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.user .message-text {
  background: #1890ff;
  color: white;
}

.message-text--thinking {
  min-width: 60px;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.suggestion-btn {
  border-radius: 12px;
  font-size: 12px;
  color: #1890ff;
  border-color: #91d5ff;
}

.input-container {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #f0f0f0;
}
</style>
