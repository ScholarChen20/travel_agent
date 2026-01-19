<template>
  <a-card hoverable @click="$emit('click', plan.id)">
    <template #cover>
      <div class="plan-cover">
        {{ plan.destination }}
      </div>
    </template>
    <template #actions>
      <HeartOutlined v-if="!plan.is_favorite" @click.stop="$emit('toggleFavorite', plan.id)" />
      <HeartFilled v-else style="color: #ff4d4f" @click.stop="$emit('toggleFavorite', plan.id)" />
      <ExportOutlined @click.stop="$emit('export', plan.id)" />
      <DeleteOutlined @click.stop="$emit('delete', plan.id)" />
    </template>
    <a-card-meta :title="plan.title">
      <template #description>
        <div>{{ plan.start_date }} 至 {{ plan.end_date }}</div>
        <div v-if="plan.budget">预算: ¥{{ plan.budget }}</div>
      </template>
    </a-card-meta>
  </a-card>
</template>

<script setup lang="ts">
import { HeartOutlined, HeartFilled, ExportOutlined, DeleteOutlined } from '@ant-design/icons-vue'

defineProps<{
  plan: {
    id: string
    title: string
    destination: string
    start_date: string
    end_date: string
    budget?: number
    is_favorite: boolean
  }
}>()

defineEmits<{
  click: [planId: string]
  toggleFavorite: [planId: string]
  export: [planId: string]
  delete: [planId: string]
}>()
</script>

<style scoped>
.plan-cover {
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
}
</style>
