<template>
  <div class="page-content">
    <div class="community-header">
      <div class="community-info">
        <img :src="community.avatar" :alt="community.name" class="community-avatar">
        <div>
          <h2 class="community-name">{{ community.name }}</h2>
          <p class="community-category">{{ community.category }}</p>
          <p class="community-description">{{ community.description }}</p>
          <div class="community-stats">
            <span>{{ community.member_count }} 成员</span>
            <span>{{ community.post_count }} 内容</span>
            <span>{{ community.activity_score }}% 活跃度</span>
          </div>
        </div>
      </div>
      <button class="create-btn" @click="showCreateModal = true">
        <font-awesome-icon :icon="['fas', 'plus']" /> 新建帖子
      </button>
    </div>

    <div class="posts-container">
      <div v-for="post in posts" :key="post.id" class="post-card" @click="goToPostDetail(post.id)">
        <div class="post-header">
          <img :src="post.author.avatar" :alt="post.author.username" class="post-author-avatar">
          <div>
            <div class="post-author-name">{{ post.author.username }}</div>
            <div class="post-date">{{ formatDate(post.created_at) }}</div>
          </div>
        </div>
        <h3 class="post-title">{{ post.title }}</h3>
        <div class="post-content-preview" v-html="truncateContent(post.content)"></div>
        <div class="post-footer">
          <span class="post-likes">
            <font-awesome-icon :icon="['fas', 'heart']" /> {{ post.likes }}
          </span>
          <span class="post-comments">
            <font-awesome-icon :icon="['fas', 'comment']" /> {{ post.comments_count || 0 }}
          </span>
        </div>
      </div>
    </div>

    <CreateModal
      :visible="showCreateModal"
      title="新建帖子"
      @close="showCreateModal = false"
      @submit="createPost"
    >
      <form class="create-form">
        <div class="form-group">
          <label for="postTitle">标题</label>
          <input type="text" id="postTitle" v-model="newPost.title" required>
        </div>
        <div class="form-group">
          <label for="postCategory">帖子分类</label>
          <select id="postCategory" v-model="newPost.sub" required>
            <option value="common">常规</option>
            <option value="blog">出行记录</option>
            <option value="communication">公交之窗</option>
            <option value="chat">话题讨论</option>
            <option value="data">数据汇总</option>
          </select>
        </div>
        <div class="form-group">
          <label for="postContent">内容</label>
          <Editor
            id="postContent"
            v-model="newPost.content"
            api-key="ct6il0doy91ptb1u7t6r7z9xuawi1lpl44ukf19fgs18rkk0"
            :init="{
              height: 300,
              menubar: false,
              license_key: 'gpl',
              plugins: [
               'accordion',
                'advlist',
                'anchor',
                'autolink',
                'autoresize',
                'autosave',
                'charmap',
                'code',
                'codesample',
                'directionality',
                'emoticons',
                'fullscreen',
                'help',
                'image',
                'importcss',
                'insertdatetime',
                'link',
                'lists',
                'media',
                'nonbreaking',
                'pagebreak',
                'preview',
                'quickbars',
                'save',
                'searchreplace',
                'table',
                'visualblocks',
                'visualchars',
                'wordcount'
              ],
              toolbar: 'undo redo | blocks | formatselect | emoticons | bold italic forecolor backcolor | alignleft aligncenter alignright | bullist numlist outdent indent | link image media | table | code preview | fullscreen',
              language: 'zh_CN',

              fontsize_formats: '8px 10px 12px 14px 16px 18px 24px 36px 48px',
              block_formats: '段落=p;标题 1=h1;标题 2=h2;标题 3=h3;标题 4=h4;标题 5=h5;标题 6=h6;预格式化=pre'
            }"
          />
        </div>
         <div class="form-group">
          <label for="postMode">发布设置</label>
          <select id="postMode" v-model="newPost.mode" required>
            <option value="普通">普通</option>
            <option value="首页">首页</option>
            <option value="置顶">置顶</option>
            <option value="数据">数据资源</option>
          </select>
        </div>
      </form>
    </CreateModal>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { useApi } from '@/composables/useApi'
import CreateModal from '@/components/CreateModal.vue'
import Editor from '@tinymce/tinymce-vue'

export default {
  name: 'CommunityDetail',
  components: {
    CreateModal,
    Editor
  },
  data() {
    return {
      community: {},
      posts: [],
      showCreateModal: false,
      newPost: {
        title: '',
        content: '',
        sub: 'common',
        mode: '普通',
        user_id: null,
        community_id: null
      }
    }
  },
   computed: {
    ...mapGetters(['currentUser', 'isAuthenticated'])
  },
  async created() {
    const communityId = this.$route.params.id
    this.newPost.community_id = parseInt(communityId)
     // 检查用户是否已登录
    await this.$store.dispatch('checkAuth')
     if (this.isAuthenticated && this.currentUser) {
        this.newPost.user_id = this.currentUser.id
     } else {
     console.warn('用户未登录，无法创建帖子')
     this.$router.push('/login')
  }
    await this.fetchCommunityDetail(communityId)
    await this.fetchCommunityPosts(communityId)
  },
  methods: {
    ...mapActions(['createPost']),
    async fetchCommunityDetail(communityId) {
      this.loading = true
      this.error = null

      try {
        const { get } = useApi()
        this.community = await get(`/communities/${communityId}`)
      } catch (err) {
        console.error('Failed to fetch community detail:', err)
        this.error = '获取社区详情失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    sortPosts(posts) {
      if (!posts || posts.length === 0) return posts

      return [...posts].sort((a, b) => {
        // 置顶帖子优先
        const aIsPinned = a.mode === '置顶' ? 1 : 0
        const bIsPinned = b.mode === '置顶' ? 1 : 0

        if (aIsPinned !== bIsPinned) {
          return bIsPinned - aIsPinned // 置顶的在前
        }

        // 同级别按时间倒序（新的在前）
        return new Date(b.created_at) - new Date(a.created_at)
      })
    },
    async fetchCommunityPosts(communityId) {
       this.loading = true
      this.error = null

      try {
        const { get } = useApi()
        this.posts = await get(`/communities/${communityId}/posts`)
      } catch (err) {
        console.error('Failed to fetch community posts:', err)
        this.error = '获取社区帖子失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    truncateContent(content) {
      // 移除HTML标签并截取内容
      const plainText = content.replace(/<[^>]*>/g, '')
      return plainText.length > 100 ? plainText.substring(0, 100) + '...' : plainText
    },
    goToPostDetail(postId) {
      this.$router.push({ name: 'PostDetail', params: { id: postId } })
    },
    async createPost() {
      // 再次检查用户登录状态
  if (!this.isAuthenticated || !this.currentUser) {
    alert('请先登录后再创建帖子')
    this.$router.push('/login')
    return
  }

  // 确保user_id正确设置
  this.newPost.user_id = this.currentUser.id
      try {
        await this.$store.dispatch('createPost', this.newPost)
        this.showCreateModal = false
        this.newPost = {
          title: '',
          content: '',
          sub: 'common',
          mode: '普通',
          user_id: this.currentUser.id,
          community_id: this.$route.params.id
        }
        // 重新加载帖子列表
        await this.fetchCommunityPosts(this.$route.params.id)
      } catch (error) {
        console.error('Failed to create post:', error)
        alert('创建失败，请重试')
      }
    }
  }
}
</script>

<style scoped>
.community-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.community-info {
  display: flex;
  gap: 20px;
}

.community-avatar {
  width: 100px;
  height: 100px;
  border-radius: 10px;
  object-fit: cover;
}

.community-name {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 5px;
}

.community-category {
  color: #1abc9c;
  font-weight: 600;
  margin-bottom: 10px;
}

.community-description {
  color: #7f8c8d;
  margin-bottom: 15px;
}

.community-stats {
  display: flex;
  gap: 15px;
  color: #95a5a6;
}

.posts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.post-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.post-author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}

.post-author-name {
  font-weight: 600;
  color: #2c3e50;
}

.post-date {
  color: #95a5a6;
  font-size: 0.9rem;
}

.post-title {
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.post-content-preview {
  color: #7f8c8d;
  margin-bottom: 15px;
  line-height: 1.5;
}

.post-footer {
  display: flex;
  gap: 15px;
  color: #95a5a6;
}

.post-likes, .post-comments {
  display: flex;
  align-items: center;
  gap: 5px;
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
.form-group select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #1abc9c;
}
</style>