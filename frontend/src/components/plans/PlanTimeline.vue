<template>
  <a-timeline>
    <a-timeline-item v-for="(day, index) in itinerary" :key="index">
      <template #dot>
        <CalendarOutlined style="font-size: 16px" />
      </template>
      <h3>第 {{ index + 1 }} 天</h3>
      <a-list :data-source="day.activities" size="small">
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
</template>

<script setup lang="ts">
import { CalendarOutlined } from '@ant-design/icons-vue'

defineProps<{
  itinerary: Array<{
    activities: Array<{
      name: string
      time: string
      description: string
    }>
  }>
}>()
</script>
