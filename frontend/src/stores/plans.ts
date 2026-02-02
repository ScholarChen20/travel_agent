import { defineStore } from 'pinia'
import { ref } from 'vue'

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

export const usePlansStore = defineStore('plans', () => {
  const plans = ref<TravelPlan[]>([])
  const currentPlan = ref<TravelPlan | null>(null)
  const isLoading = ref(false)

  function setPlans(newPlans: TravelPlan[]) {
    plans.value = newPlans
  }

  function setCurrentPlan(plan: TravelPlan | null) {
    currentPlan.value = plan
  }

  function addPlan(plan: TravelPlan) {
    plans.value.unshift(plan)
  }

  function updatePlan(planId: string, updates: Partial<TravelPlan>) {
    const index = plans.value.findIndex(p => p.id === planId)
    if (index !== -1) {
      plans.value[index] = { ...plans.value[index], ...updates }
    }
    if (currentPlan.value?.id === planId) {
      currentPlan.value = { ...currentPlan.value, ...updates }
    }
  }

  function removePlan(planId: string) {
    plans.value = plans.value.filter(p => p.id !== planId)
    if (currentPlan.value?.id === planId) {
      currentPlan.value = null
    }
  }

  function toggleFavorite(planId: string) {
    const plan = plans.value.find(p => p.id === planId)
    if (plan) {
      plan.is_favorite = !plan.is_favorite
    }
    if (currentPlan.value?.id === planId) {
      currentPlan.value.is_favorite = !currentPlan.value.is_favorite
    }
  }

  return {
    plans,
    currentPlan,
    isLoading,
    setPlans,
    setCurrentPlan,
    addPlan,
    updatePlan,
    removePlan,
    toggleFavorite
  }
})
