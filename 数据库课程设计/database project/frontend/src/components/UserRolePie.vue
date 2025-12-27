<template>
  <div ref="chartRef" style="width: 100%; height: 240px;"></div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: Array // [{name: 'Admin', value: 3}, ...]
})
const chartRef = ref(null)
let chartInstance = null

const renderChart = () => {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  chartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      name: '用户角色分布',
      type: 'pie',
      radius: ['50%', '80%'],
      avoidLabelOverlap: false,
      label: { show: true, position: 'outside', formatter: '{b}: {c} ({d}%)' },
      data: props.data
    }]
  })
}

onMounted(renderChart)
watch(() => props.data, renderChart, { deep: true })
</script>
