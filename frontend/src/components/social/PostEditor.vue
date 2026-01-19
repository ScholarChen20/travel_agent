<template>
  <a-form :model="form" layout="vertical">
    <a-form-item label="内容">
      <a-textarea
        v-model:value="form.content"
        :rows="4"
        placeholder="分享你的旅行故事..."
      />
    </a-form-item>
    <a-form-item label="标签">
      <a-select
        v-model:value="form.tags"
        mode="tags"
        placeholder="添加标签"
        style="width: 100%"
      />
    </a-form-item>
    <a-form-item label="图片">
      <a-upload
        list-type="picture-card"
        :file-list="fileList"
        @change="handleChange"
        :before-upload="beforeUpload"
      >
        <div v-if="fileList.length < 9">
          <PlusOutlined />
          <div style="margin-top: 8px">上传</div>
        </div>
      </a-upload>
    </a-form-item>
    <a-form-item>
      <a-button type="primary" @click="handleSubmit" :loading="loading">
        发布
      </a-button>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'

const emit = defineEmits<{
  submit: [data: { content: string; tags: string[]; files: File[] }]
}>()

defineProps<{
  loading?: boolean
}>()

const form = ref({
  content: '',
  tags: [] as string[]
})

const fileList = ref<any[]>([])

function beforeUpload(file: File) {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件')
    return false
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('图片大小不能超过5MB')
    return false
  }
  return false
}

function handleChange({ fileList: newFileList }: any) {
  fileList.value = newFileList
}

function handleSubmit() {
  if (!form.value.content.trim()) {
    message.error('请输入内容')
    return
  }
  const files = fileList.value.map(f => f.originFileObj).filter(Boolean)
  emit('submit', { ...form.value, files })
}
</script>
