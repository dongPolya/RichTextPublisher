<template>
  <div class="user-center">
    <div class="container">
      <!-- 页面头部 -->
      <header>
        <div class="logo">
          <font-awesome-icon icon="fa-solid fa-compass" />
          <span>Ta的小窝</span>
        </div>
        <div class="user-actions">
          <button class="btn btn-outline">
           <font-awesome-icon icon="fa-solid fa-bell" />
          </button>
          <button class="btn btn-primary">
           <font-awesome-icon icon="fa-solid fa-plus" />
            <span>创建内容</span>
          </button>
        </div>
      </header>

      <!-- 主要内容区域 -->
      <div class="main-content">
        <!-- 用户信息卡片 -->
        <div class="user-card">
          <div class="user-header">
            <img :src="user.avatar" :alt="user.username" class="avatar">
            <div class="user-info">
              <h1 v-if="!isEditing" @click="startEdit">{{ user.username }}</h1>
              <input
                v-else
                v-model="editForm.username"
                class="editable-input username-input"
                placeholder="用户名"
              />
              <div class="user-title" v-if="!isEditing" @click="startEdit">
                <font-awesome-icon icon="fa-solid fa-crown" />
                <span>{{ user.title || '旅行爱好者' }}</span>
              </div>
               <div class="user-title editable-field" v-else @click="startEdit">
                <font-awesome-icon icon="fa-solid fa-crown" />
                <input
                  v-model="editForm.title"
                  class="editable-input"
                  placeholder="头衔"
                />
              </div>
              <p class="user-bio" v-if="!isEditing" @click="startEdit">{{ user.bio || '热爱探索未知的世界，记录旅途中的每一刻精彩' }}</p>
               <textarea
                v-else
                v-model="editForm.bio"
                class="editable-textarea"
                placeholder="个人简介"
                rows="3"
              ></textarea>
            </div>
          </div>

          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">{{ user.score || 1258 }}</div>
              <div class="stat-label">积分</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ posts.length }}</div>
              <div class="stat-label">帖子</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ user.followers || 24 }}</div>
              <div class="stat-label">粉丝</div>
            </div>
          </div>

          <div class="tags">
            <div class="tag" v-for="tag in user.tags" :key="tag">{{ tag }}</div>
          </div>

          <div class="user-actions-card">
            <button  v-if="!isEditing"
              class="btn btn-primary"
              @click="startEdit"
            >
              <font-awesome-icon icon="fa-solid fa-edit" />
              <span>编辑资料</span>
            </button>
             <button
              v-else
              class="btn btn-success"
              @click="saveProfile"
              :disabled="saving"
            >
              <font-awesome-icon icon="fa-solid fa-save" />
              <span>{{ saving ? '保存中...' : '保存' }}</span>
            </button>

            <button
              v-if="isEditing"
              class="btn btn-outline"
              @click="cancelEdit"
            >
              <font-awesome-icon icon="fa-solid fa-times" />
              <span>取消</span>
            </button>
            <button  v-else
              class="btn btn-outline"
              @click="shareProfile"
            >
               <font-awesome-icon icon="fa-solid fa-share-alt" />
              <span>分享资料</span>
            </button>
          </div>
        </div>

        <!-- 内容区域 -->
        <div class="content-column">
          <!-- 我的社区 -->
          <div class="content-section">
            <div class="section-header">
              <h2 class="section-title">
                <font-awesome-icon icon="fa-solid fa-users" />
                <span>我的社区</span>
              </h2>
              <a href="#" class="view-all">查看全部</a>
            </div>

            <div class="communities-grid">
               <div v-if="communities.length === 0" class="empty-state">
                <div class="community-card empty-card">
                  <div class="community-icon" style="background-color: #ccc;">
                    <font-awesome-icon icon="fa-solid fa-plus" />
                  </div>
                  <div class="community-name">暂无社区</div>
                  <div class="community-members">加入社区开始探索吧</div>
                </div>
              </div>

              <!-- 改动2: 正常显示社区列表 -->
              <div
                class="community-card"
                v-for="community in communities"
                :key="community.id"
                @click="goToCommunity(community.id)"
              >
                <div class="community-icon" :style="{ backgroundColor: getRandomColor() }">
                  <font-awesome-icon :icon="getCommunityIcon(community.category)" />
                </div>
                <div class="community-name">{{ community.name }}</div>
                <div class="community-members">{{ community.member_count }} 成员</div>
              </div>
            </div>
          </div>

          <!-- 我的帖子 -->
          <div class="content-section">
            <div class="section-header">
              <h2 class="section-title">
                <font-awesome-icon icon="fa-solid fa-file-alt" />
                <span>我的帖子</span>
              </h2>
              <router-link to="/communication" class="view-all">查看全部</router-link>
            </div>

            <div class="posts-list">
              <div
                class="post-item"
                v-for="post in posts.slice(0, 3)"
                :key="post.id"
                @click="goToPost(post.id)"
              >
                <img :src="post.image" :alt="post.title" class="post-image">
                <div class="post-content">
                  <h3 class="post-title">{{ post.title }}</h3>
                  <div class="post-meta">
                    <span>{{ formatDate(post.created_at) }}</span>
                    <span>{{ post.sub }}</span>
                  </div>
                  <p class="post-excerpt">{{ post.content.substring(0, 100) }}...</p>
                  <div class="post-stats">
                    <div class="stat">
                      <i class="far fa-eye"></i>
                      <span>{{ post.views || 0 }}</span>
                    </div>
                    <div class="stat">
                      <i class="far fa-comment"></i>
                      <span>{{ post.comments_count || 0 }}</span>
                    </div>
                    <div class="stat">
                      <i class="far fa-heart"></i>
                      <span>{{ post.likes }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 出行日志 -->
          <div class="content-section">
            <div class="section-header">
              <h2 class="section-title">
                <i class="fas fa-road"></i>
                <span>出行日志</span>
              </h2>
              <router-link to="/logs" class="view-all">查看全部</router-link>
            </div>

            <div class="travel-logs">
              <div
                class="travel-item"
                v-for="log in logs.slice(0, 2)"
                :key="log.id"
                @click="goToLog(log.id)"
              >
                <img :src="log.image || 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80'"
                     :alt="log.title" class="travel-image">
                <div class="travel-content">
                  <h3 class="travel-title">{{ log.title }}</h3>
                  <div class="travel-meta">
                    <span>{{ formatDate(log.created_at) }}</span>
                    <span>{{ log.destination }}</span>
                  </div>
                  <p class="travel-excerpt">{{ log.description || log.content.substring(0, 100) }}...</p>
                  <div class="travel-stats">
                    <div class="stat">
                      <i class="far fa-calendar"></i>
                      <span>{{ log.duration || '7天' }}</span>
                    </div>
                    <div class="stat">
                      <i class="fas fa-map-marker-alt"></i>
                      <span>{{ log.destination }}</span>
                    </div>
                    <div class="stat">
                      <i class="far fa-heart"></i>
                      <span>{{ log.likes || 0 }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'User',
  data() {
    return {
      userId: null,
       isEditing: false, // 改动5: 编辑状态
      saving: false, // 改动6: 保存状态
      editForm: { // 改动7: 编辑表单数据
        username: '',
        title: '',
        bio: ''
      }
    }
  },
  computed: {
    ...mapState(['user', 'communities', 'posts', 'logs'])
  },
  methods: {
    ...mapActions(['fetchUser', 'fetchUserPosts', 'fetchUserLogs', 'fetchUserCommunities','updateUserProfile']),

    // 初始化页面数据
    async initData() {
      this.userId = this.$route.params.id || 1 // 默认用户ID为1

      try {
        await Promise.all([
          this.fetchUser(this.userId),
          this.fetchUserPosts(this.userId),
          this.fetchUserLogs(this.userId),
          this.fetchUserCommunities(this.userId)
        ])
      } catch (error) {
        console.error('Failed to load user data:', error)
      }
    },

    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
    },

    // 获取社区图标
    getCommunityIcon(category) {
      const icons = {
        '户外运动': 'fas fa-mountain',
        '摄影': 'fas fa-camera',
        '美食': 'fas fa-utensils',
        '自驾游': 'fas fa-car',
        '文化': 'fas fa-landmark',
        '电子音乐': 'fas fa-music'
      }
      return icons[category] || 'fas fa-users'
    },

    // 生成随机颜色
    getRandomColor() {
      const colors = ['#6c5ce7', '#fd79a8', '#00b894', '#fdcb6e', '#0984e3', '#e17055']
      return colors[Math.floor(Math.random() * colors.length)]
    },

    // 导航到社区详情
    goToCommunity(communityId) {
      this.$router.push(`/community/${communityId}`)
    },

    // 导航到帖子详情
    goToPost(postId) {
      this.$router.push(`/post/${postId}`)
    },

    // 导航到日志详情
    goToLog(logId) {
      this.$router.push(`/log/${logId}`)
    },

     startEdit() {
      this.isEditing = true
      // 初始化编辑表单
      this.editForm = {
        username: this.user.username || '',
        title: this.user.title || '',
        bio: this.user.bio || ''
      }
    },

    // 改动9: 取消编辑
    cancelEdit() {
      this.isEditing = false
      this.editForm = {
        username: '',
        title: '',
        bio: ''
      }
    },

    // 改动10: 保存资料
    async saveProfile() {
      // 验证输入
      if (!this.editForm.username.trim()) {
        alert('用户名不能为空')
        return
      }

      this.saving = true

      try {
        // 调用 Vuex action 更新用户信息
         await this.updateUserProfile({
          userId: this.userId,
          userData: this.editForm
        })

        // 更新本地显示
        this.isEditing = false

        alert('资料保存成功！')
      } catch (error) {
        console.error('Failed to update profile:', error)
        alert('保存失败，请重试')
      } finally {
        this.saving = false
      }
    },

    // 分享资料
    shareProfile() {
      const url = window.location.href
      navigator.clipboard.writeText(url).then(() => {
        alert('链接已复制到剪贴板！')
      }).catch(err => {
        console.error('复制失败:', err)
        prompt('请手动复制链接：', url)
      })
     }
    },
  mounted() {
    this.initData()
  },
  watch: {
    '$route.params.id': {
      handler(newId) {
        if (newId) {
          this.initData()
        }
      },
      immediate: true
    }
  }
}
</script>

<style scoped>
/* 保持原有的所有CSS样式，这里只列出关键部分 */
:root {
  --primary: #6c5ce7;
  --secondary: #a29bfe;
  --accent: #fd79a8;
  --light: #f8f9fa;
  --dark: #2d3436;
  --gray: #636e72;
  --success: #00b894;
  --warning: #fdcb6e;
  --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  --transition: all 0.3s ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.user-center {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
  padding: 0;
}

#app .user-center {
  margin: 0;
  padding: 20px 0;
}

/* 隐藏App.vue中的HeroSection和Navigation */
.user-center ~ * {
  display: none !important;
}
body {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
  color: var(--dark);
  line-height: 1.6;
  min-height: 100vh;
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  margin-bottom: 30px;
}

.logo {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
  display: flex;
  align-items: center;
}

.logo i {
  margin-right: 10px;
  font-size: 32px;
}



.user-actions {
  display: flex;
  gap: 15px;
}

.btn {
  padding: 10px 20px;
  border-radius: 50px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: var(--primary);
  color: var(--primary);
}

.btn-primary:hover {
  background: #f8c9124f;;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3);
}

.btn-outline {
  background: transparent;
  color: var(--primary);
  border: 2px solid var(--primary);
}

.btn-outline:hover {
 background: #3de54c4f;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3);
}
.btn-success {
  background: var(--success);
 color: var(--primary);
}

.btn-success:hover:not(:disabled) {
  background: #00a383;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 184, 148, 0.3);
}

.btn-success:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
}

.user-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: var(--card-shadow);
  position: relative;
  overflow: hidden;
}

.user-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 8px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
}

.user-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 5px solid white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  margin-right: 20px;
}

.user-info h1 {
  font-size: 24px;
  margin-bottom: 5px;
}

.user-title {
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.user-bio {
  color: var(--gray);
  font-size: 15px;
  margin-bottom: 15px;
}
/* 改动12: 可编辑字段的悬停提示 */
.user-info h1:hover,
.user-title:hover,
.user-bio:hover {
  cursor: pointer;
  opacity: 0.8;
  transition: var(--transition);
}

/* 改动13: 编辑状态下的输入框样式 */
.editable-input {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid var(--primary);
  border-radius: 8px;
  font-size: inherit;
  font-family: inherit;
  background: white;
  transition: var(--transition);
  outline: none;
}

.editable-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.username-input {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 5px;
}

.editable-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid var(--primary);
  border-radius: 8px;
  font-size: 15px;
  font-family: inherit;
  background: white;
  resize: vertical;
  min-height: 80px;
  transition: var(--transition);
  outline: none;
  color: var(--gray);
}

.editable-textarea:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
}

.editable-field {
  display: flex;
  align-items: center;
  gap: 5px;
}

.editable-field input {
  flex: 1;
}

.user-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
}

.stat-label {
  font-size: 14px;
  color: var(--gray);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 25px;
}

.tag {
  background: rgba(108, 92, 231, 0.1);
  color: var(--primary);
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 500;
}

.user-actions-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-actions-card .btn {
  width: 100%;
  justify-content: center;
}

.content-section {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: var(--card-shadow);
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--dark);
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-title i {
  color: var(--primary);
}

.view-all {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: var(--transition);
}

.view-all:hover {
  text-decoration: underline;
}

.communities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.community-card {
  background: var(--light);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  transition: var(--transition);
  cursor: pointer;
}

.community-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.community-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: white;
  font-size: 24px;
}

.community-name {
  font-weight: 600;
  margin-bottom: 5px;
}

.community-members {
  font-size: 14px;
  color: var(--gray);
}
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.empty-card {
  background: #f8f9fa;
  border: 2px dashed #ddd;
  cursor: default;
}

.empty-card:hover {
  transform: none;
  box-shadow: none;
}


.posts-list, .travel-logs {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-item, .travel-item {
  display: flex;
  gap: 15px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: var(--transition);
}

.post-item:hover, .travel-item:hover {
  transform: translateX(5px);
}

.post-item:last-child, .travel-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.post-image, .travel-image {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  object-fit: cover;
  flex-shrink: 0;
}

.post-content, .travel-content {
  flex: 1;
}

.post-title, .travel-title {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 16px;
}

.post-meta, .travel-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: var(--gray);
  margin-bottom: 8px;
}

.post-excerpt, .travel-excerpt {
  font-size: 14px;
  color: var(--gray);
  line-height: 1.5;
}

.post-stats, .travel-stats {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: var(--gray);
}

@media (max-width: 992px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .communities-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}

@media (max-width: 768px) {
  header {
    flex-direction: column;
    gap: 20px;
  }

  .nav-links {
    order: 3;
    width: 100%;
    justify-content: center;
  }

  .user-header {
    flex-direction: column;
    text-align: center;
  }

  .avatar {
    margin-right: 0;
    margin-bottom: 15px;
  }

  .user-stats {
    justify-content: center;
  }

  .communities-grid {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  }

  .post-item, .travel-item {
    flex-direction: column;
  }

  .post-image, .travel-image {
    width: 100%;
    height: 150px;
  }
}
</style>