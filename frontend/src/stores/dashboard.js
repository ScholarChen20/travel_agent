import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useDashboardStore = defineStore('dashboard', () => {
  // 状态
  const userStats = ref({})
  const contentStats = ref({})
  const businessStats = ref({})
  const businessTrend = ref(null)

  // 获取首页综合指标
  const fetchOverview = async () => {
    try {
      const response = await axios.get('/api/dashboard/overview')
      if (response.data.code === 200) {
        const data = response.data.data
        userStats.value = data.user_stats
        contentStats.value = data.content_stats
        businessStats.value = data.business_stats
      } else {
        throw new Error(response.data.msg)
      }
    } catch (error) {
      console.error('获取首页综合指标失败:', error)
      throw error
    }
  }

  // 获取用户统计数据
  const fetchUserStats = async () => {
    try {
      const response = await axios.get('/api/dashboard/user-stats')
      if (response.data.code === 200) {
        userStats.value = response.data.data
      } else {
        throw new Error(response.data.msg)
      }
    } catch (error) {
      console.error('获取用户统计数据失败:', error)
      throw error
    }
  }

  // 获取内容统计数据
  const fetchContentStats = async () => {
    try {
      const response = await axios.get('/api/dashboard/content-stats')
      if (response.data.code === 200) {
        contentStats.value = response.data.data
      } else {
        throw new Error(response.data.msg)
      }
    } catch (error) {
      console.error('获取内容统计数据失败:', error)
      throw error
    }
  }

  // 获取业务指标数据
  const fetchBusinessStats = async () => {
    try {
      const response = await axios.get('/api/dashboard/business-stats')
      if (response.data.code === 200) {
        businessStats.value = response.data.data
      } else {
        throw new Error(response.data.msg)
      }
    } catch (error) {
      console.error('获取业务指标数据失败:', error)
      throw error
    }
  }

  // 获取业务趋势数据
  const fetchBusinessTrend = async (startDate, endDate) => {
    try {
      const params = {}
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate

      const response = await axios.get('/api/dashboard/business-trend', { params })
      if (response.data.code === 200) {
        businessTrend.value = response.data.data
      } else {
        throw new Error(response.data.msg)
      }
    } catch (error) {
      console.error('获取业务趋势数据失败:', error)
      throw error
    }
  }

  return {
    userStats,
    contentStats,
    businessStats,
    businessTrend,
    fetchOverview,
    fetchUserStats,
    fetchContentStats,
    fetchBusinessStats,
    fetchBusinessTrend
  }
})
