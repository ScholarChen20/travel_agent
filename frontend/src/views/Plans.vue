<template>
  <div class="plans-container">
    <a-page-header title="我的旅行计划" class="page-header" @back="router.push('/')">
      <template #extra>
        <a-button type="primary" size="large" @click="$router.push('/create-plan')">
          <PlusOutlined /> 创建新计划
        </a-button>
      </template>
    </a-page-header>

    <div class="content-wrapper">
      <a-spin :spinning="plansStore.isLoading">
        <a-row :gutter="[24, 24]">
          <a-col v-for="plan in plansStore.plans" :key="plan.id" :xs="24" :sm="24" :md="12" :lg="12" :xl="8">
            <a-card
              hoverable
              class="plan-card"
              @click="viewPlan(plan.id)"
              :body-style="{ padding: 0 }"
            >
              <!-- 图片封面 -->
              <div class="plan-cover">
                <img
                  v-if="getCoverImage(plan)"
                  :src="getCoverImage(plan)"
                  :alt="plan.destination"
                  class="cover-image"
                />
                <div v-else class="cover-placeholder">
                  <EnvironmentOutlined class="placeholder-icon" />
                </div>
                <div class="cover-overlay">
                  <h2 class="destination-title">{{ plan.destination }}</h2>
                  <a-tag v-if="plan.is_favorite" color="red" class="favorite-tag">
                    <HeartFilled /> 已收藏
                  </a-tag>
                </div>
              </div>

              <!-- 内容区域 -->
              <div class="plan-content">
                <!-- 日期信息 -->
                <div class="info-section">
                  <CalendarOutlined class="section-icon" />
                  <div class="section-content">
                    <div class="section-label">旅行日期</div>
                    <div class="section-value">{{ formatDateRange(plan.start_date, plan.end_date) }}</div>
                  </div>
                </div>

                <!-- 预算信息 -->
                <div class="info-section" v-if="getBudgetTotal(plan)">
                  <WalletOutlined class="section-icon" style="color: #52c41a" />
                  <div class="section-content">
                    <div class="section-label">总预算</div>
                    <div class="section-value budget-value">¥{{ getBudgetTotal(plan).toLocaleString() }}</div>
                  </div>
                </div>

                <!-- 景点信息 -->
                <div class="info-section" v-if="getAttractionCount(plan) > 0">
                  <EnvironmentOutlined class="section-icon" style="color: #1890ff" />
                  <div class="section-content">
                    <div class="section-label">游览景点</div>
                    <div class="section-value">{{ getAttractionCount(plan) }} 个景点</div>
                  </div>
                </div>

                <!-- 美食推荐 -->
                <div class="info-section" v-if="getMealCount(plan) > 0">
                  <CoffeeOutlined class="section-icon" style="color: #faad14" />
                  <div class="section-content">
                    <div class="section-label">美食推荐</div>
                    <div class="section-value">{{ getMealCount(plan) }} 家餐厅</div>
                  </div>
                </div>

                <!-- 景点预览标签 -->
                <div class="attractions-preview" v-if="getTopAttractions(plan).length > 0">
                  <a-tag
                    v-for="(attraction, index) in getTopAttractions(plan)"
                    :key="index"
                    color="blue"
                    class="attraction-tag"
                  >
                    {{ attraction }}
                  </a-tag>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="plan-actions">
                <a-button
                  type="text"
                  size="small"
                  @click.stop="toggleFavorite(plan.id)"
                  class="action-btn"
                >
                  <HeartFilled v-if="plan.is_favorite" style="color: #ff4d4f" />
                  <HeartOutlined v-else />
                  {{ plan.is_favorite ? '取消收藏' : '收藏' }}
                </a-button>
                <a-button
                  type="text"
                  size="small"
                  @click.stop="exportPlan(plan.id)"
                  class="action-btn"
                >
                  <ExportOutlined /> 导出
                </a-button>
                <a-button
                  type="text"
                  size="small"
                  danger
                  @click.stop="deletePlan(plan.id)"
                  class="action-btn"
                >
                  <DeleteOutlined /> 删除
                </a-button>
              </div>
            </a-card>
          </a-col>
        </a-row>

        <a-empty
          v-if="plansStore.plans.length === 0"
          description="还没有旅行计划，开始创建你的第一个旅行计划吧！"
          class="empty-state"
        >
          <a-button type="primary" size="large" @click="$router.push('/create-plan')">
            <PlusOutlined /> 创建第一个计划
          </a-button>
        </a-empty>
      </a-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  PlusOutlined,
  HeartOutlined,
  HeartFilled,
  ExportOutlined,
  DeleteOutlined,
  CalendarOutlined,
  WalletOutlined,
  EnvironmentOutlined,
  CoffeeOutlined
} from '@ant-design/icons-vue'
import { usePlansStore } from '@/stores/plans'
import { plansService } from '@/services/plans'
import dayjs from 'dayjs'

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

// 获取封面图片
function getCoverImage(plan: any): string | null {
  if (!plan.plan_data || !Array.isArray(plan.plan_data)) return null

  // 遍历所有天的行程，找到第一个有图片的景点
  for (const day of plan.plan_data) {
    if (day.attractions && Array.isArray(day.attractions)) {
      for (const attraction of day.attractions) {
        // 优先使用 image_url，如果没有则使用 photos 数组的第一张
        if (attraction.image_url) {
          return attraction.image_url
        }
        if (attraction.photos && Array.isArray(attraction.photos) && attraction.photos.length > 0) {
          return attraction.photos[0]
        }
      }
    }
  }
  return null
}

// 格式化日期范围
function formatDateRange(startDate: string, endDate: string): string {
  const start = dayjs(startDate).format('MM月DD日')
  const end = dayjs(endDate).format('MM月DD日')
  const days = dayjs(endDate).diff(dayjs(startDate), 'day') + 1
  return `${start} - ${end} (${days}天)`
}

// 获取总预算
function getBudgetTotal(plan: any): number {
  if (!plan.plan_data || !Array.isArray(plan.plan_data)) return 0

  let total = 0
  for (const day of plan.plan_data) {
    // 酒店费用
    if (day.hotel && day.hotel.estimated_cost) {
      total += parseFloat(day.hotel.estimated_cost) || 0
    }
    // 景点费用
    if (day.attractions && Array.isArray(day.attractions)) {
      for (const attraction of day.attractions) {
        if (attraction.ticket_price) {
          total += parseFloat(attraction.ticket_price) || 0
        }
      }
    }
    // 餐饮费用
    if (day.meals && Array.isArray(day.meals)) {
      for (const meal of day.meals) {
        if (meal.estimated_cost) {
          total += parseFloat(meal.estimated_cost) || 0
        }
      }
    }
  }
  return Math.round(total)
}

// 获取景点数量
function getAttractionCount(plan: any): number {
  if (!plan.plan_data || !Array.isArray(plan.plan_data)) return 0

  let count = 0
  for (const day of plan.plan_data) {
    if (day.attractions && Array.isArray(day.attractions)) {
      count += day.attractions.length
    }
  }
  return count
}

// 获取餐厅数量
function getMealCount(plan: any): number {
  if (!plan.plan_data || !Array.isArray(plan.plan_data)) return 0

  let count = 0
  for (const day of plan.plan_data) {
    if (day.meals && Array.isArray(day.meals)) {
      count += day.meals.length
    }
  }
  return count
}

// 获取前3个景点名称
function getTopAttractions(plan: any): string[] {
  if (!plan.plan_data || !Array.isArray(plan.plan_data)) return []

  const attractions: string[] = []
  for (const day of plan.plan_data) {
    if (day.attractions && Array.isArray(day.attractions)) {
      for (const attraction of day.attractions) {
        if (attraction.name && attractions.length < 3) {
          attractions.push(attraction.name)
        }
      }
    }
    if (attractions.length >= 3) break
  }
  return attractions
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
    a.download = `plan_${planId}_${dayjs().format('YYYYMMDD')}.json`
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
    content: '确定要删除这个旅行计划吗？此操作不可恢复。',
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

<style scoped lang="scss">
.plans-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 40px;
}

.page-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.plan-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  }

  .plan-cover {
    position: relative;
    height: 240px;
    overflow: hidden;

    .cover-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }

    .cover-placeholder {
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;

      .placeholder-icon {
        font-size: 64px;
        color: rgba(255, 255, 255, 0.8);
      }
    }

    .cover-overlay {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 20px;
      background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
      display: flex;
      justify-content: space-between;
      align-items: flex-end;

      .destination-title {
        margin: 0;
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
      }

      .favorite-tag {
        font-size: 14px;
        padding: 4px 12px;
        border: none;
      }
    }
  }

  &:hover .cover-image {
    transform: scale(1.05);
  }

  .plan-content {
    padding: 20px;

    .info-section {
      display: flex;
      align-items: flex-start;
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid #f0f0f0;

      &:last-of-type {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
      }

      .section-icon {
        font-size: 20px;
        color: #1890ff;
        margin-right: 12px;
        margin-top: 2px;
      }

      .section-content {
        flex: 1;

        .section-label {
          font-size: 12px;
          color: #999;
          margin-bottom: 4px;
        }

        .section-value {
          font-size: 15px;
          color: #333;
          font-weight: 500;

          &.budget-value {
            color: #52c41a;
            font-size: 18px;
            font-weight: bold;
          }
        }
      }
    }

    .attractions-preview {
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .attraction-tag {
        margin: 0;
        font-size: 13px;
        padding: 4px 12px;
        border-radius: 12px;
      }
    }
  }

  .plan-actions {
    display: flex;
    justify-content: space-around;
    padding: 12px 20px;
    background: #fafafa;
    border-top: 1px solid #f0f0f0;

    .action-btn {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      padding: 4px 8px;
      transition: all 0.2s;

      &:hover {
        transform: scale(1.05);
      }
    }
  }
}

.empty-state {
  margin-top: 100px;
  padding: 60px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
</style>

