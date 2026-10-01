<template>
  <div class="stat-item">
    <div class="stat-number">{{ displayNumber }}</div>
    <div class="stat-label">{{ label }}</div>
  </div>
</template>

<script>
import { useApi } from '@/composables/useApi'
import { ref, onMounted, computed } from 'vue'

export default {
  name: 'StatCounter',
  props: {
    number: {
      type: [String, Number],
      required: true
    },
    label: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const dynamicNumber = ref(null)
    const loading = ref(false)

    // 改动1: 计算显示的数字（优先使用动态获取的值）
    const displayNumber = computed(() => {
      if (dynamicNumber.value !== null) {
        return dynamicNumber.value
      }
      return props.number
    })

    // 改动2: 根据标签类型获取对应的数据
    const fetchDynamicData = async () => {
      loading.value = true

      try {
        const { get } = useApi()

        // 累计出行次数 - 获取日志总数
        if (props.label === '累计出行次数') {
          const logs = await get('/logs')
          dynamicNumber.value = logs.length+2
        }
        // 与你度过 - 计算从2024年4月4日到今天的天数
        else if (props.label === '与你度过') {
          const startDate = new Date('2024-04-04')
          const today = new Date()
          const diffTime = Math.abs(today - startDate)
          const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
          dynamicNumber.value = diffDays
        }
        // 其他情况使用传入的静态数字
        else {
          dynamicNumber.value = props.number
        }
      } catch (error) {
        console.error(`Failed to fetch data for ${props.label}:`, error)
        // 出错时使用传入的静态数字
        dynamicNumber.value = props.number
      } finally {
        loading.value = false
      }
    }

    // 组件挂载时获取数据
    onMounted(() => {
      fetchDynamicData()
    })

    return {
      displayNumber,
      loading
    }
  }
}
</script>

<style scoped>
.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 5px;
  transition: all 0.3s ease;
}

.stat-label {
  font-size: 1.2rem;
  opacity: 0.9;
}

@media (max-width: 992px) {
  .stat-number {
    font-size: 2.5rem;
  }
}

@media (max-width: 768px) {
  .stat-number {
    font-size: 2rem;
  }

  .stat-label {
    font-size: 1rem;
  }
}
</style>
