<template>
  <div class="developer-page">
    <div class="page-header">
      <h2 class="page-title">开发者控制台</h2>
      <p class="page-description">管理系统内容:文章、社区和用户</p>
    </div>

    <!-- 顶部搜索框 - 文章管理 -->
    <div class="section-card">
      <div class="section-header">
        <h3>文章管理</h3>
      </div>
      <div class="search-container">
        <div class="search-controls">
          <input
            v-model="searchQuery"
            @keyup.enter="handleSearch"
            type="text"
            placeholder="搜索文章..."
            class="search-input"
          />
          <select v-model="searchType" class="search-select">
            <option value="post">帖子</option>
            <option value="log">日志</option>
            <option value="quiz">问题</option>
          </select>
          <select v-model="searchMode" class="search-select">
            <option value="title">按内容</option>
            <option value="id">按ID</option>
          </select>
          <button @click="handleSearch" class="search-btn">
            <i class="fas fa-search"></i> 搜索
          </button>
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <div v-for="result in searchResults" :key="`${result.item_type}-${result.id}`" class="result-item">
            <div class="result-info">
              <span class="result-type">{{ getItemTypeLabel(result) }}</span>
              <span class="result-id">ID: {{ result.id }}</span>
              <h4 class="result-title">{{ result.title || result.question }}</h4>
              <p class="result-meta">{{ result.sub || result.item_type }} | {{ formatDate(result.created_at) }}</p>
            </div>
            <div class="result-actions">
              <button v-if="result.item_type !== 'quiz'" @click="editItem(result)" class="btn-edit">
                <i class="fas fa-edit"></i> 编辑
              </button>
              <button @click="deleteItem(result)" class="btn-delete">
                <i class="fas fa-trash"></i> 删除
              </button>
            </div>
          </div>
        </div>
        <div v-else-if="hasSearched" class="no-results">
          <p>未找到相关结果</p>
        </div>
      </div>
    </div>

    <!-- 中部社区管理列表 -->
    <div class="section-card">
      <div class="section-header">
        <h3>社区管理</h3>
      </div>
      <div class="list-container">
        <div v-for="community in communities" :key="community.id" class="list-item">
          <div class="list-item-info">
            <img v-if="community.avatar" :src="community.avatar" class="item-avatar" alt="社区头像" />
            <div class="item-details">
              <h4>{{ community.name }}</h4>
              <p class="item-meta">{{ community.category }} | 成员: {{ community.member_count }} | 帖子: {{ community.post_count }}</p>
              <p class="item-description">{{ community.description }}</p>
            </div>
          </div>
          <div class="list-item-actions">
            <button @click="editCommunity(community)" class="btn-edit">
              <i class="fas fa-edit"></i> 编辑
            </button>
            <button @click="manageCommunityMembers(community)" class="btn-manage">
              <i class="fas fa-cog"></i> 管理
            </button>
            <button @click="deleteCommunity(community.id)" class="btn-delete">
              <i class="fas fa-trash"></i> 删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 下方用户管理列表 -->
    <div class="section-card">
      <div class="section-header">
        <h3>用户管理</h3>
      </div>
      <div class="list-container">
        <div v-for="user in users" :key="user.id" class="list-item">
          <div class="list-item-info">
            <img v-if="user.avatar" :src="user.avatar" class="item-avatar" alt="用户头像" />
            <div class="item-details">
              <h4>{{ user.username }}</h4>
              <p class="item-meta">{{ user.email }} | 注册时间: {{ formatDate(user.created_at) }}</p>
              <p v-if="user.title" class="item-description">头衔: {{ user.title }}</p>
            </div>
          </div>
          <div class="list-item-actions">
            <button @click="deactivateUser(user.id)" class="btn-delete">
              <i class="fas fa-user-times"></i> 注销
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <h3>编辑 {{ editItemType }}</h3>
        <form @submit.prevent="saveEdit">
          <div v-if="editItemType === '帖子' || editItemType === '日志'" class="form-group">
            <label>标题</label>
            <input v-model="editForm.title" type="text" required />
          </div>
          <div v-if="editItemType === '问题'" class="form-group">
            <label>问题</label>
            <textarea v-model="editForm.question" rows="3" required></textarea>
          </div>
          <div v-if="editItemType === '帖子' || editItemType === '日志'" class="form-group">
            <label>内容</label>
            <textarea v-model="editForm.content" rows="6" required></textarea>
          </div>
          <div v-if="editItemType === '社区'" class="form-group">
            <label>名称</label>
            <input v-model="editForm.name" type="text" required />
          </div>
          <div v-if="editItemType === '社区'" class="form-group">
            <label>分类</label>
            <input v-model="editForm.category" type="text" />
          </div>
          <div v-if="editItemType === '社区'" class="form-group">
            <label>简介</label>
            <textarea v-model="editForm.description" rows="3"></textarea>
          </div>
          <!-- ⭐ 新增：社区头像上传区域 -->
          <div v-if="editItemType === '社区'" class="form-group">
            <label>社区头像</label>
            <div class="image-upload-container">
              <img v-if="imagePreview || editForm.avatar" :src="imagePreview || editForm.avatar" class="current-avatar" alt="当前头像" />
              <input type="file" ref="avatarInput" @change="handleAvatarChange" accept="image/*" class="file-input" />
              <button type="button" @click="triggerAvatarUpload" class="btn-upload">选择图片</button>
              <p v-if="selectedAvatarFile" class="file-info">已选择: {{ selectedAvatarFile.name }}</p>
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeEditModal" class="btn-cancel">取消</button>
            <button type="submit" class="btn-save">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 社区成员管理模态框 -->
    <div v-if="showMembersModal" class="modal-overlay" @click.self="closeMembersModal">
      <div class="modal-content large-modal">
        <h3>社区成员管理 - {{ currentCommunity?.name }}</h3>
        <div v-if="communityMembers.length > 0" class="members-list">
          <div v-for="member in communityMembers" :key="member.id" class="member-item">
            <div class="member-info">
              <img v-if="member.avatar" :src="member.avatar" class="member-avatar" alt="头像" />
              <div>
                <h4>{{ member.username }}</h4>
                <p>{{ member.email }}</p>
              </div>
            </div>
            <button @click="removeMember(member.id)" class="btn-remove">
              <i class="fas fa-user-minus"></i> 移除
            </button>
          </div>
        </div>
        <div v-else class="no-members">
          <p>该社区暂无成员</p>
        </div>
        <div class="modal-actions">
          <button @click="closeMembersModal" class="btn-cancel">关闭</button>
        </div>
      </div>
    </div>
     <!-- 主页样式管理 -->
    <div class="section-card">
      <div class="section-header">
        <h3>主页样式管理</h3>
      </div>

      <!-- 设置主页样式表单 -->
      <div class="form-section">
        <h4>新建主页样式</h4>
        <form @submit.prevent="saveCover" class="cover-form">
          <div class="form-group">
            <label>背景图片</label>
            <div class="image-upload-container">
              <img v-if="bgPreview" :src="bgPreview" class="preview-image" alt="背景预览" />
              <input type="file" ref="bgInput" @change="handleBgChange" accept="image/*" class="file-input" />
              <button type="button" @click="triggerBgUpload" class="btn-upload">选择背景图片</button>
              <p v-if="selectedBgFile" class="file-info">已选择: {{ selectedBgFile.name }}</p>
            </div>
          </div>

          <div class="form-group">
            <label>副标题（Motto）</label>
            <textarea v-model="coverForm.motto" rows="3" placeholder="输入主页副标题..."></textarea>
          </div>

          <div class="form-group">
            <label>背景音乐（MP3）</label>
            <div class="music-upload-container">
              <audio v-if="musicPreview" :src="musicPreview" controls class="music-preview"></audio>
              <input type="file" ref="musicInput" @change="handleMusicChange" accept=".mp3,audio/mpeg" class="file-input" />
              <button type="button" @click="triggerMusicUpload" class="btn-upload">选择音乐文件</button>
              <p v-if="selectedMusicFile" class="file-info">已选择: {{ selectedMusicFile.name }}</p>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-save">
              <i class="fas fa-plus"></i> 添加样式
            </button>
          </div>
        </form>
      </div>

      <!-- 管理主页样式列表 -->
      <div class="list-container">
        <h4>所有主页样式</h4>
        <div v-for="cover in covers" :key="cover.id" class="list-item">
          <div class="list-item-info">
            <img v-if="cover.background_image" :src="cover.background_image" class="item-thumbnail" alt="背景缩略图" />
            <div class="item-details">
              <h4>样式 #{{ cover.id }}</h4>
              <p class="item-meta">创建时间: {{ formatDate(cover.created_at) }}</p>
              <p v-if="cover.motto" class="item-description">副标题: {{ cover.motto }}</p>
              <p v-if="cover.music" class="item-description">
                <i class="fas fa-music"></i> 有背景音乐
                <audio :src="cover.music" controls class="inline-audio"></audio>
              </p>
            </div>
          </div>
          <div class="list-item-actions">
            <button @click="deleteCover(cover.id)" class="btn-delete">
              <i class="fas fa-trash"></i> 删除
            </button>
          </div>
        </div>
        <div v-if="covers.length === 0" class="no-data">
          <p>暂无主页样式</p>
        </div>
      </div>
    </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Developer',
  setup() {
    const router = useRouter()

    // 搜索相关
    const searchQuery = ref('')
    const searchType = ref('post')
    const searchMode = ref('title')
    const searchResults = ref([])
    const hasSearched = ref(false)

    // 数据列表
    const communities = ref([])
    const users = ref([])

    // 编辑相关
    const showEditModal = ref(false)
    const editItemType = ref('')
    const editForm = ref({})
    const editingItem = ref(null)

    // 成员管理相关
    const showMembersModal = ref(false)
    const currentCommunity = ref(null)
    const communityMembers = ref([])

    // ⭐ 新增：图像上传相关响应式变量
    const selectedAvatarFile = ref(null)
    const imagePreview = ref(null)
    const avatarInput = ref(null)

    // 主页样式管理相关
    const covers = ref([])
    const selectedBgFile = ref(null)
    const bgPreview = ref(null)
    const bgInput = ref(null)
    const selectedMusicFile = ref(null)
    const musicPreview = ref(null)
    const musicInput = ref(null)
    const coverForm = ref({
      motto: ''
    })

    // 获取类型标签
    const getTypeLabel = (type) => {
      const labels = {
        post: '帖子',
        log: '日志',
        quiz: '问题'
      }
      return labels[type] || type
    }
     const getItemTypeLabel = (item) => {
      return getTypeLabel(item.item_type || item.type)
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString('zh-CN')
    }

    // ⭐ 新增：触发文件选择
    const triggerAvatarUpload = () => {
      if (avatarInput.value) {
        avatarInput.value.click()
      }
    }

    // ⭐ 新增：处理头像文件选择
    const handleAvatarChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        // 检查文件类型
        if (!file.type.match('image.*')) {
          alert('请选择图像文件')
          return
        }

        // 检查文件大小（限制5MB）
        if (file.size > 5 * 1024 * 1024) {
          alert('图片大小不能超过5MB')
          return
        }

        selectedAvatarFile.value = file

        // 创建预览
        const reader = new FileReader()
        reader.onload = (e) => {
          imagePreview.value = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    // 搜索功能
    const handleSearch = async () => {
      if (!searchQuery.value.trim()) {
        searchResults.value = []
        hasSearched.value = false
        return
      }

      try {
        const params = new URLSearchParams({
          q: searchQuery.value,
          type: searchType.value,
          mode: searchMode.value
        })

        const response = await fetch(`/api/search?${params}`, {
          credentials: 'include'
        })

        if (response.ok) {
          searchResults.value = await response.json()
          hasSearched.value = true
        }
      } catch (error) {
        console.error('Search failed:', error)
        alert('搜索失败')
      }
    }

    // 编辑项目
    const editItem = (item) => {
      editingItem.value = item
      editItemType.value = getItemTypeLabel(item.type)

      if (item.item_type === 'quiz') {
        editForm.value = {
          question: item.question
        }
      } else {
        editForm.value = {
          title: item.title,
          content: item.content || ''
        }
      }

      showEditModal.value = true
    }

    // ⭐ 修改：编辑社区方法，重置图像状态
    const editCommunity = (community) => {
      editingItem.value = { ...community, type: 'community' }
      editItemType.value = '社区'
      editForm.value = {
        name: community.name,
        category: community.category,
        description: community.description,
        avatar: community.avatar
      }
      // 重置图像上传状态
      selectedAvatarFile.value = null
      imagePreview.value = null
      showEditModal.value = true
    }

    // ⭐ 修改：保存编辑方法，支持文件上传
    const saveEdit = async () => {
      try {
        let endpoint = ''

        if (editingItem.value.type === 'post') {
          endpoint = `/api/posts/${editingItem.value.id}`
        } else if (editingItem.value.type === 'log') {
          endpoint = `/api/logs/${editingItem.value.id}`
        } else if (editingItem.value.type === 'quiz') {
          // Quiz 只支持删除，不支持编辑
          alert('问题暂不支持编辑')
          closeEditModal()
          return
        } else if (editingItem.value.type === 'community') {
          endpoint = `/api/communities/${editingItem.value.id}`

          // 如果有新选择的头像文件，使用 FormData
          if (selectedAvatarFile.value) {
            const formData = new FormData()
            formData.append('name', editForm.value.name)
            formData.append('category', editForm.value.category || '')
            formData.append('description', editForm.value.description || '')
            formData.append('avatar', selectedAvatarFile.value)

            const response = await fetch(endpoint, {
              method: 'PUT',
              credentials: 'include',
              body: formData
            })

            if (response.ok) {
              alert('保存成功')
              closeEditModal()
              loadData()
            } else {
              const error = await response.json()
              alert(`保存失败: ${error.error}`)
            }
            return
          }
        }

        // 普通 JSON 请求（没有文件上传的情况）
        const response = await fetch(endpoint, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(editForm.value)
        })

        if (response.ok) {
          alert('保存成功')
          closeEditModal()
          // 重新加载数据
          loadData()
        } else {
          const error = await response.json()
          alert(`保存失败: ${error.error}`)
        }
      } catch (error) {
        console.error('Save failed:', error)
        alert('保存失败')
      }
    }

    // ⭐ 修改：关闭编辑模态框，重置图像状态
    const closeEditModal = () => {
      showEditModal.value = false
      editForm.value = {}
      editingItem.value = null
      // 重置图像上传状态
      selectedAvatarFile.value = null
      imagePreview.value = null
      if (avatarInput.value) {
        avatarInput.value.value = ''
      }
    }

     const deleteItem = async (item) => {
      console.log('=== DELETE ITEM DEBUG ===')
      console.log('Item:', item)
      console.log('Item type:', item.item_type)
      console.log('Item id:', item.id)

      if (!confirm(`确定要删除这个${getItemTypeLabel(item)}吗？`)) {
        return
      }

      try {
        let endpoint = ''

        // ⭐ 关键修复：使用 item_type 而不是 type
        if (item.item_type === 'post') {
          endpoint = `/api/posts/${item.id}`
        } else if (item.item_type === 'log') {
          endpoint = `/api/logs/${item.id}`
        } else if (item.item_type === 'quiz') {
          endpoint = `/api/questions/${item.id}`
        } else {
          console.error('Unknown item type:', item.item_type)
          alert(`未知的类型: ${item.item_type}`)
          return
        }

        console.log('Endpoint:', endpoint)

        const response = await fetch(endpoint, {
          method: 'DELETE',
          credentials: 'include'
        })

        console.log('Response status:', response.status)
        console.log('Response ok:', response.ok)

        if (response.ok) {
          let result
          try {
            const text = await response.text()
            console.log('Response text:', text)
            result = text ? JSON.parse(text) : {}
          } catch (parseError) {
            console.error('JSON parse error:', parseError)
            result = {}
          }

          alert('删除成功')
          handleSearch()
        } else {
          try {
            const errorText = await response.text()
            console.error('Error response:', errorText)
            const error = errorText ? JSON.parse(errorText) : { error: 'Unknown error' }
            alert(`删除失败: ${error.error || '未知错误'}`)
          } catch (e) {
            alert(`删除失败: HTTP ${response.status}`)
          }
        }
      } catch (error) {
        console.error('Delete failed:', error)
        alert(`删除失败: ${error.message}`)
      }
    }

    // 删除社区
    const deleteCommunity = async (communityId) => {
      if (!confirm('确定要删除这个社区吗？此操作不可恢复！')) {
        return
      }

      try {
        const response = await fetch(`/api/communities/${communityId}`, {
          method: 'DELETE',
          credentials: 'include'
        })

        if (response.ok) {
          alert('删除成功')
          loadData()
        } else {
          const error = await response.json()
          alert(`删除失败: ${error.error}`)
        }
      } catch (error) {
        console.error('Delete community failed:', error)
        alert('删除失败')
      }
    }

    // ⭐ 修复：管理社区成员 - 直接显示成员列表
    const manageCommunityMembers = async (community) => {
      try {
        const response = await fetch(`/api/communities/${community.id}`, {
          credentials: 'include'
        })

        if (response.ok) {
          const data = await response.json()
          currentCommunity.value = community
          communityMembers.value = data.members || []
          showMembersModal.value = true
        } else {
          alert('获取成员列表失败')
        }
      } catch (error) {
        console.error('Fetch members failed:', error)
        alert('获取成员列表失败')
      }
    }

    // 移除成员
    const removeMember = async (userId) => {
      if (!confirm('确定要移除该成员吗？')) {
        return
      }

      try {
        const response = await fetch(
          `/api/communities/${currentCommunity.value.id}/members/${userId}`,
          {
            method: 'DELETE',
            credentials: 'include'
          }
        )

        if (response.ok) {
          alert('移除成功')
          // 重新加载成员列表
          manageCommunityMembers(currentCommunity.value)
        } else {
          const error = await response.json()
          alert(`移除失败: ${error.error}`)
        }
      } catch (error) {
        console.error('Remove member failed:', error)
        alert('移除失败')
      }
    }

    // 关闭成员模态框
    const closeMembersModal = () => {
      showMembersModal.value = false
      currentCommunity.value = null
      communityMembers.value = []
    }

    // 注销用户
    const deactivateUser = async (userId) => {
      if (!confirm('确定要注销该用户吗？这将删除用户及其所有内容！')) {
        return
      }

      try {
        const response = await fetch(`/api/developer/users/${userId}`, {
          method: 'DELETE',
          credentials: 'include'
        })

        if (response.ok) {
          alert('用户已注销')
          loadData()
        } else {
          const error = await response.json()
          alert(`注销失败: ${error.error}`)
        }
      } catch (error) {
        console.error('Deactivate user failed:', error)
        alert('注销失败')
      }
    }

    // 加载数据
    const loadData = async () => {
      try {
        // 加载社区列表
        const communitiesResponse = await fetch('/api/communities', {
          credentials: 'include'
        })
        if (communitiesResponse.ok) {
          communities.value = await communitiesResponse.json()
        }

        // 加载用户列表
        const usersResponse = await fetch('/api/users/all', {
          credentials: 'include'
        })
        if (usersResponse.ok) {
          users.value = await usersResponse.json()
        }
      } catch (error) {
        console.error('Load data failed:', error)
        alert('加载数据失败')
      }
    }
     const triggerBgUpload = () => {
      if (bgInput.value) {
        bgInput.value.click()
      }
    }

    const handleBgChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        if (!file.type.match('image.*')) {
          alert('请选择图像文件')
          return
        }
        if (file.size > 5 * 1024 * 1024) {
          alert('图片大小不能超过5MB')
          return
        }
        selectedBgFile.value = file
        const reader = new FileReader()
        reader.onload = (e) => {
          bgPreview.value = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }
     const triggerMusicUpload = () => {
      if (musicInput.value) {
        musicInput.value.click()
      }
    }

    const handleMusicChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        if (!file.type.match('audio.*') && !file.name.endsWith('.mp3')) {
          alert('请选择MP3音频文件')
          return
        }
        if (file.size > 10 * 1024 * 1024) {
          alert('音乐文件大小不能超过10MB')
          return
        }
        selectedMusicFile.value = file
        musicPreview.value = URL.createObjectURL(file)
      }
    }

    const saveCover = async () => {
      try {
        if (!selectedBgFile.value) {
          alert('请选择背景图片')
          return
        }

        const formData = new FormData()
        formData.append('background', selectedBgFile.value)
        formData.append('motto', coverForm.value.motto || '')
        if (selectedMusicFile.value) {
          formData.append('music', selectedMusicFile.value)
        }

        const response = await fetch('/api/covers', {
          method: 'POST',
          credentials: 'include',
          body: formData
        })

        if (response.ok) {
          alert('主页样式添加成功')
          // 重置表单
          selectedBgFile.value = null
          bgPreview.value = null
          selectedMusicFile.value = null
          musicPreview.value = null
          coverForm.value.motto = ''
          if (bgInput.value) bgInput.value.value = ''
          if (musicInput.value) musicInput.value.value = ''
          // 重新加载列表
          loadCovers()
        } else {
          const error = await response.json()
          alert(`添加失败: ${error.error}`)
        }
      } catch (error) {
        console.error('Save cover failed:', error)
        alert('添加失败')
      }
    }

    const deleteCover = async (coverId) => {
      if (!confirm('确定要删除这个主页样式吗？')) {
        return
      }

      try {
        const response = await fetch(`/api/covers/${coverId}`, {
          method: 'DELETE',
          credentials: 'include'
        })

        if (response.ok) {
          alert('删除成功')
          loadCovers()
        } else {
          const error = await response.json()
          alert(`删除失败: ${error.error}`)
        }
      } catch (error) {
        console.error('Delete cover failed:', error)
        alert('删除失败')
      }
    }

    const loadCovers = async () => {
      try {
        const response = await fetch('/api/covers')
        if (response.ok) {
          covers.value = await response.json()
        }
      } catch (error) {
        console.error('Load covers failed:', error)
      }
    }

    onMounted(() => {
      loadData()
      loadCovers()
    })

    return {
      searchQuery,
      searchType,
      searchMode,
      searchResults,
      hasSearched,
      communities,
      users,
      showEditModal,
      editItemType,
      editForm,
      showMembersModal,
      currentCommunity,
      communityMembers,
      // ⭐ 新增：返回图像上传相关的变量和方法
      selectedAvatarFile,
      imagePreview,
      avatarInput,
      covers,
      selectedBgFile,
      bgPreview,
      bgInput,
      selectedMusicFile,
      musicPreview,
      musicInput,
      coverForm,
      getTypeLabel,
      getItemTypeLabel,
      formatDate,
      triggerAvatarUpload,
      handleAvatarChange,
      handleSearch,
      editItem,
      saveEdit,
      closeEditModal,
      deleteItem,
      editCommunity,
      deleteCommunity,
      manageCommunityMembers,
      removeMember,
      closeMembersModal,
      deactivateUser,
       triggerBgUpload,
      handleBgChange,
      triggerMusicUpload,
      handleMusicChange,
      saveCover,
      deleteCover,
      loadCovers
    }
  }
}
</script>

<style scoped>
.developer-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-title {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.page-description {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.section-card {
  background: white;
  border-radius: 10px;
  padding: 25px;
  margin-bottom: 25px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.section-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e8f4fc;
}

.section-header h3 {
  font-size: 1.5rem;
  color: #2c3e50;
}

/* 搜索区域样式 */
.search-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.search-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 12px 15px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.search-select {
  padding: 12px 15px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  min-width: 120px;
}

.search-btn {
  padding: 12px 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.search-btn:hover {
  transform: translateY(-2px);
}

/* 搜索结果样式 */
.search-results {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  transition: box-shadow 0.3s;
}

.result-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-info {
  flex: 1;
}

.result-type {
  display: inline-block;
  padding: 4px 10px;
  background: #667eea;
  color: white;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-right: 10px;
}

.result-id {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-right: 10px;
}

.result-title {
  margin: 8px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.result-meta {
  color: #95a5a6;
  font-size: 0.9rem;
}

.result-actions {
  display: flex;
  gap: 10px;
}

.no-results {
  text-align: center;
  padding: 30px;
  color: #7f8c8d;
}

/* 列表样式 */
.list-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  transition: box-shadow 0.3s;
}

.list-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.list-item-info {
  display: flex;
  gap: 15px;
  flex: 1;
}

.item-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.item-details {
  flex: 1;
}

.item-details h4 {
  color: #2c3e50;
  margin-bottom: 5px;
  font-size: 1.1rem;
}

.item-meta {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.item-description {
  color: #95a5a6;
  font-size: 0.9rem;
}

.list-item-actions {
  display: flex;
  gap: 10px;
}

/* 按钮样式 */
.btn-edit, .btn-delete, .btn-manage, .btn-remove {
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-edit {
  background: #3498db;
  color: white;
}

.btn-edit:hover {
  background: #2980b9;
}

.btn-delete {
  background: #e74c3c;
  color: white;
}

.btn-delete:hover {
  background: #c0392b;
}

.btn-manage {
  background: #9b59b6;
  color: white;
}

.btn-manage:hover {
  background: #8e44ad;
}

.btn-remove {
  background: #e67e22;
  color: white;
}

.btn-remove:hover {
  background: #d35400;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.large-modal {
  max-width: 800px;
}

.modal-content h3 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #2c3e50;
  font-weight: 600;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

/* ⭐ 新增：图像上传相关样式 */
.image-upload-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.current-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e1e5e9;
}

.file-input {
  display: none;
}

.btn-upload {
  padding: 8px 16px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-upload:hover {
  background: #2980b9;
}

.file-info {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-cancel, .btn-save {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #95a5a6;
  color: white;
}

.btn-cancel:hover {
  background: #7f8c8d;
}

.btn-save {
  background: #27ae60;
  color: white;
}

.btn-save:hover {
  background: #229954;
}

/* 成员列表样式 */
.members-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.no-members {
  text-align: center;
  padding: 30px;
  color: #7f8c8d;
}

.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
}

.member-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.member-info h4 {
  color: #2c3e50;
  margin-bottom: 3px;
}

.member-info p {
  color: #7f8c8d;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .search-controls {
    flex-wrap: wrap;
  }

  .search-input {
    width: 100%;
  }

  .result-item,
  .list-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .result-actions,
  .list-item-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
/* ⭐ 新增：图像上传相关样式 */
.image-upload-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.current-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e1e5e9;
}

.preview-image {
  max-width: 300px;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #e1e5e9;
}

.item-thumbnail {
  width: 120px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
}

.music-upload-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.music-preview {
  width: 100%;
  max-width: 400px;
}

.inline-audio {
  margin-top: 5px;
  width: 200px;
}

.form-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.form-section h4 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.cover-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.no-data {
  text-align: center;
  padding: 30px;
  color: #7f8c8d;
}

.file-input {
  display: none;
}

.btn-upload {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-upload:hover {
  background: #2980b9;
}

.file-info {
  color: #7f8c8d;
  font-size: 0.9rem;
}
</style>
