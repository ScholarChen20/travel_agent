<template>
  <div class="social-container">
    <a-page-header title="旅行动态" style="background: white; margin-bottom: 16px">
      <template #extra>
        <a-button type="primary" @click="showCreateModal = true">
          <PlusOutlined /> 发布动态
        </a-button>
      </template>
    </a-page-header>

    <div style="padding: 0 24px; max-width: 800px; margin: 0 auto">
      <a-spin :spinning="socialStore.isLoading.value">
        <a-list
          :data-source="socialStore.feed.value"
          item-layout="vertical"
        >
          <template #renderItem="{ item }">
            <a-list-item>
              <template #actions>
                <span @click="toggleLike(item.id)" style="cursor: pointer">
                  <HeartFilled v-if="item.is_liked" style="color: #ff4d4f" />
                  <HeartOutlined v-else />
                  {{ item.likes_count }}
                </span>
                <span @click="viewPost(item.id)" style="cursor: pointer">
                  <CommentOutlined /> {{ item.comments_count }}
                </span>
              </template>
              <a-list-item-meta>
                <template #avatar>
                  <a-avatar :src="item.user_avatar">
                    {{ item.username[0] }}
                  </a-avatar>
                </template>
                <template #title>
                  {{ item.username }}
                </template>
                <template #description>
                  {{ item.created_at }}
                </template>
              </a-list-item-meta>
              <div>{{ item.content }}</div>
              <div v-if="item.media_urls.length > 0" style="margin-top: 12px">
                <a-image-preview-group>
                  <a-image
                    v-for="(url, index) in item.media_urls"
                    :key="index"
                    :src="url"
                    :width="200"
                    style="margin-right: 8px"
                  />
                </a-image-preview-group>
              </div>
              <div v-if="item.tags.length > 0" style="margin-top: 12px">
                <a-tag v-for="tag in item.tags" :key="tag" color="blue">
                  #{{ tag }}
                </a-tag>
              </div>
            </a-list-item>
          </template>
        </a-list>
      </a-spin>
    </div>

    <a-modal
      v-model:open="showCreateModal"
      title="发布动态"
      @ok="createPost"
      :confirm-loading="creating"
    >
      <a-form :model="postForm" layout="vertical">
        <a-form-item label="内容">
          <a-textarea
            v-model:value="postForm.content"
            :rows="4"
            placeholder="分享你的旅行故事..."
          />
        </a-form-item>
        <a-form-item label="标签">
          <a-select
            v-model:value="postForm.tags"
            mode="tags"
            placeholder="添加标签"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="图片">
          <a-upload
            list-type="picture-card"
            :file-list="fileList"
            @change="handleUploadChange"
            :before-upload="beforeUpload"
          >
            <div v-if="fileList.length < 9">
              <PlusOutlined />
              <div style="margin-top: 8px">上传</div>
            </div>
          </a-upload>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { PlusOutlined, HeartOutlined, HeartFilled, CommentOutlined } from '@ant-design/icons-vue'
import { useSocialStore } from '@/stores/social'
import { socialService } from '@/services/social'

const router = useRouter()
const socialStore = useSocialStore()

const showCreateModal = ref(false)
const creating = ref(false)
const postForm = ref({
  content: '',
  tags: [] as string[],
  media_urls: [] as string[]
})
const fileList = ref<any[]>([])

onMounted(async () => {
  await loadFeed()
})

async function loadFeed() {
  socialStore.isLoading.value = true
  try {
    const feed = await socialService.getFeed()
    socialStore.setFeed(feed)
  } catch (error) {
    message.error('加载动态失败')
  } finally {
    socialStore.isLoading.value = false
  }
}

async function toggleLike(postId: string) {
  const post = socialStore.feed.value.find((p: any) => p.id === postId)
  if (!post) return

  try {
    if (post.is_liked) {
      await socialService.unlikePost(postId)
    } else {
      await socialService.likePost(postId)
    }
    socialStore.toggleLike(postId)
  } catch (error) {
    message.error('操作失败')
  }
}

function viewPost(postId: string) {
  // Navigate to post detail or show comments modal
  message.info('查看帖子详情')
}

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
  return false // Prevent auto upload
}

async function handleUploadChange({ fileList: newFileList }: any) {
  fileList.value = newFileList
}

async function createPost() {
  if (!postForm.value.content.trim()) {
    message.error('请输入内容')
    return
  }

  creating.value = true
  try {
    // Upload images first
    const uploadedUrls: string[] = []
    for (const file of fileList.value) {
      if (file.originFileObj) {
        const result = await socialService.uploadMedia(file.originFileObj)
        uploadedUrls.push(result.url)
      }
    }

    await socialService.createPost({
      content: postForm.value.content,
      tags: postForm.value.tags,
      media_urls: uploadedUrls
    })

    message.success('发布成功')
    showCreateModal.value = false
    postForm.value = { content: '', tags: [], media_urls: [] }
    fileList.value = []

    // Reload feed to show the new post
    await loadFeed()
  } catch (error) {
    message.error('发布失败')
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.social-container {
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
