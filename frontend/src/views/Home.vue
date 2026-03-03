<template>
  <div class="home-container">
    <!-- Navbar -->
    <nav class="navbar animate-fade-in-down">
      <div class="nav-content">
        <div class="logo">
          <span class="logo-icon">✈️</span>
          <span class="logo-text">TravelAI</span>
        </div>
        <div class="nav-links">
          <template v-if="authStore.isAuthenticated">
            <router-link to="/chat" class="nav-link">
              <span class="icon">💬</span> 对话
            </router-link>
            <router-link to="/plans" class="nav-link">
              <span class="icon">📋</span> 计划
            </router-link>
            <router-link to="/social" class="nav-link">
              <span class="icon">🌐</span> 社区
            </router-link>
            
            <a-dropdown>
              <div class="user-menu-trigger">
                <a-avatar :src="userAvatar" :size="40" class="user-avatar">
                  {{ authStore.user?.username?.[0]?.toUpperCase() }}
                </a-avatar>
                <span class="username">{{ authStore.user?.nickname || authStore.user?.username }}</span>
                <DownOutlined />
              </div>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="profile" @click="$router.push('/profile')">
                    <UserOutlined /> 个人中心
                  </a-menu-item>
                  <a-menu-item key="admin" v-if="authStore.isAdmin" @click="$router.push('/admin')">
                    <SettingOutlined /> 管理后台
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item key="logout" @click="handleLogout">
                    <LogoutOutlined /> 退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>
          <template v-else>
            <router-link to="/login" class="nav-link">登录</router-link>
            <router-link to="/register" class="nav-btn-primary">注册</router-link>
          </template>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content animate-fade-in-up">
        <h1 class="hero-title">探索世界，<br><span class="gradient-text">智绘</span>你的旅程</h1>
        <p class="hero-subtitle">
          基于AI的智能旅行助手，为你定制专属行程，记录每一次难忘足迹。
        </p>
        <div class="hero-actions">
          <a-button type="primary" size="large" class="cta-btn" @click="$router.push('/create-plan')">
            <template #icon><RocketOutlined /></template>
            开始规划
          </a-button>
          <a-button size="large" class="secondary-btn" @click="scrollToMap">
            查看足迹
          </a-button>
        </div>
      </div>
      
      <!-- Animated Background Elements -->
      <div class="hero-bg-elements">
        <div class="floating-shape shape-1"></div>
        <div class="floating-shape shape-2"></div>
        <div class="floating-shape shape-3"></div>
      </div>
    </section>

    <!-- Stats & Map Section -->
    <section id="map-section" class="map-section">
      <div class="section-container">
        <a-card class="map-card" :bordered="false">
          <template #title>
            <div class="card-header">
              <span class="header-icon">🗺️</span>
              <span class="header-title">我的旅行足迹</span>
            </div>
          </template>
          
          <div v-if="authStore.isAuthenticated">
            <!-- Stats -->
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value gradient-text">{{ visitedCities.length }}</div>
                <div class="stat-label">去过的城市</div>
              </div>
              <div class="stat-item">
                <div class="stat-value gradient-text">{{ getProvinceCount() }}</div>
                <div class="stat-label">点亮的省份</div>
              </div>
              <div class="stat-item">
                <div class="stat-value gradient-text">{{ getCoveragePercentage() }}%</div>
                <div class="stat-label">中国探索度</div>
              </div>
            </div>

            <!-- Map -->
            <div class="map-wrapper">
              <a-spin :spinning="mapLoading" tip="加载地图中...">
                <div ref="mapRef" class="echarts-map"></div>
              </a-spin>
            </div>
            
            <!-- City Tags -->
            <div class="cities-list" v-if="visitedCities.length > 0">
              <div class="cities-title">已访问城市</div>
              <div class="tags-wrapper">
                <a-tag v-for="city in visitedCities" :key="city" color="blue" class="city-tag">
                  📍 {{ city }}
                </a-tag>
              </div>
            </div>
          </div>
          
          <div v-else class="login-placeholder">
            <a-empty description="登录后开启你的足迹地图" :image="Empty.PRESENTED_IMAGE_SIMPLE">
              <a-button type="primary" @click="$router.push('/login')">立即登录</a-button>
            </a-empty>
          </div>
        </a-card>
      </div>
    </section>

    <!-- Dashboard Section -->
    <section id="dashboard-section" class="dashboard-section" v-if="authStore.isAuthenticated">
      <div class="section-container">
        <a-card class="dashboard-card" :bordered="false">
          <template #title>
            <div class="card-header">
              <span class="header-icon">📊</span>
              <span class="header-title">平台数据统计</span>
            </div>
          </template>
          
          <a-spin :spinning="dashboardLoading" tip="加载数据中...">
            <!-- Dashboard Stats Grid -->
            <div class="dashboard-stats-grid" v-if="dashboardData && dashboardData.user_stats">
              <div class="dashboard-stat-item">
                <div class="stat-icon">👥</div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData?.user_stats?.total_users ?? 0 }}</div>
                  <div class="stat-label">总用户数</div>
                </div>
                <div class="stat-trend" :class="(dashboardData?.user_stats?.user_growth_rate ?? 0) >= 0 ? 'up' : 'down'">
                  {{ (dashboardData?.user_stats?.user_growth_rate ?? 0) >= 0 ? '↑' : '↓' }} {{ Math.abs(dashboardData?.user_stats?.user_growth_rate ?? 0).toFixed(1) }}%
                </div>
              </div>
              <div class="dashboard-stat-item">
                <div class="stat-icon">📋</div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData?.content_stats?.total_plans ?? 0 }}</div>
                  <div class="stat-label">总计划数</div>
                </div>
                <div class="stat-trend up">
                  +{{ dashboardData?.content_stats?.plans_created_today ?? 0 }} 今日
                </div>
              </div>
              <div class="dashboard-stat-item">
                <div class="stat-icon">🏷️</div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData?.content_stats?.total_pois ?? 0 }}</div>
                  <div class="stat-label">景点数</div>
                </div>
              </div>
              <div class="dashboard-stat-item">
                <div class="stat-icon">💬</div>
                <div class="stat-info">
                  <div class="stat-value">{{ dashboardData?.content_stats?.total_posts ?? 0 }}</div>
                  <div class="stat-label">帖子数</div>
                </div>
                <div class="stat-trend up">
                  +{{ dashboardData?.content_stats?.posts_created_today ?? 0 }} 今日
                </div>
              </div>
            </div>

            <!-- Charts Grid -->
            <div class="charts-grid" v-if="dashboardData && dashboardData.user_stats">
              <!-- User Growth Chart -->
              <a-card class="chart-card" :bordered="false">
                <template #title>
                  <div class="chart-card-header">
                    <span>用户增长趋势</span>
                  </div>
                </template>
                <div ref="userChartRef" class="chart-container"></div>
              </a-card>

              <!-- Content Stats Chart -->
              <a-card class="chart-card" :bordered="false">
                <template #title>
                  <div class="chart-card-header">
                    <span>内容统计分布</span>
                  </div>
                </template>
                <div ref="contentChartRef" class="chart-container"></div>
              </a-card>

              <!-- Business Trend Chart -->
              <a-card class="chart-card" :bordered="false" style="grid-column: span 2;">
                <template #title>
                  <div class="chart-card-header">
                    <span>业务趋势</span>
                    <a-range-picker
                      v-model:value="dateRange"
                      @change="handleDateRangeChange"
                      style="width: 300px;"
                    />
                  </div>
                </template>
                <div ref="businessChartRef" class="chart-container"></div>
              </a-card>
            </div>

            <!-- Last Update -->
            <div class="last-update" v-if="dashboardData">
              数据更新时间: {{ formatDate(dashboardData?.updated_at) }}
            </div>
          </a-spin>
        </a-card>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Empty, RangePickerProps } from 'ant-design-vue'
import { 
  UserOutlined, 
  SettingOutlined, 
  LogoutOutlined, 
  DownOutlined,
  RocketOutlined
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { userService } from '@/services/user'
import * as echarts from 'echarts'
import chinaJson from '@/assets/china.json'
import { findProvinceByCity } from '@/data/cities'
import { 
  getDashboardOverview, 
  getBusinessTrend,
  type DashboardOverviewResponse,
  type BusinessTrendResponse
} from '@/services/dashboard'

const router = useRouter()
const authStore = useAuthStore()

const userAvatar = ref<string | undefined>()
const visitedCities = ref<string[]>([])
const mapRef = ref<HTMLElement>()
const mapLoading = ref(false)
let chartInstance: echarts.ECharts | null = null

const dashboardLoading = ref(false)
const dashboardData = ref<DashboardOverviewResponse | null>(null)
const businessTrendData = ref<BusinessTrendResponse | null>(null)
const dateRange = ref<RangePickerProps['value']>(null)
const userChartRef = ref<HTMLElement>()
const contentChartRef = ref<HTMLElement>()
const businessChartRef = ref<HTMLElement>()
let userChartInstance: echarts.ECharts | null = null
let contentChartInstance: echarts.ECharts | null = null
let businessChartInstance: echarts.ECharts | null = null

const TOTAL_PROVINCES = 34

// 省份简称 → GeoJSON 全称（与 china.json 的 feature name 完全一致）
const provinceGeoNameMap: Record<string, string> = {
  '北京': '北京市', '上海': '上海市', '天津': '天津市', '重庆': '重庆市',
  '广东': '广东省', '浙江': '浙江省', '江苏': '江苏省', '四川': '四川省',
  '湖北': '湖北省', '湖南': '湖南省', '河南': '河南省', '陕西': '陕西省',
  '山东': '山东省', '河北': '河北省', '福建': '福建省', '安徽': '安徽省',
  '江西': '江西省', '辽宁': '辽宁省', '黑龙江': '黑龙江省', '吉林': '吉林省',
  '山西': '山西省', '云南': '云南省', '贵州': '贵州省', '海南': '海南省',
  '甘肃': '甘肃省', '青海': '青海省', '台湾': '台湾省',
  '内蒙古': '内蒙古自治区', '广西': '广西壮族自治区', '西藏': '西藏自治区',
  '宁夏': '宁夏回族自治区', '新疆': '新疆维吾尔自治区',
  '香港': '香港特别行政区', '澳门': '澳门特别行政区',
}

// 获取用户头像
async function fetchUserAvatar() {
  try {
    if (authStore.user?.avatar_url) {
      userAvatar.value = authStore.user.avatar_url
    } else {
      const response = await userService.getProfile()
      userAvatar.value = response.avatar_url
      if (authStore.user) {
        authStore.setUser({
          ...authStore.user,
          avatar_url: response.avatar_url
        })
      }
    }
  } catch (error) {
    console.error('获取头像URL失败:', error)
  }
}

// 获取已访问城市
async function fetchVisitedCities() {
  try {
    const cities = await userService.getVisitedCities()
    visitedCities.value = Array.isArray(cities) ? cities : []
  } catch (error) {
    console.error('获取已访问城市失败:', error)
    visitedCities.value = []
  } finally {
    await nextTick()
    initMap()
  }
}

function getProvinceCount(): number {
  const provinces = new Set<string>()
  visitedCities.value.forEach(city => {
    const province = findProvinceByCity(city)
    if (province) provinces.add(province)
  })
  return provinces.size
}

function getCoveragePercentage(): number {
  return Math.round((getProvinceCount() / TOTAL_PROVINCES) * 100)
}

async function initMap() {
  if (!mapRef.value) return
  mapLoading.value = true
  try {
    echarts.registerMap('china', chinaJson as any)
    if (chartInstance) chartInstance.dispose()
    chartInstance = echarts.init(mapRef.value)

    // 把访问过的城市 → 省份简称 → GeoJSON 全称
    const visitedProvinceGeoNames = new Set<string>()
    visitedCities.value.forEach(city => {
      const province = findProvinceByCity(city)
      if (province && provinceGeoNameMap[province]) {
        visitedProvinceGeoNames.add(provinceGeoNameMap[province])
      }
    })

    // series.data：已访问省份 value=1（高亮色），其余由 itemStyle 默认色填充
    const mapData = Array.from(visitedProvinceGeoNames).map(name => ({
      name,
      value: 1,
    }))

    const option = {
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#667eea',
        textStyle: { color: '#fff' },
        formatter: (params: any) => {
          const visited = visitedProvinceGeoNames.has(params.name)
          return `${params.name}<br/>${visited ? '✅ 已到访' : '未到访'}`
        }
      },
      visualMap: {
        show: false,
        min: 0, max: 1,
        inRange: { color: ['#e8eaf6', '#667eea'] }
      },
      series: [{
        type: 'map',
        map: 'china',
        roam: true,
        zoom: 1.2,
        itemStyle: {
          areaColor: '#f0f0f0',
          borderColor: '#ccc'
        },
        emphasis: {
          itemStyle: {
            areaColor: '#764ba2',
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,0.2)'
          }
        },
        data: mapData
      }]
    }
    chartInstance.setOption(option)
    window.addEventListener('resize', () => chartInstance?.resize())
  } catch (error) {
    message.error('地图加载失败')
  } finally {
    mapLoading.value = false
  }
}

// 获取仪表盘数据
async function fetchDashboardData() {
  dashboardLoading.value = true
  try {
    const overview = await getDashboardOverview()
    dashboardData.value = overview
    
    await nextTick()
    initUserChart()
    initContentChart()
    initBusinessChart()
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
    message.error('获取仪表盘数据失败')
  } finally {
    dashboardLoading.value = false
  }
}

// 初始化用户增长图表
function initUserChart() {
  if (!userChartRef.value || !dashboardData.value) return
  if (userChartInstance) userChartInstance.dispose()
  
  userChartInstance = echarts.init(userChartRef.value)
  
  const stats = dashboardData.value.user_stats
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      textStyle: { color: '#fff' },
      formatter: '{b}: {c} 人'
    },
    xAxis: {
      type: 'category',
      data: ['今日新增', '本周新增', '本月新增'],
      axisLabel: { color: '#666' },
      axisLine: { lineStyle: { color: '#e0e0e0' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#f0f0f0' } }
    },
    series: [{
      data: [stats.new_users_today ?? 0, stats.new_users_week ?? 0, stats.new_users_month ?? 0],
      type: 'bar',
      barWidth: '40%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#4facfe' },
          { offset: 1, color: '#00f2fe' }
        ]),
        borderRadius: [8, 8, 0, 0]
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(79, 172, 254, 0.5)'
        }
      },
      label: {
        show: true,
        position: 'top',
        color: '#4facfe',
        fontSize: 14,
        fontWeight: 'bold',
        formatter: '{c}'
      }
    }],
    grid: {
      left: '10%',
      right: '10%',
      bottom: '10%',
      top: '20%'
    }
  }
  
  userChartInstance.setOption(option)
  window.addEventListener('resize', () => userChartInstance?.resize())
}

// 初始化内容统计图表
function initContentChart() {
  if (!contentChartRef.value || !dashboardData.value) return
  if (contentChartInstance) contentChartInstance.dispose()
  
  contentChartInstance = echarts.init(contentChartRef.value)
  
  const stats = dashboardData.value.content_stats
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      textStyle: { color: '#fff' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}: {c}'
      },
      data: [
        { value: stats.total_plans, name: '旅行计划', itemStyle: { color: '#667eea' } },
        { value: stats.total_pois, name: '景点', itemStyle: { color: '#764ba2' } },
        { value: stats.total_posts, name: '帖子', itemStyle: { color: '#f093fb' } },
        { value: stats.total_comments, name: '评论', itemStyle: { color: '#f5576c' } }
      ]
    }]
  }
  
  contentChartInstance.setOption(option)
  window.addEventListener('resize', () => contentChartInstance?.resize())
}

// 初始化业务趋势图表
async function initBusinessChart() {
  if (!businessChartRef.value) return
  if (businessChartInstance) businessChartInstance.dispose()
  
  businessChartInstance = echarts.init(businessChartRef.value)
  
  let data = businessTrendData.value
  if (!data) {
    try {
      data = await getBusinessTrend()
      businessTrendData.value = data
    } catch (error) {
      console.error('获取业务趋势失败:', error)
      return
    }
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      textStyle: { color: '#fff' }
    },
    legend: {
      data: ['旅行计划', '用户注册', '用户活跃'],
      textStyle: { color: '#666' },
      top: 10
    },
    xAxis: {
      type: 'category',
      data: data.date_range,
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#666' }
    },
    series: [
      {
        name: '旅行计划',
        type: 'line',
        data: data.plan_creation_trend,
        smooth: true,
        itemStyle: { color: '#667eea' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        }
      },
      {
        name: '用户注册',
        type: 'line',
        data: data.user_registration_trend,
        smooth: true,
        itemStyle: { color: '#764ba2' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(118, 75, 162, 0.3)' },
            { offset: 1, color: 'rgba(118, 75, 162, 0.05)' }
          ])
        }
      },
      {
        name: '用户活跃',
        type: 'line',
        data: data.user_activity_trend,
        smooth: true,
        itemStyle: { color: '#f093fb' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(240, 147, 251, 0.3)' },
            { offset: 1, color: 'rgba(240, 147, 251, 0.05)' }
          ])
        }
      }
    ],
    grid: {
      left: '5%',
      right: '5%',
      bottom: '10%',
      top: '15%'
    }
  }
  
  businessChartInstance.setOption(option)
  window.addEventListener('resize', () => businessChartInstance?.resize())
}

// 处理日期范围变化
async function handleDateRangeChange(dates: any) {
  if (dates && dates.length === 2) {
    try {
      businessTrendData.value = await getBusinessTrend({
        start_date: dates[0].format('YYYY-MM-DD'),
        end_date: dates[1].format('YYYY-MM-DD')
      })
      initBusinessChart()
    } catch (error) {
      console.error('获取业务趋势失败:', error)
      message.error('获取业务趋势失败')
    }
  }
}

// 格式化日期
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function handleLogout() {
  authStore.logout()
  message.success('已退出登录')
  router.push('/')
}

function scrollToMap() {
  document.getElementById('map-section')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await fetchUserAvatar()
    await fetchVisitedCities()
    await fetchDashboardData()
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  if (userChartInstance) {
    userChartInstance.dispose()
    userChartInstance = null
  }
  if (contentChartInstance) {
    contentChartInstance.dispose()
    contentChartInstance = null
  }
  if (businessChartInstance) {
    businessChartInstance.dispose()
    businessChartInstance = null
  }
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #fff;
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 100;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 800;
  color: var(--primary-color);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-link {
  color: var(--text-secondary);
  font-weight: 500;
  text-decoration: none;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link:hover {
  color: var(--primary-color);
}

.nav-btn-primary {
  padding: 8px 24px;
  background: var(--bg-gradient);
  color: white;
  border-radius: 20px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.nav-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 20px;
  transition: background 0.3s;
}

.user-menu-trigger:hover {
  background: var(--bg-secondary);
}

.hero-section {
  padding-top: 64px;
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  text-align: center;
}

.hero-content {
  z-index: 10;
  max-width: 800px;
  padding: 0 20px;
}

.hero-title {
  font-size: 64px;
  font-weight: 900;
  line-height: 1.2;
  margin-bottom: 24px;
  color: var(--text-primary);
}

.hero-subtitle {
  font-size: 20px;
  color: var(--text-secondary);
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.cta-btn {
  height: 56px;
  padding: 0 40px;
  border-radius: 28px;
  font-size: 18px;
  background: var(--bg-gradient);
  border: none;
}

.secondary-btn {
  height: 56px;
  padding: 0 40px;
  border-radius: 28px;
  font-size: 18px;
}

.hero-bg-elements .floating-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  z-index: 1;
}

.shape-1 {
  width: 400px;
  height: 400px;
  background: rgba(102, 126, 234, 0.2);
  top: -100px;
  left: -100px;
  animation: float 10s infinite;
}

.shape-2 {
  width: 300px;
  height: 300px;
  background: rgba(240, 147, 251, 0.2);
  bottom: 0;
  right: -50px;
  animation: float 12s infinite reverse;
}

.map-section {
  padding: 80px 24px;
  background: var(--bg-secondary);
}

.dashboard-section {
  padding: 80px 24px;
  background: #fff;
}

.section-container {
  max-width: 1200px;
  margin: 0 auto;
}

.map-card,
.dashboard-card {
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
  padding: 24px;
  background: var(--bg-light-gradient);
  border-radius: var(--border-radius-lg);
}

.stat-value {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 8px;
}

.stat-label {
  color: var(--text-secondary);
}

.map-wrapper {
  height: 600px;
  background: #f5f5f5;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  margin-bottom: 32px;
}

.echarts-map {
  width: 100%;
  height: 600px;
}

:deep(.ant-spin-nested-loading),
:deep(.ant-spin-container) {
  height: 100%;
}

.cities-title {
  font-weight: 700;
  margin-bottom: 16px;
}

.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.login-placeholder {
  padding: 80px 0;
  text-align: center;
}

/* Dashboard Styles */
.dashboard-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.dashboard-stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: var(--bg-light-gradient);
  border-radius: var(--border-radius-lg);
  transition: transform 0.3s, box-shadow 0.3s;
}

.dashboard-stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 16px;
}

.stat-info {
  flex: 1;
}

.stat-info .stat-value {
  font-size: 28px;
  font-weight: 800;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.stat-info .stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.stat-trend {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.05);
}

.stat-trend.up {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.stat-trend.down {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  border-radius: var(--border-radius-lg);
}

.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.chart-container {
  height: 350px;
}

.last-update {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

/* Animations */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
</style>
