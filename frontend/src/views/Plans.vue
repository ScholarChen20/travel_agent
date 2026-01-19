<template>
  <div class="plans-container">
    <a-page-header title="我的旅行计划" style="background: white; margin-bottom: 16px">
      <template #extra>
        <a-button type="primary" @click="$router.push('/')">
          <PlusOutlined /> 创建新计划
        </a-button>
      </template>
    </a-page-header>

    <div style="padding: 0 24px">
      <a-spin :spinning="plansStore.isLoading">
        <a-row :gutter="[16, 16]">
          <a-col v-for="plan in plansStore.plans" :key="plan.id" :xs="24" :sm="12" :lg="8">
            <a-card hoverable @click="viewPlan(plan.id)">
              <template #cover>
                <div style="height: 200px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 24px">
                  {{ plan.destination }}
                </div>
              </template>
              <template #actions>
                <HeartOutlined
                  v-if="!plan.is_favorite"
                  @click.stop="toggleFavorite(plan.id)"
                />
                <HeartFilled
                  v-else
                  style="color: #ff4d4f"
                  @click.stop="toggleFavorite(plan.id)"
                />
                <ExportOutlined @click.stop="exportPlan(plan.id)" />
                <DeleteOutlined @click.stop="deletePlan(plan.id)" />
              </template>
              <a-card-meta :title="plan.title">
                <template #description>
                  <div>{{ plan.start_date }} 至 {{ plan.end_date }}</div>
                  <div v-if="plan.budget">预算: ¥{{ plan.budget }}</div>
                </template>
              </a-card-meta>
            </a-card>
          </a-col>
        </a-row>

        <a-empty v-if="plansStore.plans.length === 0" description="还没有旅行���划" style="margin-top: 60px">
          <a-button type="primary" @click="$router.push('/')">创建第一个计划</a-button>
        </a-empty>
      </a-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, HeartOutlined, HeartFilled, ExportOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { usePlansStore } from '@/stores/plans'
import { plansService } from '@/services/plans'

const router = useRouter()
const plansStore = usePlansStore()

onMounted(async () => {
  await loadPlans()
})

async function loadPlans() {
  plansStore.isLoading = true
  try {
    const plans = await plansService.getPlans()
    plansStore.setPlans(plans)
  } catch (error) {
    message.error('加载计划失败')
  } finally {
    plansStore.isLoading = false
  }
}

function viewPlan(planId: string) {
  router.push(`/plans/${planId}`)
}

async function toggleFavorite(planId: string) {
  try {
    await plansService.toggleFavorite(planId)
    plansStore.toggleFavorite(planId)
    message.success('操作成功')
  } catch (error) {
    message.error('操作失败')
  }
}

async function exportPlan(planId: string) {
  try {
    const blob = await plansService.exportPlan(planId, 'json')
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `plan_${planId}.json`
    a.click()
    window.URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
  }
}

function deletePlan(planId: string) {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个旅行计划吗？',
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        await plansService.deletePlan(planId)
        plansStore.removePlan(planId)
        message.success('删除成功')
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}
</script>

<style scoped>
.plans-container {
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
