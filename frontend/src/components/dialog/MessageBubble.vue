<template>
  <div :class="['message-bubble', message.role]">
    <a-avatar v-if="message.role === 'user'" style="background-color: #1890ff">
      <UserOutlined />
    </a-avatar>
    <a-avatar v-else style="background-color: #52c41a">
      <RobotOutlined />
    </a-avatar>
    <div class="bubble-content">
      <div class="bubble-text">{{ message.content }}</div>
      <div class="bubble-time">{{ formatTime(message.timestamp) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { UserOutlined, RobotOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'

defineProps<{
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: string
  }
}>()

function formatTime(timestamp: string) {
  return dayjs(timestamp).format('HH:mm')
}
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: flex-start;
}

.message-bubble.user {
  flex-direction: row-reverse;
}

.bubble-content {
  max-width: 60%;
}

.bubble-text {
  padding: 12px 16px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-bubble.user .bubble-text {
  background: #1890ff;
  color: white;
}

.bubble-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.message-bubble.user .bubble-time {
  text-align: left;
}
</style>
