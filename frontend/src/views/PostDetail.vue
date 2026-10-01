<template>
  <div class="page-content">
    <div v-if="post" class="post-detail">
      <div class="post-header">
        <div class="post-meta" @click="goToUser">
          <img :src="post.author.avatar" :alt="post.author.username" class="author-avatar">
          <div>
            <div class="author-name">{{ post.author.username }}</div>
            <div class="post-date">{{ formatDate(post.created_at) }}</div>
          </div>
        </div>
        <div class="post-category">{{ getCategoryName(post.sub) }}</div>
      </div>

      <h1 class="post-title">{{ post.title }}</h1>

      <div class="post-content" v-html="post.content"></div>

      <div class="post-actions">
        <button class="like-btn" @click="likePost">
          <font-awesome-icon :icon="['fas', 'heart']" /> {{ post.likes }}
        </button>
        <button class="action-btn">
          <font-awesome-icon :icon="['fas', 'bookmark']" /> 收藏
        </button>
        <button class="action-btn" @click="sharePost">
          <font-awesome-icon :icon="['fas', 'share']" /> 分享
        </button>
         <button
          v-if="isPostAuthor"
          class="action-btn edit-btn"
          @click="showEditModal = true"
        >
          <font-awesome-icon :icon="['fas', 'edit']" /> 编辑
        </button>
         <button
          v-if="isPostAuthor"
          class="action-btn delete-btn"
          @click="deletePost"
        >
          <font-awesome-icon :icon="['fas', 'trash-alt']" />
        </button>
      </div>

      <div class="comments-section">
        <h3>评论 ({{ post.comments_count || 0 }})</h3>

        <div class="comment-form">
          <textarea v-model="newComment" placeholder="写下你的评论..." rows="3"></textarea>
          <button class="submit-comment" @click="addComment">提交评论</button>
        </div>

        <div class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <img :src="comment.author.avatar" :alt="comment.author.username" class="comment-avatar">
            <div class="comment-content">
              <div class="comment-author">{{ comment.author.username }}</div>
             <div class="comment-footer">
              <div class="comment-text">{{ comment.content }}</div>
              <div class="comment-date">{{ formatDate(comment.created_at) }}</div>
               <button
                  v-if="currentUser && comment.author.id === currentUser.id"
                  class="comment-delete-btn"
                  @click="deleteComment(comment.id)"
                  title="删除评论"
                >
                  <font-awesome-icon :icon="['fas', 'trash-alt']" />
                </button>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="loading">
      加载中...
    </div>
     <!-- 编辑文章模态框 -->
    <CreateModal
      :visible="showEditModal"
      title="编辑文章"
      @close="showEditModal = false"
      @submit="updatePost"
    >
     <form class="edit-form">
        <div class="form-group">
          <label for="editTitle">标题</label>
          <input type="text" id="editTitle" v-model="editPost.title" required>
        </div>
        <div class="form-group">
          <label for="editCategory">文章分类</label>
          <select id="editCategory" v-model="editPost.sub" required>
            <option value="blog">出行记录</option>
            <option value="communication">公交之窗</option>
            <option value="chat">话题讨论</option>
            <option value="common">常规</option>
            <option value="data">数据统计</option>
          </select>
        </div>
        <div class="form-group">
          <label for="editContent">内容</label>
          <Editor
            id="editContent"
            v-model="editPost.content"
            api-key="ct6il0doy91ptb1u7t6r7z9xuawi1lpl44ukf19fgs18rkk0"
            :init="{
              height: 300,
              menubar: false,
              license_key: 'gpl',
              plugins: [
                'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
                'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                'insertdatetime', 'media', 'table', 'preview', 'help', 'wordcount'
              ],
              toolbar: 'undo redo | formatselect | bold underline forecolor backcolor | \
                        alignleft aligncenter alignright alignjustify | \
                        bullist numlist outdent indent | link image media | \
                        removeformat | help',
              branding: false,
              promotion: false
            }"
          />
        </div>
        <div class="form-group">
          <label for="postMode">帖子模式</label>
          <select id="postMode" v-model="editPost.mode" required>
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
import { useApi } from '@/composables/useApi'
import {mapGetters } from 'vuex'
import CreateModal from '@/components/CreateModal.vue'
import Editor from '@tinymce/tinymce-vue'

export default {
  name: 'PostDetail',
  components: {
    CreateModal,
    Editor
  },
  data() {
    return {
      post: null,
      comments: [],
      newComment: '',
      showEditModal: false,
      editPost: {
        title: '',
        content: '',
        sub: 'common',
        mode: '普通'
      },
      editorInitialized: false,
      userLikeCount: 0
    }
  },
   computed: {
    ...mapGetters(['currentUser', 'isAuthenticated']),
     // 计算属性：判断当前用户是否为文章作者
    isPostAuthor() {
      return this.isAuthenticated &&
             this.currentUser &&
             this.post &&
             this.post.author.id === this.currentUser.id
    }
  },
   watch: {
    '$route.params.id': {
    handler: function(id) {
      if (id) {
        this.fetchPostDetail(id)
      }
    },
    immediate: true
  },
    // 监听编辑模态框显示状态
    showEditModal(newVal) {
      if (newVal && this.post) {
        this.initializeEditForm()
      }
    },
    // 监听editPost.content变化
    'editPost.content'(newVal) {
      console.log('编辑内容变化:', newVal)
    }
  },
  async created() {
    const postId = this.$route.params.id
    await this.fetchPostDetail(postId)
    this.loadUserLikeCount()
  },
  methods: {
    async fetchPostDetail(postId) {
     this.loading = true
      this.error = null

      try {
        const { get } = useApi()
        const postData = await get(`/posts/${postId}/detail`)
        this.post = postData
        this.comments = postData.comments || []
      } catch (err) {
        console.error('Failed to fetch post detail:', err)
        this.error = '获取帖子详情失败，请稍后重试'
      } finally {
        this.loading = false
      }

    },
     async likePost() {
      if (this.userLikeCount >= 5) {
        alert('您已经达到点赞上限（5次）')
        return
      }

      try {
        const { post } = useApi()
        const result = await post(`/posts/${this.post.id}/like`, {
          user_id: this.currentUser?.id
        })
        // 更新本地数据
        this.post.likes = result.likes
        this.userLikeCount++
        this.saveUserLikeCount()
      } catch (error) {
        console.error('Failed to like post:', error)
        alert('点赞失败，请重试')
      }
    },
    // 改动10: 保存用户点赞计数到本地存储
    saveUserLikeCount() {
      const key = `post_${this.post.id}_likes`
      localStorage.setItem(key, this.userLikeCount)
    },
    // 改动11: 从本地存储加载用户点赞计数
    loadUserLikeCount() {
      if (!this.post) return
      const key = `post_${this.post.id}_likes`
      const count = localStorage.getItem(key)
      this.userLikeCount = count ? parseInt(count) : 0
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    getCategoryName(sub) {
      const categories = {
        'blog': '出行记录',
        'communication': '公交之窗',
        'chat': '话题讨论',
        'common': '常规',
        'data': '数据'
      }
      return categories[sub] || '未知分类'
    },
     goToUser() {
      // 假设用户ID为1，实际项目中应该从store或props获取
      const userId =  this.post.author.id
      this.$router.push(`/users/${userId}`)
    },
    async addComment() {
     if (!this.newComment.trim()) return

      this.loading = true
      this.error = null

      try {
        const { post } = useApi()
        const newCommentData = await post(`/posts/${this.post.id}/comments`, {
          content: this.newComment,
          user_id:this.currentUser.id
        })

        this.comments.unshift(newCommentData)
        this.newComment = ''
      } catch (err) {
        console.error('Failed to add comment:', err)
        this.error = '添加评论失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
     // 显示编辑模态框并填充当前文章数据
    showEditForm() {
      if (!this.isPostAuthor) {
        alert('您没有权限编辑此文章')
        return
      }
     // 确保post数据存在
    if (!this.post) {
        alert('文章数据未加载完成')
        return
     }

     this.editPost = {
         title: this.post.title || '',
         content: this.post.content || '',
         sub: this.post.sub || 'common',
         mode: this.post.mode || '普通'
     }
      this.$nextTick(() => {
    this.showEditModal = true
  })

    },
   initializeEditForm() {
  console.log('=== initializeEditForm 被调用 ===')
  console.log('当前文章数据:', this.post)
  console.log('当前编辑数据:', this.editPost)

  if (!this.post) {
    console.warn('文章数据不存在')
    return
  }


  this.editPost = {
    title: this.post.title || '',
    content: this.post.content || '',
    sub: this.post.sub || 'common',
    mode: this.post.mode || '普通'
  }

  console.log('编辑表单数据已设置:', {
    title: this.editPost.title,
    contentLength: this.editPost.content?.length || 0,
    contentPreview: this.editPost.content?.substring(0, 50) + '...'
  })

  this.editorInitialized = true
},
    async updatePost() {
      try {
        // 确保使用最新的编辑数据
        const postData = {
          title: this.editPost.title,
          content: this.editPost.content,
          sub: this.editPost.sub,
          title: this.editPost.title,
          mode: this.editPost.mode
        }

        const { put } = useApi()
        const updatedPost = await put(`/posts/${this.post.id}`, postData)

        // 更新本地数据
        this.post = { ...this.post, ...updatedPost }
        this.showEditModal = false
        this.editorInitialized = false

        alert('文章更新成功！')
      } catch (error) {
        console.error('Failed to update post:', error)
        alert('更新失败，请重试')
      }
    },

    async deletePost() {
      if (!confirm('确定要删除这篇文章吗？此操作不可恢复。')) {
        return
      }

      try {
        const { delete: del } = useApi()
        await del(`/posts/${this.post.id}`)

        alert('文章删除成功！')
        // 删除成功后返回列表页或首页
        this.$router.push('/community/${this.post.community_id}')
      } catch (error) {
        console.error('Failed to delete post:', error)
        alert('删除失败，请重试')
      }
    },
    // 改动4: 新增删除评论方法
    async deleteComment(commentId) {
      if (!confirm('确定要删除这条评论吗？此操作不可恢复。')) {
        return
      }

      try {
        const { delete: del } = useApi()
        await del(`/comments/${commentId}`)

        // 从列表中移除该评论
        this.comments = this.comments.filter(c => c.id !== commentId)
        // 更新评论计数
        if (this.post) {
          this.post.comments_count = (this.post.comments_count || 1) - 1
        }


        alert('评论删除成功！')
      } catch (error) {
        console.error('Failed to delete comment:', error)
        alert('删除评论失败，请重试')
      }
    },
    // 改动5: 新增分享功能
    sharePost() {
      const url = window.location.href
      navigator.clipboard.writeText(url).then(() => {
        alert('链接已复制到剪贴板！')
      }).catch(err => {
        console.error('复制失败:', err)
        prompt('请手动复制链接：', url)
      })
    }


  }
}
</script>

<style scoped>
.post-detail {
  max-width: 800px;
  margin: 0 auto;
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.post-meta {
  display: flex;
  align-items: center;
}

.author-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 15px;
}

.author-name {
  font-weight: 600;
  color: #2c3e50;
}

.post-date {
  color: #95a5a6;
  font-size: 0.9rem;
}

.post-category {
  background-color: #e8f4fc;
  color: #3498db;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 600;
}

.post-title {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.post-content {
  line-height: 1.8;
  color: #333;
  margin-bottom: 30px;
}

.post-content ::v-deep p {
  margin-bottom: 1rem;
}

.post-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  color: #7f8c8d;
}

.action-btn:hover {
  background: #e9ecef;
}
 .like-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  color: #7f8c8d;
}

.like-btn:hover {
    color: #e74c3c;
     opacity: 1;
  }

.comments-section {
  margin-top: 30px;
}

.comments-section h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.comment-form {
  margin-bottom: 30px;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  resize: vertical;
  margin-bottom: 10px;
}

.submit-comment {
  background-color: #1abc9c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
}

.submit-comment:hover {
  background-color: #16a085;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  display: flex;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.comment-content {
  flex: 1;
}

.comment-author {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.comment-text {
  color: #333;
  margin-bottom: 5px;
  line-height: 1.5;
}
.comment-footer {
   display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 15px;
  margin-top: 5px;
}
.comment-date {
  color: #95a5a6;
  font-size: 0.9rem;
}


.comment-delete-btn {
  background: none;
  border: none;
  color: #95a5a6;
  cursor: pointer;
  padding: 2px 5px;
  font-size: 0.8rem;
  opacity: 0.6;
  transition: all 0.2s;
}

.comment-delete-btn:hover {
  color: #e74c3c;
  opacity: 1;
}
/* 添加编辑按钮样式 */
.edit-btn {
  background-color: #f39c12;
  color: white;
  border-color: #f39c12;
}

.edit-btn:hover {
  background-color: #e67e22;
  border-color: #e67e22;
}
.delete-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  color: #7f8c8d;
  cursor: pointer;
  padding: 2px 5px;
  font-size: 0.8rem;
  opacity: 0.6;
  transition: all 0.2s;
}

.delete-btn:hover {
   color: #e74c3c;
  opacity: 1;
}

.edit-form {
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

.loading {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
}
</style>