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
    const response = await axios.get('/api/plans', {
      params: { limit, offset }
    })
    return response.data
  },

  async getPlan(planId: string): Promise<TravelPlan> {
    const response = await axios.get(`/api/plans/${planId}`)
    return response.data
  },

  async updatePlan(planId: string, data: UpdatePlanRequest): Promise<TravelPlan> {
    const response = await axios.put(`/api/plans/${planId}`, data)
    return response.data
  },

  async deletePlan(planId: string): Promise<void> {
    await axios.delete(`/api/plans/${planId}`)
  },

  async toggleFavorite(planId: string): Promise<TravelPlan> {
    const response = await axios.post(`/api/plans/${planId}/favorite`)
    return response.data
  },

  async exportPlan(planId: string, format: 'json' | 'pdf' = 'json'): Promise<Blob> {
    const response = await axios.get(`/api/plans/${planId}/export`, {
      params: { format },
      responseType: 'blob'
    })
    return response.data
  }
}
