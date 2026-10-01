<template>
  <div class="page-content">
    <div class="page-header">
      <h2 class="page-title">出行动态</h2>
      <p class="page-description">查看最近的旅行团队和活动，与团队成员保持联系</p>
      <button class="create-btn" @click="showCreateModal = true">
        <i class="fas fa-plus"></i> 投稿
      </button>
    </div>

    <div class="blog-posts">
      <div v-for="(post, index) in posts" :key="index" class="card blog-post" @click="goToPostDetail(post.id)">
        <div class="card-body">
          <div class="blog-header">
            <div class="blog-avatar">
              <img :src="post.author.avatar" :alt="post.author.username">
            </div>
            <div>
              <div class="blog-author">{{ post.author.username }}</div>
              <div class="blog-date">{{ formatDate(post.created_at) }}</div>
            </div>
          </div>

          <h3>{{ post.title }}</h3>
          <p>{{ post.content }}</p>

          <img v-if="post.image" :src="post.image" class="blog-image" alt="Blog image">

          <div class="blog-actions">
            <div class="blog-action">
              <font-awesome-icon icon="far fa-heart"/><{{ post.likes }}
            </div>
            <div class="blog-action">
              <font-awesome-icon icon="far fa-comment"/> {{ post.comments_count }}
            </div>
            <div class="blog-action">
              <font-awesome-icon icon="far fa-bookmark"/>  收藏
            </div>
          </div>
        </div>
      </div>
    </div>

    <CreateModal
      :visible="showCreateModal"
      title="新建出行通讯"
      @close="showCreateModal = false"
      @submit="createPost"
    >
      <form class="create-form">
        <div class="form-group">
          <label for="postTitle">标题</label>
          <input type="text" id="postTitle" v-model="newPost.title" required>
        </div>
        <div class="form-group">
          <label for="postContent">内容</label>
          <textarea id="postContent" v-model="newPost.content" rows="5" required></textarea>
        </div>
          <div class="form-group">
          <label for="postImage">图片URL (可选)</label>
          <input type="url" id="postImage" v-model="newPost.image">
        </div>
        <div class="form-group">
          <label for="postImage">上传图片 (可选)</label>
          <!-- 修改这里：将type="url"改为type="file"并添加change事件处理 -->
          <input type="file" id="postImage" ref="fileInput" @change="handleFileSelect" accept="image/*">
          <div v-if="selectedFile" class="file-info">
            已选择: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
          </div>

          <div v-if="imagePreview" class="preview-container">
            <img :src="imagePreview" class="image-preview" alt="预览图">
          </div>
        </div>
      </form>
    </CreateModal>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters  } from 'vuex'
import CreateModal from '@/components/CreateModal.vue'

export default {
  name: 'Communication',
  components: {
    CreateModal
  },
  data() {
    return {
      showCreateModal: false,
      selectedFile: null, // 新增：存储选中的文件
      imagePreview: null, // 新增：存储图片预览
      newPost: {
        title: '',
        content: '',
        image: '',
        sub: 'communication',
        mode: '首页',
        user_id: null
      }
    }
  },
  computed: {
    ...mapState(['posts']),
    ...mapGetters(['currentUser', 'isAuthenticated'])
  },
  async created() {
    await this.fetchPosts('communication'),
    // 检查用户是否已登录
    await this.$store.dispatch('checkAuth')
     if (this.isAuthenticated && this.currentUser) {
        this.newPost.user_id = this.currentUser.id
     } else {
     console.warn('用户未登录，无法创建帖子')
     this.$router.push('/login')
  }
  },
  methods: {
    ...mapActions(['fetchPosts', 'createPost']),
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
     // 新增：处理文件选择
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        // 检查文件类型和大小
        if (!file.type.match('image.*')) {
          alert('请选择图像文件');
          return;
        }

        if (file.size > 5 * 1024 * 1024) { // 5MB限制
          alert('文件大小不能超过5MB');
          return;
        }

        this.selectedFile = file;

        // 创建预览
        const reader = new FileReader();
        reader.onload = (e) => {
          this.imagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    // 新增：格式化文件大小显示
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
      closeModal() {
      this.newPost.user_id = this.currentUser.id
      this.showCreateModal = false;
      this.selectedFile = null;
      this.imagePreview = null;
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = '';
      }
    },
    async createPost() {
      try {
      let postData;

        // 如果有文件，使用 FormData
        if (this.selectedFile) {
          const formData = new FormData();
          formData.append('title', this.newPost.title);
          formData.append('content', this.newPost.content);
          formData.append('sub', this.newPost.sub);
          formData.append('mode', this.newPost.mode);
          formData.append('user_id', this.newPost.user_id);
          formData.append('image', this.selectedFile);
          postData = formData;
        } else {
          // 没有文件，使用普通对象
          postData = { ...this.newPost };
        }

        // 调用 Vuex action
        await this.$store.dispatch('createPost', postData);

        // 刷新帖子列表
        await this.fetchPosts('communication');

        // 关闭模态框并重置表单
        this.closeModal();
        this.newPost = {
          title: '',
          content: '',
          image: '',
          sub: 'communication',
          mode: '首页',
          user_id:  this.currentUser.id
        };
      } catch (error) {
        console.error('Failed to create post:', error)
        alert('创建失败，请重试')
      }
    },
    goToPostDetail(postId) {
    this.$router.push({ name: 'PostDetail', params: { id: postId } })
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

.blog-post {
  margin-bottom: 40px;
}

.blog-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.blog-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 15px;
}

.blog-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.blog-author {
  font-weight: 600;
  color: #2c3e50;
}

.blog-date {
  color: #95a5a6;
  font-size: 0.9rem;
}

.blog-image {
  width: 100%;
  border-radius: 8px;
  margin: 15px 0;
  max-height: 300px;
  object-fit: cover;
}

.blog-actions {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  color: #95a5a6;
}

.blog-action {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.blog-action:hover {
  color: #3498db;
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
/* 新增样式 */
.file-info {
  margin-top: 8px;
  font-size: 14px;
  color: #7f8c8d;
}

.preview-container {
  margin-top: 15px;
  text-align: center;
}

.image-preview {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  margin-top: 10px;
}

</style>