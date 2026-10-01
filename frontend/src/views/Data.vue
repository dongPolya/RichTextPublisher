<template>
  <div class="page-content">
    <div class="page-header">
      <h2 class="page-title">数据资源</h2>
      <p class="page-description">探索网站提供的各类数据资源文章</p>
    </div>

    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i> 加载中...
    </div>

    <div v-else-if="dataPosts.length === 0" class="empty-state">
      <i class="fas fa-database"></i>
      <p>暂无数据资源文章</p>
    </div>

    <div v-else class="data-grid">
      <div
        v-for="(post, index) in dataPosts"
        :key="index"
        class="data-card"
        @click="goToPost(post.id)"
      >
        <div class="data-card-image">
          <img :src="post.image || defaultImage" :alt="post.title">
        </div>
        <div class="data-card-content">
          <h3 class="data-card-title">{{ post.title }}</h3>
          <p class="data-card-text">{{ truncateContent(post.content) }}</p>
          <div class="data-card-meta">
            <span class="data-card-author">
              <img :src="post.author?.avatar || defaultAvatar" :alt="post.author?.username">
              {{ post.author?.username || '匿名用户' }}
            </span>
            <span class="data-card-date">
              <i class="fas fa-calendar"></i>
              {{ formatDate(post.created_at) }}
            </span>
          </div>
          <div class="data-card-stats">
            <span class="data-stat">
              <i class="fas fa-heart"></i>
              {{ post.likes || 0 }}
            </span>
            <span class="data-stat">
              <i class="fas fa-comment"></i>
              {{ post.comments_count || 0 }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ref, computed, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'

export default {
  name: 'Data',
  setup() {
    const store = useStore()
    const router = useRouter()
    const { get } = useApi()

    const loading = ref(true)
    const dataPosts = ref([])

    const defaultImage = 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1170&q=80'
    const defaultAvatar = 'https://randomuser.me/api/portraits/men/1.jpg'

    const fetchDataPosts = async () => {
      try {
        loading.value = true
        const posts = await get('/posts?mode=数据')
        dataPosts.value = Array.isArray(posts) ? posts : []
      } catch (error) {
        console.error('Failed to fetch data posts:', error)
        dataPosts.value = []
      } finally {
        loading.value = false
      }
    }

    const truncateContent = (content) => {
      if (!content) return ''
      return content.length > 100 ? content.substring(0, 100) + '...' : content
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const goToPost = (postId) => {
      router.push(`/post/${postId}`)
    }

    onMounted(() => {
      fetchDataPosts()
    })

    return {
      loading,
      dataPosts,
      defaultImage,
      defaultAvatar,
      truncateContent,
      formatDate,
      goToPost
    }
  }
}
</script>

<style scoped>
.page-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.page-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 30px;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-description {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
  font-size: 1.1rem;
}

.loading i {
  margin-right: 10px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-state i {
  font-size: 4rem;
  margin-bottom: 20px;
  color: #bdc3c7;
}

.empty-state p {
  font-size: 1.2rem;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

.data-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
}

.data-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.data-card-image {
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.data-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.data-card:hover .data-card-image img {
  transform: scale(1.05);
}

.data-card-content {
  padding: 20px;
}

.data-card-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  line-height: 1.4;
}

.data-card-text {
  color: #7f8c8d;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 15px;
}

.data-card-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.data-card-author {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #555;
  font-size: 0.9rem;
}

.data-card-author img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.data-card-date {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #95a5a6;
  font-size: 0.85rem;
}

.data-card-stats {
  display: flex;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid #ecf0f1;
}

.data-stat {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.data-stat i {
  color: #1abc9c;
}

@media (max-width: 768px) {
  .page-content {
    padding: 20px 15px;
  }

  .page-title {
    font-size: 1.6rem;
  }

  .data-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}
</style>