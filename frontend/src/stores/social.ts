import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Post {
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
  moderation_status: 'pending' | 'approved' | 'rejected'
  created_at: string
}

interface Comment {
  id: string
  user_id: number
  username: string
  user_avatar?: string
  content: string
  created_at: string
}

export const useSocialStore = defineStore('social', () => {
  const feed = ref<Post[]>([])
  const userPosts = ref<Post[]>([])
  const currentPost = ref<Post | null>(null)
  const comments = ref<Comment[]>([])
  const isLoading = ref(false)

  function setFeed(posts: Post[]) {
    feed.value = posts
  }

  function addToFeed(post: Post) {
    feed.value.unshift(post)
  }

  function setUserPosts(posts: Post[]) {
    userPosts.value = posts
  }

  function setCurrentPost(post: Post | null) {
    currentPost.value = post
  }

  function setComments(newComments: Comment[]) {
    comments.value = newComments
  }

  function addComment(comment: Comment) {
    comments.value.push(comment)
    if (currentPost.value) {
      currentPost.value.comments_count++
    }
  }

  function toggleLike(postId: string) {
    const updatePost = (post: Post) => {
      if (post.id === postId) {
        post.is_liked = !post.is_liked
        post.likes_count += post.is_liked ? 1 : -1
      }
    }
    feed.value.forEach(updatePost)
    userPosts.value.forEach(updatePost)
    if (currentPost.value?.id === postId) {
      updatePost(currentPost.value)
    }
  }

  function removePost(postId: string) {
    feed.value = feed.value.filter(p => p.id !== postId)
    userPosts.value = userPosts.value.filter(p => p.id !== postId)
    if (currentPost.value?.id === postId) {
      currentPost.value = null
    }
  }

  return {
    feed,
    userPosts,
    currentPost,
    comments,
    isLoading,
    setFeed,
    addToFeed,
    setUserPosts,
    setCurrentPost,
    setComments,
    addComment,
    toggleLike,
    removePost
  }
})
