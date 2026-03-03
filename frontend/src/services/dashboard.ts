import axios from '@/utils/axios'

// ========== 请求模型 ==========

interface DateRangeRequest {
  /** 日期范围请求 */
  start_date?: string
  end_date?: string
}

// ========== 响应模型 ==========

interface UserStatsResponse {
  /** 用户统计响应 */
  total_users: number
  active_users_today: number
  active_users_week: number
  new_users_today: number
  new_users_week: number
  new_users_month: number
  user_growth_rate: number
}

interface ContentStatsResponse {
  /** 内容统计响应 */
  total_plans: number
  total_pois: number
  total_posts: number
  total_comments: number
  plans_created_today: number
  posts_created_today: number
}

interface BusinessStatsResponse {
  /** 业务统计响应 */
  daily_plan_creation: number
  weekly_plan_creation: number
  monthly_plan_creation: number
  user_retention_rate: number
  average_plan_length: number
}

interface DashboardOverviewResponse {
  /** 首页综合指标响应 */
  user_stats: UserStatsResponse
  content_stats: ContentStatsResponse
  business_stats: BusinessStatsResponse
  updated_at: string
}

interface BusinessTrendResponse {
  /** 业务趋势响应 */
  date_range: string[]
  plan_creation_trend: number[]
  user_registration_trend: number[]
  user_activity_trend: number[]
}

// ========== 接口封装 ==========

/**
 * 获取首页综合指标
 * @returns 首页综合指标响应
 */
export async function getDashboardOverview(): Promise<DashboardOverviewResponse> {
  const response = await axios.get('/dashboard/overview')
  return response.data.data
}

/**
 * 获取用户统计
 * @returns 用户统计响应
 */
export async function getUserStats(): Promise<UserStatsResponse> {
  const response = await axios.get('/dashboard/user-stats')
  return response.data.data
}

/**
 * 获取内容统计
 * @returns 内容统计响应
 */
export async function getContentStats(): Promise<ContentStatsResponse> {
  const response = await axios.get('/dashboard/content-stats')
  return response.data.data
}

/**
 * 获取业务统计
 * @returns 业务统计响应
 */
export async function getBusinessStats(): Promise<BusinessStatsResponse> {
  const response = await axios.get('/dashboard/business-stats')
  return response.data.data
}

/**
 * 获取业务趋势
 * @param request 日期范围请求
 * @returns 业务趋势响应
 */
export async function getBusinessTrend(request?: DateRangeRequest): Promise<BusinessTrendResponse> {
  const response = await axios.get('/dashboard/business-trend', { params: request })
  return response.data.data
}
