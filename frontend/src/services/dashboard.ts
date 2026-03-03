import axios from '@/utils/axios'

// ========== 请求模型 ==========

interface UserStatsRequest {
  /** 用户统计请求 */
  user_id?: string
}

interface ContentStatsRequest {
  /** 内容统计请求 */
  user_id?: string
}

interface BusinessStatsRequest {
  /** 业务统计请求 */
  user_id?: string
}

interface PopularDestinationsRequest {
  /** 热门目的地请求 */
  user_id?: string
}

// ========== 响应模型 ==========

interface UserStatsResponse {
  /** 用户统计响应 */
  totalUsers: number
  newUsers: number
  activeUsers: number
  growthRate: number
}

interface ContentStatsResponse {
  /** 内容统计响应 */
  totalPlans: number
  totalPosts: number
  totalComments: number
  plansGrowthRate: number
  postsGrowthRate: number
}

interface BusinessStatsResponse {
  /** 业务统计响应 */
  totalRevenue: number
  newOrders: number
  conversionRate: number
  revenueGrowthRate: number
}

interface PopularDestination {
  /** 热门目的地 */
  name: string
  searchCount: number
  bookCount: number
}

interface PopularDestinationsResponse {
  /** 热门目的地响应 */
  destinations: PopularDestination[]
}

// ========== 接口封装 ==========

/**
 * 获取用户统计
 * @param request 用户统计请求
 * @returns 用户统计响应
 */
export function getUserStats(request: UserStatsRequest = {}): Promise<UserStatsResponse> {
  return axios.get('/dashboard/user-stats', { params: request })
}

/**
 * 获取内容统计
 * @param request 内容统计请求
 * @returns 内容统计响应
 */
export function getContentStats(request: ContentStatsRequest = {}): Promise<ContentStatsResponse> {
  return axios.get('/dashboard/content-stats', { params: request })
}

/**
 * 获取业务统计
 * @param request 业务统计请求
 * @returns 业务统计响应
 */
export function getBusinessStats(request: BusinessStatsRequest = {}): Promise<BusinessStatsResponse> {
  return axios.get('/dashboard/business-stats', { params: request })
}

/**
 * 获取热门目的地
 * @param request 热门目的地请求
 * @returns 热门目的地响应
 */
export function getPopularDestinations(request: PopularDestinationsRequest = {}): Promise<PopularDestinationsResponse> {
  return axios.get('/dashboard/popular-destinations', { params: request })
}
