<template>
  <div class="plan-detail-container">
    <!-- 页面头部 -->
    <a-page-header
      :title="plansStore.currentPlan?.destination || '旅行计划'"
      @back="$router.back()"
      class="page-header"
    >
      <template #tags>
        <a-tag v-if="plansStore.currentPlan?.is_favorite" color="red">
          <HeartFilled /> 已收藏
        </a-tag>
      </template>
      <template #extra>
        <a-space>
          <a-button @click="toggleFavorite" type="text">
            <HeartFilled v-if="plansStore.currentPlan?.is_favorite" style="color: #ff4d4f" />
            <HeartOutlined v-else />
            {{ plansStore.currentPlan?.is_favorite ? '取消收藏' : '收藏' }}
          </a-button>
          <a-button @click="exportPlan" type="primary">
            <ExportOutlined /> 导出计划
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="content-wrapper">
      <a-spin :spinning="loading" size="large">
        <div v-if="plansStore.currentPlan" class="plan-content">
          <!-- 基本信息卡片 -->
          <a-card class="info-card" :bordered="false">
            <a-row :gutter="[24, 24]">
              <a-col :xs="24" :sm="12" :md="6">
                <a-statistic title="目的地" :value="plansStore.currentPlan.destination">
                  <template #prefix>
                    <EnvironmentOutlined />
                  </template>
                </a-statistic>
              </a-col>
              <a-col :xs="24" :sm="12" :md="6">
                <a-statistic title="出发日期" :value="plansStore.currentPlan.start_date">
                  <template #prefix>
                    <CalendarOutlined />
                  </template>
                </a-statistic>
              </a-col>
              <a-col :xs="24" :sm="12" :md="6">
                <a-statistic title="返回日期" :value="plansStore.currentPlan.end_date || plansStore.currentPlan.start_date">
                  <template #prefix>
                    <CalendarOutlined />
                  </template>
                </a-statistic>
              </a-col>
              <a-col :xs="24" :sm="12" :md="6">
                <a-statistic
                  title="总预算"
                  :value="getBudgetTotal()"
                  :precision="0"
                  suffix="元"
                >
                  <template #prefix>
                    <WalletOutlined />
                  </template>
                </a-statistic>
              </a-col>
            </a-row>

            <a-divider />

            <div class="meta-info">
              <a-space :size="16">
                <span><ClockCircleOutlined /> 创建时间：{{ formatDateTime(plansStore.currentPlan.created_at) }}</span>
                <span><SyncOutlined /> 更新时间：{{ formatDateTime(plansStore.currentPlan.updated_at) }}</span>
              </a-space>
            </div>
          </a-card>

          <!-- 预算详情卡片 -->
          <a-card v-if="plansStore.currentPlan.budget" title="预算详情" class="budget-card" :bordered="false">
            <a-row :gutter="[16, 16]">
              <a-col :xs="12" :sm="6">
                <div class="budget-item">
                  <div class="budget-icon" style="background: #1890ff">
                    <HomeOutlined />
                  </div>
                  <div class="budget-info">
                    <div class="budget-label">住宿费用</div>
                    <div class="budget-value">¥{{ plansStore.currentPlan.budget.total_hotels || 0 }}</div>
                  </div>
                </div>
              </a-col>
              <a-col :xs="12" :sm="6">
                <div class="budget-item">
                  <div class="budget-icon" style="background: #52c41a">
                    <EnvironmentOutlined />
                  </div>
                  <div class="budget-info">
                    <div class="budget-label">景点费用</div>
                    <div class="budget-value">¥{{ plansStore.currentPlan.budget.total_attractions || 0 }}</div>
                  </div>
                </div>
              </a-col>
              <a-col :xs="12" :sm="6">
                <div class="budget-item">
                  <div class="budget-icon" style="background: #faad14">
                    <CoffeeOutlined />
                  </div>
                  <div class="budget-info">
                    <div class="budget-label">餐饮费用</div>
                    <div class="budget-value">¥{{ plansStore.currentPlan.budget.total_meals || 0 }}</div>
                  </div>
                </div>
              </a-col>
              <a-col :xs="12" :sm="6">
                <div class="budget-item">
                  <div class="budget-icon" style="background: #f5222d">
                    <CarOutlined />
                  </div>
                  <div class="budget-info">
                    <div class="budget-label">交通费用</div>
                    <div class="budget-value">¥{{ plansStore.currentPlan.budget.total_transportation || 0 }}</div>
                  </div>
                </div>
              </a-col>
            </a-row>
          </a-card>

          <!-- 总体建议 -->
          <a-card
            v-if="plansStore.currentPlan.overall_suggestions"
            title="旅行建议"
            class="suggestions-card"
            :bordered="false"
          >
            <a-alert :message="plansStore.currentPlan.overall_suggestions" type="info" show-icon />
          </a-card>

          <!-- 行程详情 -->
          <a-card title="行程详情" class="itinerary-card" :bordered="false">
            <a-timeline mode="left">
              <a-timeline-item
                v-for="(day, index) in plansStore.currentPlan.plan_data"
                :key="index"
                :color="index === 0 ? 'green' : 'blue'"
              >
                <template #dot>
                  <CalendarOutlined style="font-size: 18px" />
                </template>

                <div class="day-card">
                  <div class="day-header">
                    <h3>第 {{ day.day_index || index + 1 }} 天</h3>
                    <a-tag color="blue">{{ day.date }}</a-tag>
                  </div>

                  <p class="day-description">{{ day.description }}</p>

                  <!-- 住宿信息 -->
                  <div v-if="day.hotel" class="section">
                    <h4><HomeOutlined /> 住宿</h4>
                    <a-card size="small" class="hotel-card">
                      <a-row :gutter="16">
                        <a-col :span="18">
                          <h5>{{ day.hotel.name }}</h5>
                          <p><EnvironmentOutlined /> {{ day.hotel.address }}</p>
                          <a-space>
                            <a-tag color="orange">{{ day.hotel.type }}</a-tag>
                            <a-tag color="green">{{ day.hotel.price_range }}</a-tag>
                            <a-rate :value="parseFloat(day.hotel.rating)" disabled allow-half />
                          </a-space>
                        </a-col>
                        <a-col :span="6" class="text-right">
                          <div class="price-tag">
                            <div class="price-label">预估价格</div>
                            <div class="price-value">¥{{ day.hotel.estimated_cost }}</div>
                          </div>
                        </a-col>
                      </a-row>
                    </a-card>
                  </div>

                  <!-- 景点信息 -->
                  <div v-if="day.attractions && day.attractions.length > 0" class="section">
                    <h4><EnvironmentOutlined /> 景点游览</h4>
                    <a-row :gutter="[16, 16]">
                      <a-col
                        v-for="(attraction, aIndex) in day.attractions"
                        :key="aIndex"
                        :xs="24"
                        :sm="12"
                      >
                        <a-card size="small" class="attraction-card" hoverable>
                          <div class="attraction-content">
                            <div class="attraction-image">
                              <img
                                v-if="getAttractionImage(attraction)"
                                :src="getAttractionImage(attraction)"
                                :alt="attraction.name"
                              />
                              <div v-else class="placeholder-image">
                                <PictureOutlined />
                              </div>
                            </div>
                            <div class="attraction-info">
                              <h5>{{ attraction.name }}</h5>
                              <p class="attraction-desc">{{ attraction.description }}</p>
                              <a-space>
                                <a-tag color="blue">{{ attraction.category }}</a-tag>
                                <span><ClockCircleOutlined /> {{ attraction.visit_duration }}分钟</span>
                                <span v-if="attraction.ticket_price"><WalletOutlined /> ¥{{ attraction.ticket_price }}</span>
                              </a-space>
                            </div>
                          </div>
                        </a-card>
                      </a-col>
                    </a-row>
                  </div>

                  <!-- 餐饮信息 -->
                  <div v-if="day.meals && day.meals.length > 0" class="section">
                    <h4><CoffeeOutlined /> 餐饮安排</h4>
                    <a-row :gutter="[16, 16]">
                      <a-col
                        v-for="(meal, mIndex) in day.meals"
                        :key="mIndex"
                        :xs="24"
                        :sm="8"
                      >
                        <a-card size="small" class="meal-card">
                          <div class="meal-type">
                            <a-tag :color="getMealColor(meal.type)">
                              {{ getMealLabel(meal.type) }}
                            </a-tag>
                          </div>
                          <h5>{{ meal.name }}</h5>
                          <p>{{ meal.description }}</p>
                          <div class="meal-cost">
                            <WalletOutlined /> 预估 ¥{{ meal.estimated_cost }}
                          </div>
                        </a-card>
                      </a-col>
                    </a-row>
                  </div>
                </div>
              </a-timeline-item>
            </a-timeline>
          </a-card>

          <!-- 天气信息 -->
          <a-card
            v-if="plansStore.currentPlan.weather_info && plansStore.currentPlan.weather_info.length > 0"
            title="天气预报"
            class="weather-card"
            :bordered="false"
          >
            <a-row :gutter="[16, 16]">
              <a-col
                v-for="(weather, index) in plansStore.currentPlan.weather_info"
                :key="index"
                :xs="12"
                :sm="8"
                :md="6"
              >
                <div class="weather-item">
                  <div class="weather-date">{{ weather.date }}</div>
                  <div class="weather-info">
                    <CloudOutlined class="weather-icon" />
                    <div>{{ weather.day_weather }}</div>
                  </div>
                  <div class="weather-temp">
                    {{ weather.day_temp }}°C / {{ weather.night_temp }}°C
                  </div>
                  <div class="weather-wind">
                    {{ weather.wind_direction }} {{ weather.wind_power }}
                  </div>
                </div>
              </a-col>
            </a-row>
          </a-card>
        </div>
      </a-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  HeartOutlined,
  HeartFilled,
  ExportOutlined,
  CalendarOutlined,
  EnvironmentOutlined,
  WalletOutlined,
  ClockCircleOutlined,
  SyncOutlined,
  HomeOutlined,
  CoffeeOutlined,
  CarOutlined,
  CloudOutlined,
  PictureOutlined
} from '@ant-design/icons-vue'
import { usePlansStore } from '@/stores/plans'
import { plansService } from '@/services/plans'
import dayjs from 'dayjs'

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

// 格式化日期时间
function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

// 获取总预算
function getBudgetTotal(): number {
  const budget = plansStore.currentPlan?.budget
  if (!budget) return 0
  return budget.total || 0
}

// 获取餐饮类型颜色
function getMealColor(type: string): string {
  const colors: Record<string, string> = {
    breakfast: 'orange',
    lunch: 'green',
    dinner: 'red'
  }
  return colors[type] || 'blue'
}

// 获取餐饮类型标签
function getMealLabel(type: string): string {
  const labels: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐'
  }
  return labels[type] || type
}

// 获取景点图片 - 优先使用 image_url，如果没有则使用 photos 数组的第一张
function getAttractionImage(attraction: any): string | null {
  if (attraction.image_url) {
    return attraction.image_url
  }
  if (attraction.photos && Array.isArray(attraction.photos) && attraction.photos.length > 0) {
    return attraction.photos[0]
  }
  return null
}

async function toggleFavorite() {
  if (!plansStore.currentPlan) return
  try {
    await plansService.toggleFavorite(plansStore.currentPlan.id)
    plansStore.toggleFavorite(plansStore.currentPlan.id)
    message.success('操作成功')
  } catch (error) {
    message.error('操作失败')
  }
}

async function exportPlan() {
  if (!plansStore.currentPlan) return
  try {
    const blob = await plansService.exportPlan(plansStore.currentPlan.id, 'json')
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `plan_${plansStore.currentPlan.destination}_${dayjs().format('YYYYMMDD')}.json`
    a.click()
    window.URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
  }
}
</script>

<style scoped lang="scss">
.plan-detail-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding-bottom: 40px;
}

.page-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.content-wrapper {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
}

.plan-content {
  > * {
    margin-bottom: 24px;
  }
}

.info-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .meta-info {
    color: #666;
    font-size: 14px;
  }
}

.budget-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .budget-item {
    display: flex;
    align-items: center;
    padding: 16px;
    background: #f5f5f5;
    border-radius: 8px;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .budget-icon {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 24px;
      margin-right: 12px;
    }

    .budget-info {
      flex: 1;

      .budget-label {
        font-size: 12px;
        color: #666;
        margin-bottom: 4px;
      }

      .budget-value {
        font-size: 20px;
        font-weight: bold;
        color: #333;
      }
    }
  }
}

.suggestions-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.itinerary-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .day-card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    .day-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      h3 {
        margin: 0;
        font-size: 20px;
        color: #1890ff;
      }
    }

    .day-description {
      color: #666;
      margin-bottom: 24px;
      line-height: 1.6;
    }

    .section {
      margin-bottom: 24px;

      h4 {
        font-size: 16px;
        color: #333;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .hotel-card {
      border: 1px solid #e8e8e8;
      border-radius: 8px;

      h5 {
        margin: 0 0 8px 0;
        font-size: 16px;
        color: #333;
      }

      p {
        margin: 0 0 12px 0;
        color: #666;
        font-size: 14px;
      }

      .text-right {
        text-align: right;
      }

      .price-tag {
        .price-label {
          font-size: 12px;
          color: #999;
          margin-bottom: 4px;
        }

        .price-value {
          font-size: 24px;
          font-weight: bold;
          color: #f5222d;
        }
      }
    }

    .attraction-card {
      border-radius: 8px;
      overflow: hidden;
      height: 100%;

      .attraction-content {
        .attraction-image {
          width: 100%;
          height: 180px;
          overflow: hidden;
          border-radius: 8px;
          margin-bottom: 12px;

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          .placeholder-image {
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            color: white;
          }
        }

        .attraction-info {
          h5 {
            margin: 0 0 8px 0;
            font-size: 16px;
            color: #333;
          }

          .attraction-desc {
            color: #666;
            font-size: 14px;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
        }
      }
    }

    .meal-card {
      border: 1px solid #e8e8e8;
      border-radius: 8px;
      height: 100%;

      .meal-type {
        margin-bottom: 8px;
      }

      h5 {
        margin: 0 0 8px 0;
        font-size: 15px;
        color: #333;
      }

      p {
        color: #666;
        font-size: 13px;
        margin-bottom: 12px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .meal-cost {
        color: #f5222d;
        font-weight: bold;
      }
    }
  }
}

.weather-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  .weather-item {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px;
    border-radius: 8px;
    text-align: center;

    .weather-date {
      font-size: 14px;
      margin-bottom: 8px;
      opacity: 0.9;
    }

    .weather-info {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      margin-bottom: 8px;

      .weather-icon {
        font-size: 24px;
      }
    }

    .weather-temp {
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 4px;
    }

    .weather-wind {
      font-size: 12px;
      opacity: 0.8;
    }
  }
}
</style>
