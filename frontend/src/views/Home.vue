<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-content">
        <div class="nav-left">
          <span class="logo">✈️ 智能旅行助手</span>
        </div>
        <div class="nav-right">
          <template v-if="authStore.isAuthenticated">
            <a-button type="link" @click="$router.push('/chat')" class="nav-link">
              💬 对话
            </a-button>
            <a-button type="link" @click="$router.push('/plans')" class="nav-link">
              📋 我的计划
            </a-button>
            <a-button type="link" @click="$router.push('/social')" class="nav-link">
              🌐 动态
            </a-button>
            <a-dropdown>
                <img v-if="userAvatar" :src="userAvatar" style="width: 40px; height: 40px; border-radius: 50%; cursor: pointer;" alt="头像" />
                <a-avatar v-else style="width: 40px; height: 40px; cursor: pointer;">
                  {{ authStore.user.value?.username?.[0] }}
                </a-avatar>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="$router.push('/profile')">
                    <UserOutlined /> 个人中心
                  </a-menu-item>
                  <a-menu-item v-if="authStore.isAdmin" @click="$router.push('/admin')">
                    <SettingOutlined /> 管理后台
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item @click="handleLogout">
                    <LogoutOutlined /> 退出登录
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </template>
          <template v-else>
            <a-button type="link" @click="$router.push('/login')" class="nav-link">
              登录
            </a-button>
            <a-button type="primary" @click="$router.push('/register')" class="nav-button">
              注册
            </a-button>
          </template>
        </div>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 页面标题 -->
    <div class="page-header">
      <div class="icon-wrapper">
        <span class="icon">✈️</span>
      </div>
      <h1 class="page-title">智能旅行助手</h1>
      <p class="page-subtitle">基于AI的个性化旅行规划,让每一次出行都完美无忧</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-wrapper">
      <!-- 创建计划按钮 -->
      <div class="action-section">
        <a-button
          type="primary"
          size="large"
          @click="$router.push('/create-plan')"
          class="create-plan-button"
        >
          <span class="button-icon">🚀</span>
          <span>开始规划我的旅行</span>
        </a-button>
      </div>

      <!-- 旅行足迹卡片 -->
      <a-card class="map-card" :bordered="false" v-if="authStore.isAuthenticated">
        <template #title>
          <div class="card-title">
            <span class="title-icon">🗺️</span>
            <span>我的旅行足迹</span>
          </div>
        </template>

        <!-- 统计信息 -->
        <div class="stats-section">
          <div class="stat-item">
            <div class="stat-value">{{ visitedCities.length }}</div>
            <div class="stat-label">去过的城市</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ getProvinceCount() }}</div>
            <div class="stat-label">去过的省份</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ getCoveragePercentage() }}%</div>
            <div class="stat-label">覆盖率</div>
          </div>
        </div>

        <!-- 地图容器 -->
        <div class="map-container">
          <a-spin :spinning="mapLoading" tip="加载地图中...">
            <div ref="mapRef" class="china-map"></div>
          </a-spin>
        </div>

        <!-- 城市列表 -->
        <div class="cities-list" v-if="visitedCities.length > 0">
          <div class="cities-title">已访问城市：</div>
          <div class="cities-tags">
            <a-tag
              v-for="city in visitedCities"
              :key="city"
              color="blue"
              class="city-tag"
            >
              📍 {{ city }}
            </a-tag>
          </div>
        </div>

        <!-- 空状态 -->
        <a-empty
          v-else
          description="还没有旅行足迹，快去创建你的第一个旅行计划吧！"
          class="empty-state"
        >
          <a-button type="primary" @click="$router.push('/create-plan')">
            创建旅行计划
          </a-button>
        </a-empty>
      </a-card>

      <!-- 未登录提示 -->
      <a-card class="map-card" :bordered="false" v-else>
        <a-empty description="登录后查看你的旅行足迹">
          <a-button type="primary" @click="$router.push('/login')">
            立即登录
          </a-button>
        </a-empty>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, SettingOutlined, LogoutOutlined } from '@ant-design/icons-vue'
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

// 中国省份总数（用于计算覆盖率）
const TOTAL_PROVINCES = 34

// 城市到省份的映射
const cityProvinceMap: Record<string, string> = {
  // 直辖市
  '北京': '北京',
  '上海': '上海',
  '天津': '天津',
  '重庆': '重庆',

  // 广东省
  '广州': '广东',
  '深圳': '广东',
  '珠海': '广东',
  '汕头': '广东',
  '佛山': '广东',
  '韶关': '广东',
  '湛江': '广东',
  '肇庆': '广东',
  '江门': '广东',
  '茂名': '广东',
  '惠州': '广东',
  '梅州': '广东',
  '汕尾': '广东',
  '河源': '广东',
  '阳江': '广东',
  '清远': '广东',
  '东莞': '广东',
  '中山': '广东',
  '潮州': '广东',
  '揭阳': '广东',
  '云浮': '广东',

  // 浙江省
  '杭州': '浙江',
  '宁波': '浙江',
  '温州': '浙江',
  '嘉兴': '浙江',
  '湖州': '浙江',
  '绍兴': '浙江',
  '金华': '浙江',
  '衢州': '浙江',
  '舟山': '浙江',
  '台州': '浙江',
  '丽水': '浙江',

  // 江苏省
  '南京': '江苏',
  '无锡': '江苏',
  '徐州': '江苏',
  '常州': '江苏',
  '苏州': '江苏',
  '南通': '江苏',
  '连云港': '江苏',
  '淮安': '江苏',
  '盐城': '江苏',
  '扬州': '江苏',
  '镇江': '江苏',
  '泰州': '江苏',
  '宿迁': '江苏',

  // 福建省
  '福州': '福建',
  '厦门': '福建',
  '莆田': '福建',
  '三明': '福建',
  '泉州': '福建',
  '漳州': '福建',
  '南平': '福建',
  '龙岩': '福建',
  '宁德': '福建',

  // 湖南省
  '长沙': '湖南',
  '株洲': '湖南',
  '湘潭': '湖南',
  '衡阳': '湖南',
  '邵阳': '湖南',
  '岳阳': '湖南',
  '常德': '湖南',
  '张家界': '湖南',
  '益阳': '湖南',
  '郴州': '湖南',
  '永州': '湖南',
  '怀化': '湖南',
  '娄底': '湖南',
  '湘西': '湖南',

  // 湖北省
  '武汉': '湖北',
  '黄石': '湖北',
  '十堰': '湖北',
  '宜昌': '湖北',
  '襄阳': '湖北',
  '鄂州': '湖北',
  '荆门': '湖北',
  '孝感': '湖北',
  '荆州': '湖北',
  '黄冈': '湖北',
  '咸宁': '湖北',
  '随州': '湖北',
  '恩施': '湖北',

  // 江西省
  '南昌': '江西',
  '景德镇': '江西',
  '萍乡': '江西',
  '九江': '江西',
  '新余': '江西',
  '鹰潭': '江西',
  '赣州': '江西',
  '吉安': '江西',
  '宜春': '江西',
  '抚州': '江西',
  '上饶': '江西',

  // 安徽省
  '合肥': '安徽',
  '芜湖': '安徽',
  '蚌埠': '安徽',
  '淮南': '安徽',
  '马鞍山': '安徽',
  '淮北': '安徽',
  '铜陵': '安徽',
  '安庆': '安徽',
  '黄山': '安徽',
  '滁州': '安徽',
  '阜阳': '安徽',
  '宿州': '安徽',
  '六安': '安徽',
  '亳州': '安徽',
  '池州': '安徽',
  '宣城': '安徽',

  // 广西壮族自治区
  '南宁': '广西',
  '柳州': '广西',
  '桂林': '广西',
  '梧州': '广西',
  '北海': '广西',
  '防城港': '广西',
  '钦州': '广西',
  '贵港': '广西',
  '玉林': '广西',
  '百色': '广西',
  '贺州': '广西',
  '河池': '广西',
  '来宾': '广西',
  '崇左': '广西',

  // 河北省
  '石家庄': '河北',
  '唐山': '河北',
  '秦皇岛': '河北',
  '邯郸': '河北',
  '邢台': '河北',
  '保定': '河北',
  '张家口': '河北',
  '承德': '河北',
  '沧州': '河北',
  '廊坊': '河北',
  '衡水': '河北',

  // 四川省
  '成都': '四川',
  '自贡': '四川',
  '攀枝花': '四川',
  '泸州': '四川',
  '德阳': '四川',
  '绵阳': '四川',
  '广元': '四川',
  '遂宁': '四川',
  '内江': '四川',
  '乐山': '四川',
  '南充': '四川',
  '眉山': '四川',
  '宜宾': '四川',
  '广安': '四川',
  '达州': '四川',
  '雅安': '四川',
  '巴中': '四川',
  '资阳': '四川',
  '阿坝': '四川',
  '甘孜': '四川',
  '凉山': '四川',

  // 其他省份主要城市
  '西安': '陕西',
  '郑州': '河南',
  '济南': '山东',
  '青岛': '山东',
  '烟台': '山东',
  '昆明': '云南',
  '大理': '云南',
  '丽江': '云南',
  '拉萨': '西藏',
  '乌鲁木齐': '新疆',
  '哈尔滨': '黑龙江',
  '长春': '吉林',
  '沈阳': '辽宁',
  '大连': '辽宁',
  '呼和浩特': '内蒙古',
  '银川': '宁夏',
  '兰州': '甘肃',
  '西宁': '青海',
  '贵阳': '贵州',
  '海口': '海南',
  '三亚': '海南',
  '太原': '山西',
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

    // 等待DOM更新后初始化地图
    await nextTick()
    initMap()
  } catch (error) {
    console.error('获取已访问城市失败:', error)
    visitedCities.value = []
  }
}

// 获取去过的省份数量
function getProvinceCount(): number {
  const provinces = new Set<string>()
  visitedCities.value.forEach(city => {
    const province = getCityProvince(city)
    if (province) {
      provinces.add(province)
    }
  })
  return provinces.size
}

// 获取覆盖率
function getCoveragePercentage(): number {
  const provinceCount = getProvinceCount()
  return Math.round((provinceCount / TOTAL_PROVINCES) * 100)
}

// 根据城市名称获取省份
function getCityProvince(city: string): string {
  return cityProvinceMap[city] || ''
}

// 初始化地图
async function initMap() {
  if (!mapRef.value) return

  mapLoading.value = true

  try {
    // 从在线CDN加载中国地图数据
    const response = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
    const chinaJson = await response.json()

    // 注册中国地图
    echarts.registerMap('china', chinaJson)

    // 销毁旧实例
    if (chartInstance) {
      chartInstance.dispose()
    }

    // 创建新实例
    chartInstance = echarts.init(mapRef.value)

    // 获取省份访问数据
    const provinceData = getProvinceData()

    console.log('省份数据:', provinceData)
    console.log('访问的城市:', visitedCities.value)
    console.log('地图中的省份名称:', chinaJson.features.map((f: any) => f.properties.name))

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.data && params.data.value > 0) {
            return `${params.name}<br/>访问城市: ${params.data.cities.join('、')}<br/>城市数量: ${params.data.value}`
          }
          return `${params.name}<br/>未访问`
        },
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#667eea',
        borderWidth: 1,
        textStyle: {
          color: '#fff'
        }
      },
      visualMap: {
        show: provinceData.length > 0,
        min: 0,
        max: Math.max(...provinceData.map(d => d.value), 1),
        text: ['访问多', '访问少'],
        realtime: false,
        calculable: true,
        inRange: {
          color: ['#a8d5ff', '#4da6ff', '#1a8cff', '#0066cc', '#004d99']
        },
        textStyle: {
          color: '#333'
        },
        left: 'left',
        bottom: '20px'
      },
      series: [
        {
          name: '访问城市',
          type: 'map',
          map: 'china',
          roam: true,
          zoom: 1.2,
          emphasis: {
            label: {
              show: true,
              color: '#fff',
              fontSize: 12,
              fontWeight: 'bold'
            },
            itemStyle: {
              areaColor: '#ffd700',
              borderColor: '#fff',
              borderWidth: 2,
              shadowColor: 'rgba(0, 0, 0, 0.5)',
              shadowBlur: 10
            }
          },
          select: {
            label: {
              show: true,
              color: '#fff'
            },
            itemStyle: {
              areaColor: '#ffa500'
            }
          },
          itemStyle: {
            areaColor: '#f0f0f0',
            borderColor: '#ccc',
            borderWidth: 1
          },
          label: {
            show: true,
            fontSize: 11,
            color: '#666'
          },
          data: provinceData
        }
      ]
    }

    chartInstance.setOption(option)

    // 响应式调整
    const resizeHandler = () => {
      chartInstance?.resize()
    }
    window.addEventListener('resize', resizeHandler)

  } catch (error) {
    console.error('加载地图失败:', error)
    message.error('地图加载失败，请检查网络连接')
  } finally {
    mapLoading.value = false
  }
}

// 获取省份数据
function getProvinceData() {
  const provinceMap = new Map<string, string[]>()

  visitedCities.value.forEach(city => {
    const province = getCityProvince(city)
    if (province) {
      if (!provinceMap.has(province)) {
        provinceMap.set(province, [])
      }
      provinceMap.get(province)!.push(city)
    }
  })

  // 转换省份名称为地图中的完整名称
  return Array.from(provinceMap.entries()).map(([name, cities]) => ({
    name: getFullProvinceName(name),
    value: cities.length,
    cities
  }))
}

// 将简称转换为地图中的完整省份名称
function getFullProvinceName(shortName: string): string {
  const provinceNameMap: Record<string, string> = {
    '北京': '北京市',
    '天津': '天津市',
    '上海': '上海市',
    '重庆': '重庆市',
    '河北': '河北省',
    '山西': '山西省',
    '辽宁': '辽宁省',
    '吉林': '吉林省',
    '黑龙江': '黑龙江省',
    '江苏': '江苏省',
    '浙江': '浙江省',
    '安徽': '安徽省',
    '福建': '福建省',
    '江西': '江西省',
    '山东': '山东省',
    '河南': '河南省',
    '湖北': '湖北省',
    '湖南': '湖南省',
    '广东': '广东省',
    '海南': '海南省',
    '四川': '四川省',
    '贵州': '贵州省',
    '云南': '云南省',
    '陕西': '陕西省',
    '甘肃': '甘肃省',
    '青海': '青海省',
    '台湾': '台湾省',
    '内蒙古': '内蒙古自治区',
    '广西': '广西壮族自治区',
    '西藏': '西藏自治区',
    '宁夏': '宁夏回族自治区',
    '新疆': '新疆维吾尔自治区',
    '香港': '香港特别行政区',
    '澳门': '澳门特别行政区'
  }

  return provinceNameMap[shortName] || shortName
}

// 退出登录
function handleLogout() {
  authStore.logout()
  message.success('已退出登录')
  router.push('/')
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0;
  position: relative;
  overflow: hidden;
}

/* 顶部导航栏 */
.top-nav {
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-left .logo {
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-link {
  color: #333;
  font-weight: 500;
}

.nav-link:hover {
  color: #667eea;
}

.nav-button {
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: -50px;
  animation-delay: 5s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: -50px;
  left: 30%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
  }
}

/* 页面标题 */
.page-header {
  text-align: center;
  padding: 60px 20px 40px;
  animation: fadeInDown 0.8s ease-out;
  position: relative;
  z-index: 1;
}

.icon-wrapper {
  margin-bottom: 20px;
}

.icon {
  font-size: 80px;
  display: inline-block;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.page-title {
  font-size: 56px;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 16px;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 2px;
}

.page-subtitle {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  font-weight: 300;
}

/* 内容区域 */
.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 60px;
  position: relative;
  z-index: 1;
}

/* 操作区域 */
.action-section {
  text-align: center;
  margin-bottom: 40px;
}

.create-plan-button {
  height: 56px;
  padding: 0 48px;
  border-radius: 28px;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.create-plan-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
}

.create-plan-button:active {
  transform: translateY(0);
}

.button-icon {
  margin-right: 8px;
  font-size: 20px;
}

/* 地图卡片 */
.map-card {
  border-radius: 24px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.4);
  animation: fadeInUp 0.8s ease-out;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.98) !important;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.title-icon {
  margin-right: 12px;
  font-size: 28px;
}

/* 统计信息 */
.stats-section {
  display: flex;
  justify-content: space-around;
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 地图容器 */
.map-container {
  margin-bottom: 24px;
}

.china-map {
  width: 100%;
  height: 800px;
  border-radius: 12px;
  background: #fff;
}

/* 城市列表 */
.cities-list {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 16px;
}

.cities-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

.cities-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.city-tag {
  font-size: 14px;
  padding: 4px 12px;
  border-radius: 12px;
}

/* 空状态 */
.empty-state {
  padding: 60px 0;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
