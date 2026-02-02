<template>
  <a-form :model="form" @finish="handleSubmit">
    <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
      <a-input v-model:value="form.username" placeholder="用户名" size="large">
        <template #prefix><UserOutlined /></template>
      </a-input>
    </a-form-item>

    <a-form-item name="email" :rules="[{ required: true, type: 'email', message: '请输入有效的邮箱' }]">
      <a-input v-model:value="form.email" placeholder="邮箱" size="large">
        <template #prefix><MailOutlined /></template>
      </a-input>
    </a-form-item>

    <a-form-item name="password" :rules="[{ required: true, min: 6, message: '密码至少6位' }]">
      <a-input-password v-model:value="form.password" placeholder="密码" size="large">
        <template #prefix><LockOutlined /></template>
      </a-input-password>
    </a-form-item>

    <a-form-item name="nickname">
      <a-input v-model:value="form.nickname" placeholder="昵称（可选）" size="large">
        <template #prefix><SmileOutlined /></template>
      </a-input>
    </a-form-item>

    <a-form-item>
      <a-button type="primary" html-type="submit" :loading="loading" block size="large">
        注册
      </a-button>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UserOutlined, LockOutlined, MailOutlined, SmileOutlined } from '@ant-design/icons-vue'

const emit = defineEmits<{
  submit: [data: { username: string; email: string; password: string; nickname?: string }]
}>()

defineProps<{
  loading?: boolean
}>()

const form = ref({
  username: '',
  email: '',
  password: '',
  nickname: ''
})

function handleSubmit() {
  emit('submit', form.value)
}
</script>
