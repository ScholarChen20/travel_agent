<template>
  <a-list :data-source="comments" :loading="loading">
    <template #renderItem="{ item }">
      <a-list-item>
        <a-list-item-meta>
          <template #avatar>
            <a-avatar :src="item.user_avatar">{{ item.username[0] }}</a-avatar>
          </template>
          <template #title>{{ item.username }}</template>
          <template #description>{{ item.created_at }}</template>
        </a-list-item-meta>
        <div>{{ item.content }}</div>
      </a-list-item>
    </template>
  </a-list>
  <div style="margin-top: 16px">
    <a-input-search
      v-model:value="newComment"
      placeholder="写评论..."
      :loading="submitting"
      @search="handleSubmit"
    >
      <template #enterButton>发送</template>
    </a-input-search>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  comments: Array<{
    id: string
    user_id: number
    username: string
    user_avatar?: string
    content: string
    created_at: string
  }>
  loading?: boolean
  submitting?: boolean
}>()

const emit = defineEmits<{
  submit: [content: string]
}>()

const newComment = ref('')

function handleSubmit() {
  if (newComment.value.trim()) {
    emit('submit', newComment.value)
    newComment.value = ''
  }
}
</script>
