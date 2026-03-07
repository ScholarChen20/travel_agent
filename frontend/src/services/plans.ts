import axios from '@/utils/axios'

interface TravelPlan {
  id: string
  title: string
  destination: string
  start_date: string
  end_date: string
  budget?: number
  plan_data: any
  is_favorite: boolean
  created_at: string
  updated_at: string
}

interface UpdatePlanRequest {
  title?: string
  is_favorite?: boolean
}

export const plansService = {
  async getPlans(limit = 50, offset = 0): Promise<TravelPlan[]> {
    const response = await axios.get('/plans', {
      params: { limit, skip: offset }
    })
    const data = response.data.data
    const plans = data?.plans || data || []
    return plans.map((plan: any) => ({
      id: plan.plan_id,
      title: plan.city,
      destination: plan.city,
      start_date: plan.start_date,
      end_date: plan.end_date || plan.start_date,
      budget: plan.budget,
      plan_data: plan.days,
      is_favorite: plan.is_favorite,
      created_at: plan.created_at,
      updated_at: plan.updated_at
    }))
  },

  async getPlan(planId: string): Promise<TravelPlan> {
    const response = await axios.get(`/plans/${planId}`)
    const plan = response.data.data
    return {
      id: plan.plan_id,
      title: plan.city,
      destination: plan.city,
      start_date: plan.start_date,
      end_date: plan.end_date || plan.start_date,
      budget: plan.budget,
      plan_data: plan.days,
      is_favorite: plan.is_favorite,
      created_at: plan.created_at,
      updated_at: plan.updated_at
    }
  },

  async updatePlan(planId: string, data: UpdatePlanRequest): Promise<TravelPlan> {
    const response = await axios.put(`/plans/${planId}`, data)
    const plan = response.data.data
    return {
      id: plan.plan_id,
      title: plan.city,
      destination: plan.city,
      start_date: plan.start_date,
      end_date: plan.end_date || plan.start_date,
      budget: plan.budget,
      plan_data: plan.days,
      is_favorite: plan.is_favorite,
      created_at: plan.created_at,
      updated_at: plan.updated_at
    }
  },

  async deletePlan(planId: string): Promise<void> {
    await axios.delete(`/plans/${planId}`)
  },

  async toggleFavorite(planId: string): Promise<void> {
    await axios.post(`/plans/${planId}/favorite`)
  },

  async exportPlan(planId: string, format: 'json' | 'pdf' = 'json'): Promise<Blob> {
    const response = await axios.get(`/plans/${planId}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }
}
