<template>
  <a-list-item>
    <template #actions>
      <span @click="$emit('like', post.id)" style="cursor: pointer">
        <HeartFilled v-if="post.is_liked" style="color: #ff4d4f" />
        <HeartOutlined v-else />
        {{ post.likes_count }}
      </span>
      <span @click="$emit('comment', post.id)" style="cursor: pointer">
        <CommentOutlined /> {{ post.comments_count }}
      </span>
    </template>
    <a-list-item-meta>
      <template #avatar>
        <a-avatar :src="post.user_avatar">{{ post.username[0] }}</a-avatar>
      </template>
      <template #title>{{ post.username }}</template>
      <template #description>{{ post.created_at }}</template>
    </a-list-item-meta>
    <div>{{ post.content }}</div>
    <div v-if="post.media_urls.length > 0" style="margin-top: 12px">
      <a-image-preview-group>
        <a-image
          v-for="(url, index) in post.media_urls"
          :key="index"
          :src="url"
          :width="200"
          style="margin-right: 8px"
        />
      </a-image-preview-group>
    </div>
    <div v-if="post.tags.length > 0" style="margin-top: 12px">
      <a-tag v-for="tag in post.tags" :key="tag" color="blue">#{{ tag }}</a-tag>
    </div>
  </a-list-item>
</template>

<script setup lang="ts">
import { HeartOutlined, HeartFilled, CommentOutlined } from '@ant-design/icons-vue'

defineProps<{
  post: {
    id: string
    user_id: number
    username: string
    user_avatar?: string
    content: string
    media_urls: string[]
    tags: string[]
    likes_count: number
    comments_count: number
    is_liked: boolean
    created_at: string
  }
}>()

defineEmits<{
  like: [postId: string]
  comment: [postId: string]
}>()
</script>
