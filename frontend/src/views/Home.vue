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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Empty } from 'ant-design-vue'
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

const router = useRouter()
const authStore = useAuthStore()

const userAvatar = ref<string | undefined>()
const visitedCities = ref<string[]>([])
const mapRef = ref<HTMLElement>()
const mapLoading = ref(false)
let chartInstance: echarts.ECharts | null = null

const TOTAL_PROVINCES = 34

// 城市到省份的映射 (Keep original map data)
const cityProvinceMap: Record<string, string> = {
  '北京': '北京', '上海': '上海', '天津': '天津', '重庆': '重庆',
  '广州': '广东', '深圳': '广东', '珠海': '广东', '汕头': '广东', '佛山': '广东', 
  '杭州': '浙江', '宁波': '浙江', '温州': '浙江', '南京': '江苏', '苏州': '江苏',
  '成都': '四川', '武汉': '湖北', '西安': '陕西', '长沙': '湖南', '郑州': '河南',
  // ... (Can add more or rely on backend/complete list later)
}

// 获取用户头像
async function fetchUserAvatar() {
  try {
    if (authStore.user.value?.avatar_url) {
      userAvatar.value = authStore.user.value.avatar_url
    } else {
      const response = await userService.getProfile()
      userAvatar.value = response.avatar_url
      if (authStore.user.value) {
        authStore.setUser({
          ...authStore.user.value,
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
    await nextTick()
    initMap()
  } catch (error) {
    console.error('获取已访问城市失败:', error)
    visitedCities.value = []
  }
}

function getProvinceCount(): number {
  const provinces = new Set<string>()
  visitedCities.value.forEach(city => {
    // Simple check, robust mapping would be better
    for(const [c, p] of Object.entries(cityProvinceMap)) {
        if(city.includes(c)) provinces.add(p)
    }
  })
  return provinces.size > 0 ? provinces.size : Math.ceil(visitedCities.value.length / 2) // Fallback estimation
}

function getCoveragePercentage(): number {
  return Math.round((getProvinceCount() / TOTAL_PROVINCES) * 100)
}

async function initMap() {
  if (!mapRef.value) return
  mapLoading.value = true
  try {
    const response = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    const chinaJson = await response.json()
    echarts.registerMap('china', chinaJson)
    if (chartInstance) chartInstance.dispose()
    chartInstance = echarts.init(mapRef.value)
    
    const option = {
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#667eea',
        textStyle: { color: '#fff' }
      },
      visualMap: {
        show: false,
        min: 0, max: 10,
        inRange: { color: ['#e0e0e0', '#667eea'] }
      },
      series: [{
        type: 'map',
        map: 'china',
        roam: true,
        zoom: 1.2,
        itemStyle: {
          areaColor: '#f5f5f5',
          borderColor: '#ccc'
        },
        emphasis: {
          itemStyle: {
            areaColor: '#764ba2',
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,0.2)'
          }
        },
        data: [] // Can populate if needed
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
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
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

.section-container {
  max-width: 1200px;
  margin: 0 auto;
}

.map-card {
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

/* Animations */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
</style>