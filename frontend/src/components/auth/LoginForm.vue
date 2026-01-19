<template>
  <a-form :model="form" @finish="handleSubmit">
    <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
      <a-input v-model:value="form.username" placeholder="用户名" size="large">
        <template #prefix><UserOutlined /></template>
      </a-input>
    </a-form-item>

    <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
      <a-input-password v-model:value="form.password" placeholder="密码" size="large">
        <template #prefix><LockOutlined /></template>
      </a-input-password>
    </a-form-item>

    <a-form-item>
      <a-button type="primary" html-type="submit" :loading="loading" block size="large">
        登录
      </a-button>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'

const emit = defineEmits<{
  submit: [data: { username: string; password: string }]
}>()

defineProps<{
  loading?: boolean
}>()

const form = ref({
  username: '',
  password: ''
})

function handleSubmit() {
  emit('submit', form.value)
}
</script>
