<template>
  <div class="page-content">
    <div class="page-header">
      <h2 class="page-title">话题社区</h2>
      <p class="page-description">加入感兴趣的热议话题，畅所欲言...</p>
      <button class="create-btn" @click="showCreateModal = true">
        <i class="fas fa-plus"></i> 新建社区
      </button>
    </div>

    <div class="community-grid">
      <div v-for="(community, index) in communities" :key="index" class="card user-card">
        <div class="user-avatar">
          <img :src="community.avatar" :alt="community.name">
        </div>
        <h3 class="user-name">{{ community.name }}</h3>
        <div class="user-location">
          <font-awesome-icon icon="far fa-tag"/> {{ community.category }}
        </div>

        <div class="user-stats">
          <div class="user-stat">
            <div class="user-stat-number">{{ community.member_count }}</div>
            <div class="user-stat-label">成员</div>
          </div>
          <div class="user-stat">
            <div class="user-stat-number">{{ community.post_count }}</div>
            <div class="user-stat-label">内容</div>
          </div>
          <div class="user-stat">
            <div class="user-stat-number">{{ community.activity_score }}%</div>
            <div class="user-stat-label">活跃</div>
          </div>
        </div>

        <button class="join-button" @click="joinCommunityAction(community.id)">
          <font-awesome-icon icon="far fa-plus"/> 加入
        </button>
      </div>
    </div>

    <CreateModal
      :visible="showCreateModal"
      title="新建社区"
      @close="showCreateModal = false"
      @submit="createCommunity"
    >
      <form class="create-form">
        <div class="form-group">
          <label for="communityName">社区名称</label>
          <input type="text" id="communityName" v-model="newCommunity.name" required>
        </div>
        <div class="form-group">
          <label for="communityCategory">分类</label>
          <input type="text" id="communityCategory" v-model="newCommunity.category" required>
        </div>
        <div class="form-group">
          <label for="communityDescription">描述</label>
          <textarea id="communityDescription" v-model="newCommunity.description" rows="3"></textarea>
        </div>
        <div class="form-group">
          <label for="communityAvatar">头像URL</label>
          <input type="url" id="communityAvatar" v-model="newCommunity.avatar">
        </div>
      </form>
    </CreateModal>
  </div>
</template>

<script>
import { mapState, mapActions,mapGetters } from 'vuex'
import CreateModal from '@/components/CreateModal.vue'

export default {
  name: 'Community',
  components: {
    CreateModal
  },
  data() {
    return {
      showCreateModal: false,
      newCommunity: {
        name: '',
        category: '',
        description: '',
        avatar: '',
        member_count: 0,
        post_count: 0,
        activity_score: 0
      }
    }
  },
  computed: {
    ...mapState(['communities']),
    ...mapGetters(['currentUser', 'isAuthenticated'])
  },
  async created() {
    await this.fetchCommunities()
    await this.$store.dispatch('checkAuth')
  },
  methods: {
    ...mapActions(['fetchCommunities', 'createCommunity', 'joinCommunity']),
    async createCommunity() {
      try {
        await this.$store.dispatch('createCommunity', this.newCommunity)
        this.showCreateModal = false
        this.newCommunity = {
          name: '',
          category: '',
          description: '',
          avatar: '',
          member_count: 0,
          post_count: 0,
          activity_score: 0
        }
      } catch (error) {
        console.error('Failed to create community:', error)
        alert('创建失败，请重试')
      }
    },
     async joinCommunityAction(communityId) {
      // 检查用户是否登录
      if (!this.isAuthenticated || !this.currentUser) {
        alert('请先登录后再加入社区')
        this.$router.push('/login')
        return
      }

      try {
        await this.joinCommunity({
          communityId: communityId,
          userId: this.currentUser.id
        })
        this.$router.push({ name: 'CommunityDetail', params: { id: communityId } })
        alert('加入社区成功！')
      } catch (error) {
        console.error('Failed to join community:', error)
        alert('加入失败，请重试')
      }
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 30px;
}

.create-btn {
  align-self: flex-end;
  background-color: #1abc9c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
  margin-top: 10px;
}

.create-btn:hover {
  background-color: #16a085;
}

.community-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.user-card {
  text-align: center;
  padding: 20px;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 15px;
  border: 4px solid #e8f4fc;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.user-location {
  color: #7f8c8d;
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.user-stats {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 15px;
}

.user-stat {
  text-align: center;
}

.user-stat-number {
  font-weight: 600;
  color: #1abc9c;
}

.user-stat-label {
  font-size: 0.8rem;
  color: #95a5a6;
}

.join-button {
  background-color: #1abc9c;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background-color 0.3s;
}

.join-button:hover {
  background-color: #16a085;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 5px;
  color: #2c3e50;
}

.form-group input,
.form-group textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1abc9c;
}
</style>