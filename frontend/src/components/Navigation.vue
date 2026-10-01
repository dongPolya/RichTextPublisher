<template>
  <nav class="navbar">
    <div class="container">
      <div class="nav-container">
        <div
          v-for="(tab, index) in tabs"
          :key="index"
          class="nav-item"
          :class="{ active: activeTab === tab.id }"
          @click="$emit('tab-change', tab.id)"
        >
          {{ tab.name }}
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navigation',
  props: {
    activeTab: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      tabs: [
        { id: 'communication', name: '出行通讯' },
        { id: 'logs', name: '出行日志' },
        { id: 'community', name: '话题讨论' },
        { id: 'quiz', name: '知识竞答' }
      ]
    }
  },
   methods: {
    isDetailPage() {
      // 检查当前是否是详情页
      const detailPages = ['CommunityDetail', 'PostDetail', 'LogDetail']
      return detailPages.includes(this.$route.name)
    },
    handleTabClick(tabId) {
      if (this.isDetailPage()) {
        // 如果在详情页，先返回上一页或主页
        this.$router.push({ name: tabId.charAt(0).toUpperCase() + tabId.slice(1) })
      } else {
        // 正常切换选项卡
        this.$emit('tab-change', tabId)
      }
    }
  }
}
</script>

<style scoped>
.navbar {
  background-color: #2c3e50;
  color: white;
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.nav-container {
  display: flex;
  justify-content: center;
}

.nav-item {
  padding: 20px 30px;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
  font-weight: 500;
  position: relative;
}

.nav-item:hover {
  background-color: #34495e;
}

.nav-item.active {
  background-color: #1abc9c;
  color: white;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  height: 4px;
  background-color: white;
  border-radius: 2px 2px 0 0;
}

@media (max-width: 768px) {
  .nav-container {
    flex-wrap: wrap;
  }

  .nav-item {
    padding: 15px;
    flex: 1;
    text-align: center;
    min-width: 120px;
  }
}

@media (max-width: 576px) {
  .nav-container {
    overflow-x: auto;
    justify-content: flex-start;
    padding: 0 10px;
  }

  .nav-item {
    min-width: 110px;
  }
}
</style>