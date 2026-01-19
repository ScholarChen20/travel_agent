<template>
  <div class="plan-detail-container">
    <a-page-header
      :title="plansStore.currentPlan.value?.title"
      @back="$router.back()"
      style="background: white; margin-bottom: 16px"
    >
      <template #extra>
        <a-button @click="toggleFavorite">
          <HeartFilled v-if="plansStore.currentPlan.value?.is_favorite" style="color: #ff4d4f" />
          <HeartOutlined v-else />
        </a-button>
        <a-button @click="exportPlan">
          <ExportOutlined /> 导出
        </a-button>
      </template>
    </a-page-header>

    <div style="padding: 0 24px">
      <a-spin :spinning="loading">
        <a-card v-if="plansStore.currentPlan.value">
          <a-descriptions bordered :column="2">
            <a-descriptions-item label="目的地">
              {{ plansStore.currentPlan.value.destination }}
            </a-descriptions-item>
            <a-descriptions-item label="预算">
              ¥{{ plansStore.currentPlan.value.budget || '未设置' }}
            </a-descriptions-item>
            <a-descriptions-item label="开始日期">
              {{ plansStore.currentPlan.value.start_date }}
            </a-descriptions-item>
            <a-descriptions-item label="结束日期">
              {{ plansStore.currentPlan.value.end_date }}
            </a-descriptions-item>
            <a-descriptions-item label="创建时间" :span="2">
              {{ plansStore.currentPlan.value.created_at }}
            </a-descriptions-item>
          </a-descriptions>

          <a-divider>行程详情</a-divider>

          <div v-if="plansStore.currentPlan.value.plan_data">
            <a-timeline>
              <a-timeline-item
                v-for="(day, index) in plansStore.currentPlan.value.plan_data.itinerary"
                :key="index"
              >
                <template #dot>
                  <CalendarOutlined style="font-size: 16px" />
                </template>
                <h3>第 {{ index + 1 }} 天</h3>
                <a-list
                  :data-source="day.activities"
                  size="small"
                >
                  <template #renderItem="{ item }">
                    <a-list-item>
                      <a-list-item-meta>
                        <template #title>{{ item.name }}</template>
                        <template #description>
                          <div>{{ item.time }}</div>
                          <div>{{ item.description }}</div>
                        </template>
                      </a-list-item-meta>
                    </a-list-item>
                  </template>
                </a-list>
              </a-timeline-item>
            </a-timeline>
          </div>
        </a-card>
      </a-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { HeartOutlined, HeartFilled, ExportOutlined, CalendarOutlined } from '@ant-design/icons-vue'
import { usePlansStore } from '@/stores/plans'
import { plansService } from '@/services/plans'

const route = useRoute()
const plansStore = usePlansStore()
const loading = ref(false)

onMounted(async () => {
  await loadPlan()
})

async function loadPlan() {
  loading.value = true
  try {
    const planId = route.params.id as string
    const plan = await plansService.getPlan(planId)
    plansStore.setCurrentPlan(plan)
  } catch (error) {
    message.error('加载计划失败')
  } finally {
    loading.value = false
  }
}

async function toggleFavorite() {
  if (!plansStore.currentPlan.value) return
  try {
    await plansService.toggleFavorite(plansStore.currentPlan.value.id)
    plansStore.toggleFavorite(plansStore.currentPlan.value.id)
    message.success('操作成功')
  } catch (error) {
    message.error('操作失败')
  }
}

async function exportPlan() {
  if (!plansStore.currentPlan.value) return
  try {
    const blob = await plansService.exportPlan(plansStore.currentPlan.value.id, 'json')
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `plan_${plansStore.currentPlan.value.id}.json`
    a.click()
    window.URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
  }
}
</script>

<style scoped>
.plan-detail-container {
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
