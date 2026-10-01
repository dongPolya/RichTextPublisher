<template>
  <div id="app">
  <template v-if="showHeroSection">
    <!-- 英雄区域 -->
    <HeroSection />

  </template>

    <!-- 主内容区域 -->
    <main class="main-content">
      <div class="container">
       <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <!-- 优先渲染路由组件，如果没有路由匹配则渲染动态组件 -->
          <component :is="showRouterView ? Component : currentTabComponent" />
        </transition>
        </router-view>
      </div>
    </main>
      <!-- 页脚 -->
    <SiteFooter />
  </div>
</template>

<script>
import HeroSection from '@/components/HeroSection.vue'
import Navigation from '@/components/Navigation.vue'
import Communication from '@/views/Communication.vue'
import Community from '@/views/Community.vue'
import Interact from '@/views/Interact.vue'
import User from '@/views/User.vue'
import SiteFooter from '@/components/SiteFooter.vue'

export default {
  name: 'App',
  components: {
    HeroSection,
    SiteFooter,
    Communication,
    Community,
    Interact
  },
  data() {
    return {
      activeTab: 'communication'
    }
  },
  computed: {
    // 判断是否显示路由视图
    showRouterView() {
       const mainTabs = ['Communication',  'Community', 'Quiz']
       return !mainTabs.includes(this.$route.name)
    },
    isUserPage() {
      return this.$route.name === 'User'
    },
    showHeroSection() {
     const mainTabs = ['Communication',  'Community', 'Quiz']
     return mainTabs.includes(this.$route.name)
  },
    currentTabComponent() {
      const componentMap = {
        'communication': Communication,
        'community': Community,
        'quiz': Interact
      }
      return componentMap[this.activeTab]
    }
  },
  methods: {
    // 添加初始化认证检查
    async initializeAuth() {
      try {
        await this.$store.dispatch('checkAuth')
      } catch (error) {
        console.error('Initial auth check failed:', error)
      }
    },
    switchTab(tabId) {
      this.activeTab = tabId
      // 更新URL路由，但只在主选项卡之间导航
      const routeMap = {
        'communication': 'Communication',
        'community': 'Community',
        'quiz': 'Quiz'
      }

      if (routeMap[tabId]) {
        this.$router.push({ name: routeMap[tabId] })
      }
    }
   },
  watch: {
    // 监听路由变化，更新活动标签
    '$route'(to) {
      const routeToTabMap = {
        'Communication': 'communication',
        'Community': 'community',
        'Quiz': 'quiz'
      }

      if (routeToTabMap[to.name]) {
        this.activeTab = routeToTabMap[to.name]
      }
    }
  },
  created() {
   this.initializeAuth()

    // 根据当前路由初始化活动标签
    const routeToTabMap = {
      'Communication': 'communication',
      'Community': 'community',
      'Quiz': 'quiz'
    }

    if (routeToTabMap[this.$route.name]) {
      this.activeTab = routeToTabMap[this.$route.name]
    }
  },

  }


</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Helvetica Neue', Arial, sans-serif;
}
html, body, #app {
  height: auto;
  min-height: 100%;
}

#app {
  display: flex;
  flex-direction: column;
}

body {
  color: #333;
  background-color: #f8f9fa;
  line-height: 1.6;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 主内容区域样式 */
.main-content {
  flex: 1 0 auto;
  padding: 40px 0;
  min-height: 600px;
}

.page-content {
  background: white;
  border-radius: 10px;
  padding: 30px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  margin-top: 20px;
}

.page-title {
  font-size: 2.2rem;
  color: #2c3e50;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e8f4fc;
}

.page-description {
  color: #7f8c8d;
  margin-bottom: 30px;
  font-size: 1.1rem;
}

/* 卡片样式 */
.card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  margin-bottom: 25px;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  font-weight: 600;
  font-size: 1.2rem;
  color: #2c3e50;
}

.card-body {
  padding: 20px;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 0 15px;
  }

  .page-content {
    padding: 20px;
  }

  .page-title {
    font-size: 1.8rem;
  }
}
</style>