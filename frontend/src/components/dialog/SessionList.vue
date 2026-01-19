<template>
  <a-list :data-source="sessions" :loading="loading">
    <template #renderItem="{ item }">
      <a-list-item
        :class="{ active: item.id === currentSessionId }"
        @click="$emit('select', item.id)"
        style="cursor: pointer"
      >
        <a-list-item-meta>
          <template #title>{{ item.title }}</template>
          <template #description>{{ item.message_count }} 条消息</template>
        </a-list-item-meta>
        <template #actions>
          <a-button type="text" danger size="small" @click.stop="$emit('delete', item.id)">
            <DeleteOutlined />
          </a-button>
        </template>
      </a-list-item>
    </template>
  </a-list>
</template>

<script setup lang="ts">
import { DeleteOutlined } from '@ant-design/icons-vue'

defineProps<{
  sessions: Array<{
    id: string
    title: string
    message_count: number
  }>
  currentSessionId?: string | null
  loading?: boolean
}>()

defineEmits<{
  select: [sessionId: string]
  delete: [sessionId: string]
}>()
</script>

<style scoped>
.active {
  background-color: #e6f7ff;
}
</style>
