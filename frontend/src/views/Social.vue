<template>
  <div class="social-page">
    <!-- 顶部导航栏 -->
    <div class="top-header">
      <div class="header-content">
        <h2 class="page-title">旅行动态</h2>
        <a-button type="primary" size="large" @click="showCreateModal = true" class="post-btn">
          <template #icon><EditOutlined /></template>
          发布动态
        </a-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧内容区 -->
      <div class="content-left">
        <a-spin :spinning="socialStore.isLoading" size="large">
          <div v-if="socialStore.feed.length === 0 && !socialStore.isLoading" class="empty-feed">
            <a-empty description="暂无动态，快来发布第一条吧！" />
          </div>

          <!-- 动态列表 -->
          <div v-else class="feed-list">
            <div
              v-for="item in socialStore.feed"
              :key="item.id"
              class="post-card"
            >
              <!-- 用户信息 -->
              <div class="post-header">
                <a-avatar :size="48" :src="item.user_avatar" class="user-avatar">
                  {{ item.username?.[0] || '?' }}
                </a-avatar>
                <div class="user-info">
                  <div class="username">{{ item.username || '未知用户' }}</div>
                  <div class="post-time">
                    {{ formatTime(item.created_at) }}
                  </div>
                </div>
              </div>

              <!-- 帖子内容 -->
              <div class="post-content">
                <div class="post-text">{{ item.content }}</div>

                <!-- 图片列表 -->
                <div v-if="item.media_urls && item.media_urls.length > 0" class="post-images">
                  <a-image-preview-group>
                    <div :class="`image-grid grid-${Math.min(item.media_urls.length, 9)}`">
                      <a-image
                        v-for="(url, index) in item.media_urls.slice(0, 9)"
                        :key="index"
                        :src="url"
                        class="post-image"
                        :preview="true"
                      />
                    </div>
                  </a-image-preview-group>
                </div>

                <!-- 标签 -->
                <div v-if="item.tags && item.tags.length > 0" class="post-tags">
                  <a-tag
                    v-for="tag in item.tags"
                    :key="tag"
                    color="blue"
                    class="post-tag"
                  >
                    #{{ tag }}
                  </a-tag>
                </div>
              </div>

              <!-- 互动区域 -->
              <div class="post-actions">
                <div class="action-item" @click="toggleLike(item.id, item.is_liked)">
                  <HeartFilled v-if="item.is_liked" class="action-icon liked" />
                  <HeartOutlined v-else class="action-icon" />
                  <span class="action-text">{{ item.likes_count || 0 }}</span>
                </div>
                <div class="action-item" @click="showComments(item)">
                  <CommentOutlined class="action-icon" />
                  <span class="action-text">{{ item.comments_count || 0 }}</span>
                </div>
                <div class="action-item">
                  <ShareAltOutlined class="action-icon" />
                  <span class="action-text">分享</span>
                </div>
              </div>
            </div>
          </div>
        </a-spin>
      </div>

      <!-- 右侧边栏 -->
      <div class="sidebar-right">
        <!-- 用户卡片 -->
        <div class="sidebar-card user-card">
          <a-avatar :size="64" :src="authStore.user?.avatar_url">
            {{ authStore.user?.username?.[0] || 'U' }}
          </a-avatar>
          <div class="user-name">{{ authStore.user?.username || '游客' }}</div>
        </div>

        <!-- 热门话题 -->
        <div class="sidebar-card">
          <div class="card-title">热门话题</div>
          <div class="hot-topics">
            <div v-for="i in 5" :key="i" class="topic-item">
              <span class="topic-rank">{{ i }}</span>
              <span class="topic-name">#旅行分享#</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 发布动态弹窗 -->
    <a-modal
      v-model:open="showCreateModal"
      title="发布动态"
      width="600px"
      :confirm-loading="creating"
      @ok="createPost"
      okText="发布"
      cancelText="取消"
    >
      <a-form :model="postForm" layout="vertical" class="post-form">
        <a-form-item>
          <a-textarea
            v-model:value="postForm.content"
            :rows="6"
            placeholder="分享你的旅行故事..."
            :maxlength="5000"
            show-count
          />
        </a-form-item>

        <a-form-item label="添加图片">
          <a-upload
            v-model:file-list="fileList"
            list-type="picture-card"
            :before-upload="beforeUpload"
            @change="handleUploadChange"
            :max-count="9"
          >
            <div v-if="fileList.length < 9">
              <PlusOutlined />
              <div style="margin-top: 8px">上传</div>
            </div>
          </a-upload>
        </a-form-item>

        <a-form-item label="添加标签">
          <a-select
            v-model:value="postForm.tags"
            mode="tags"
            placeholder="输入标签，按回车添加"
            style="width: 100%"
            :max-tag-count="5"
          >
            <a-select-option value="旅行">旅行</a-select-option>
            <a-select-option value="美食">美食</a-select-option>
            <a-select-option value="风景">风景</a-select-option>
            <a-select-option value="攻略">攻略</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 评论弹窗 -->
    <a-modal
      v-model:open="showCommentsModal"
      title="评论"
      width="700px"
      :footer="null"
      class="comments-modal"
    >
      <div class="comments-container">
        <!-- 评论加载中 -->
        <a-spin :spinning="loadingComments">
          <!-- 评论列表 -->
          <div class="comments-list">
            <div v-if="comments.length === 0 && !loadingComments" class="no-comments">
              <a-empty description="暂无评论，快来抢沙发！" :image="Empty.PRESENTED_IMAGE_SIMPLE" />
            </div>

            <div v-else>
              <div
                v-for="comment in comments"
                :key="comment.id"
                class="comment-item"
              >
                <a-avatar :size="40" :src="comment.user_avatar">
                  {{ comment.username?.[0] || '?' }}
                </a-avatar>
                <div class="comment-content">
                  <div class="comment-username">{{ comment.username || '未知用户' }}</div>
                  <div class="comment-text">{{ comment.content }}</div>
                  <div class="comment-time">{{ formatTime(comment.created_at) }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 发表评论 -->
          <div class="comment-input-area">
            <a-textarea
              v-model:value="commentContent"
              placeholder="写下你的评论..."
              :rows="3"
              :maxlength="500"
              show-count
            />
            <a-button
              type="primary"
              :loading="submittingComment"
              @click="submitComment"
              class="comment-submit-btn"
            >
              发表评论
            </a-button>
          </div>
        </a-spin>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message, Empty } from 'ant-design-vue'
import {
  EditOutlined,
  HeartOutlined,
  HeartFilled,
  CommentOutlined,
  ShareAltOutlined,
  PlusOutlined
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useSocialStore } from '@/stores/social'
import { socialService } from '@/services/social'

const socialStore = useSocialStore()
const authStore = useAuthStore()

// 发布动态相关
const showCreateModal = ref(false)
const creating = ref(false)
const postForm = ref({
  content: '',
  tags: [] as string[]
})
const fileList = ref<any[]>([])

// 评论相关
const showCommentsModal = ref(false)
const currentPost = ref<any>(null)
const comments = ref<any[]>([])
const loadingComments = ref(false)
const commentContent = ref('')
const submittingComment = ref(false)

onMounted(async () => {
  await loadFeed()
})

// 加载动态列表
async function loadFeed() {
  try {
    const feed = await socialService.getFeed()
    // console.log('动态列表:', feed)
    socialStore.setFeed(feed)
  } catch (error) {
    console.error('加载动态失败:', error)
    message.error('加载动态失败')
  } finally {
    // socialStore.isLoading.value = false
  }
}

// 点赞/取消点赞
async function toggleLike(postId: string, isLiked: boolean) {
  try {
    if (isLiked) {
      await socialService.unlikePost(postId)
    } else {
      await socialService.likePost(postId)
    }
    socialStore.toggleLike(postId)
    message.success(isLiked ? '已取消点赞' : '已点赞')
  } catch (error) {
    console.error('点赞操作失败:', error)
    message.error('操作失败，请重试')
  }
}

// 显示评论
async function showComments(post: any) {
  currentPost.value = post
  showCommentsModal.value = true
  await loadComments(post.id)
}

// 加载评论列表
async function loadComments(postId: string) {
  loadingComments.value = true
  try {
    const result = await socialService.getComments(postId)
    comments.value = result
    // console.log('评论列表:', result)
  } catch (error) {
    console.error('加载评论失败:', error)
    message.error('加载评论失败')
  } finally {
    loadingComments.value = false
  }
}

// 提交评论
async function submitComment() {
  if (!commentContent.value.trim()) {
    message.warning('请输入评论内容')
    return
  }

  if (!currentPost.value) {
    message.error('无法获取帖子信息')
    return
  }

  submittingComment.value = true
  try {
    const newComment = await socialService.addComment(
      currentPost.value.id,
      commentContent.value
    )

    console.log('新评论数据:', newComment)

    // 添加新评论到列表（后端已返回完整数据，直接添加到开头）
    comments.value.unshift({
      ...newComment,
      id: newComment.id || newComment.comment_id
    })

    // 更新帖子的评论数
    const feedList = socialStore.feed
    if (feedList && Array.isArray(feedList)) {
      feedList.forEach((post: any) => {
        if (post.id === currentPost.value?.id) {
          post.comments_count = (post.comments_count || 0) + 1
        }
      })
    }

    commentContent.value = ''
    message.success('评论发表成功')
  } catch (error) {
    console.error('发表评论失败:', error)
    message.error('发表评论失败')
  } finally {
    submittingComment.value = false
  }
}

// 上传前校验
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
  return false // 阻止自动上传
}

// 文件列表变化
function handleUploadChange({ fileList: newFileList }: any) {
  fileList.value = newFileList
}

// 发布动态
async function createPost() {
  if (!postForm.value.content.trim()) {
    message.error('请输入动态内容')
    return
  }

  creating.value = true
  try {
    // 上传图片
    const uploadedUrls: string[] = []
    for (const file of fileList.value) {
      if (file.originFileObj) {
        const result = await socialService.uploadMedia(file.originFileObj)
        uploadedUrls.push(result.url)
      }
    }

    // 创建帖子
    await socialService.createPost({
      content: postForm.value.content,
      tags: postForm.value.tags,
      media_urls: uploadedUrls
    })

    message.success('发布成功')
    showCreateModal.value = false
    postForm.value = { content: '', tags: [] }
    fileList.value = []

    // 重新加载动态
    await loadFeed()
  } catch (error) {
    console.error('发布失败:', error)
    message.error('发布失败，请重试')
  } finally {
    creating.value = false
  }
}

// 格式化时间
function formatTime(time: string) {
  if (!time) return ''

  const now = new Date()
  const postTime = new Date(time)
  const diff = now.getTime() - postTime.getTime()

  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (seconds < 60) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return postTime.toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.social-page {
  min-height: 100vh;
  background: #f5f5f5;
}

/* 顶部导航栏 */
.top-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
}

.post-btn {
  border-radius: 20px;
  height: 40px;
  padding: 0 24px;
}

/* 主内容区 */
.main-content {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
  display: flex;
  gap: 24px;
}

.content-left {
  flex: 1;
  min-width: 0;
}

.sidebar-right {
  width: 300px;
  flex-shrink: 0;
}

/* 动态卡片 */
.post-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.3s;
}

.post-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 用户信息 */
.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.user-avatar {
  flex-shrink: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 600;
}

.user-info {
  margin-left: 12px;
  flex: 1;
}

.username {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  line-height: 1.4;
}

.post-time {
  font-size: 13px;
  color: #8c8c8c;
  margin-top: 2px;
}

/* 帖子内容 */
.post-content {
  margin-bottom: 16px;
}

.post-text {
  font-size: 15px;
  line-height: 1.6;
  color: #262626;
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 12px;
}

/* 图片网格 */
.post-images {
  margin: 12px 0;
}

.image-grid {
  display: grid;
  gap: 8px;
}

.grid-1 {
  grid-template-columns: 1fr;
  max-width: 400px;
}

.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

.grid-4 {
  grid-template-columns: repeat(2, 1fr);
}

.grid-5,
.grid-6,
.grid-7,
.grid-8,
.grid-9 {
  grid-template-columns: repeat(3, 1fr);
}

.post-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
}

/* 标签 */
.post-tags {
  margin: 12px 0;
}

.post-tag {
  margin-right: 8px;
  margin-bottom: 8px;
  border-radius: 12px;
  padding: 4px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.post-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

/* 互动区域 */
.post-actions {
  display: flex;
  gap: 48px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  transition: all 0.3s;
}

.action-item:hover {
  color: #1890ff;
}

.action-item:hover .action-icon {
  transform: scale(1.1);
}

.action-icon {
  font-size: 18px;
  transition: all 0.3s;
}

.action-icon.liked {
  color: #ff4d4f;
}

.action-text {
  font-size: 14px;
  color: #8c8c8c;
}

.action-item:hover .action-text {
  color: #1890ff;
}

/* 右侧边栏 */
.sidebar-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.user-card {
  text-align: center;
}

.user-name {
  margin-top: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #262626;
}

.hot-topics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.topic-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.topic-item:hover {
  background: #f5f5f5;
}

.topic-rank {
  width: 24px;
  height: 24px;
  background: #f0f0f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #8c8c8c;
  flex-shrink: 0;
}

.topic-name {
  font-size: 14px;
  color: #262626;
}

/* 空状态 */
.empty-feed {
  background: #fff;
  border-radius: 12px;
  padding: 60px 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 评论弹窗 */
.comments-container {
  max-height: 600px;
  display: flex;
  flex-direction: column;
}

.comments-list {
  flex: 1;
  overflow-y: auto;
  max-height: 400px;
  margin-bottom: 20px;
}

.no-comments {
  padding: 40px 20px;
  text-align: center;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-content {
  flex: 1;
}

.comment-username {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 4px;
}

.comment-text {
  font-size: 14px;
  color: #262626;
  line-height: 1.6;
  margin-bottom: 8px;
}

.comment-time {
  font-size: 12px;
  color: #8c8c8c;
}

.comment-input-area {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.comment-submit-btn {
  margin-top: 12px;
  float: right;
}

/* 发布表单 */
.post-form :deep(.ant-form-item) {
  margin-bottom: 16px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .sidebar-right {
    display: none;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 0 12px;
  }

  .post-card {
    padding: 16px;
    border-radius: 0;
  }

  .post-actions {
    gap: 24px;
  }
}
</style>
