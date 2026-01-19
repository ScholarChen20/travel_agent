<template>
  <a-card>
    <div style="text-align: center">
      <a-avatar :size="100" :src="profile.avatar">
        {{ profile.username[0] }}
      </a-avatar>
      <a-upload
        v-if="editable"
        :show-upload-list="false"
        :before-upload="handleUpload"
        accept="image/*"
      >
        <a-button type="link" style="margin-top: 8px">
          <UploadOutlined /> 更换头像
        </a-button>
      </a-upload>
      <h2 style="margin-top: 16px">{{ profile.nickname || profile.username }}</h2>
      <p style="color: #999">@{{ profile.username }}</p>
      <a-tag v-if="profile.role === 'admin'" color="red">管理员</a-tag>
      <a-tag v-if="profile.is_verified" color="green">已验证</a-tag>
    </div>

    <a-divider />

    <a-descriptions :column="1" size="small">
      <a-descriptions-item label="邮箱">{{ profile.email }}</a-descriptions-item>
      <a-descriptions-item label="位置">{{ profile.location || '未设置' }}</a-descriptions-item>
      <a-descriptions-item label="注册时间">{{ profile.created_at }}</a-descriptions-item>
    </a-descriptions>
  </a-card>
</template>

<script setup lang="ts">
import { UploadOutlined } from '@ant-design/icons-vue'

defineProps<{
  profile: {
    username: string
    nickname?: string
    avatar?: string
    email: string
    location?: string
    role: string
    is_verified: boolean
    created_at: string
  }
  editable?: boolean
}>()

const emit = defineEmits<{
  uploadAvatar: [file: File]
}>()

function handleUpload(file: File) {
  emit('uploadAvatar', file)
  return false
}
</script>
