<template>
  <a-card title="旅行统计">
    <div ref="chartRef" style="width: 100%; height: 400px"></div>
  </a-card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  stats: {
    plans_count: number
    posts_count: number
    followers_count: number
    following_count: number
    likes_received: number
  }
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value)
    updateChart()
  }
})

watch(() => props.stats, updateChart, { deep: true })

function updateChart() {
  if (!chart) return

  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: '统计数据',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: props.stats.plans_count, name: '旅行计划' },
          { value: props.stats.posts_count, name: '帖子' },
          { value: props.stats.followers_count, name: '粉丝' },
          { value: props.stats.following_count, name: '关注' },
          { value: props.stats.likes_received, name: '获赞' }
        ]
      }
    ]
  }

  chart.setOption(option)
}
</script>
