<template>
  <div class="page-content">
    <div class="page-header">
      <h2 class="page-title">出行日志</h2>
      <p class="page-description">分享你的旅行经历，阅读其他旅行者的精彩故事</p>
      <button class="create-btn" @click="showCreateModal = true">
        <font-awesome-icon icon="fa-map-marker-alt"/> 新建日志
      </button>
    </div>

    <div class="trip-list">
      <div v-for="(log, index) in logs" :key="index" class="card trip-card" @click="goToLogDetail(log.id)">
        <div class="card-header">
          <span>{{ log.title }}</span>
          <span class="trip-date">{{ formatDate(log.date) }}</span>
        </div>
        <div class="card-body">
          <div class="trip-destination">
            <font-awesome-icon icon="fa-map-marker-alt"/>{{ log.destination }}
          </div>
          <p>{{ log.description }}</p>

          <div class="trip-members">
            <div v-for="(member, mIndex) in log.members" :key="mIndex" class="member">
              <img :src="member.avatar" :alt="member.name">
            </div>
            <div v-if="log.members.length > 3" class="member" style="background-color: #3498db; color: white; display: flex; align-items: center; justify-content: center;">
              +{{ log.members.length - 3 }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <CreateModal
      :visible="showCreateModal"
      title="新建出行日志"
      @close="showCreateModal = false"
      @submit="createLog"
    >
      <form class="create-form">
        <div class="form-group">
          <label for="logTitle">标题</label>
          <input type="text" id="logTitle" v-model="newLog.title" required>
        </div>
        <div class="form-group">
          <label for="logDate">日期</label>
          <input type="date" id="logDate" v-model="newLog.date" required>
        </div>
        <div class="form-group">
          <label for="logDestination">目的地</label>
          <input type="text" id="logDestination" v-model="newLog.destination" required>
        </div>
        <div class="form-group">
          <label for="logDescription">描述</label>
          <textarea id="logDescription" v-model="newLog.description" rows="3" required></textarea>
        </div>
        <div class="form-group">
          <label for="logContent">详细内容</label>
          <textarea id="logContent" v-model="newLog.content" rows="5"></textarea>
        </div>
        <div class="form-group">
          <label for="logCategory">出行类型</label>
          <select id="logCategory" v-model="newLog.type" required>
            <option value="集体出行">集体出行</option>
            <option value="私人出行">私人出行</option>
          </select>
        </div>
         <div class="form-group">
          <label for="logtransport">交通工具</label>
          <select id="logtransport" v-model="newLog.transportation" required multiple>
            <option value="步行">步行</option>
            <option value="骑行">骑行</option>
            <option value="公交">公交</option>
            <option value="地铁">地铁</option>
            <option value="汽车">汽车</option>
            <option value="轮船">轮船</option>
            <option value="火车">火车</option>
            <option value="飞机">飞机</option>
            <option value="其他">其他</option>
          </select>
        </div>

        <div class="form-group">
          <label for="logFooter">页脚</label>
          <input type="text" id="logFooter" v-model="newLog.footer">
        </div>
      </form>
    </CreateModal>
  </div>
</template>

<script>
import { mapState, mapActions, mapGetters } from 'vuex'
import CreateModal from '@/components/CreateModal.vue'

export default {
  name: 'Log',
  components: {
    CreateModal
  },
  data() {
    return {
      showCreateModal: false,
      newLog: {
        title: '',
        date: '',
        destination: '',
        type: '集体出行',
        transportation:[],
        members: [
          { name: '默认成员', avatar: 'https://randomuser.me/api/portraits/lego/1.jpg' }
        ],
        description: '',
        content: '',
        footer: '',
        user_id: null
      }
    }
  },
  computed: {
    ...mapState(['logs']),
    ...mapGetters(['currentUser', 'isAuthenticated'])
  },
  async created() {
    await this.fetchLogs()
    // 检查用户是否已登录
    await this.$store.dispatch('checkAuth')
     if (this.isAuthenticated && this.currentUser) {
        this.newLog.user_id = this.currentUser.id
     } else {
     console.warn('用户未登录，无法创建帖子')
     this.$router.push('/login')
  }
  },
  methods: {
    ...mapActions(['fetchLogs', 'createLog']),
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN')
    },
    async createLog() {
      try {
        await this.$store.dispatch('createLog', this.newLog)
        this.showCreateModal = false
        this.newLog = {
          title: '',
          date: '',
          destination: '',
          type: '',
          transportation:[],
          members: [
            { name: '默认成员', avatar: 'https://randomuser.me/api/portraits/lego/1.jpg' }
          ],
          description: '',
          content: '',
          footer: '',
          user_id: this.currentUser.id
        }
      } catch (error) {
        console.error('Failed to create log:', error)
        alert('创建失败，请重试')
      }
    },
    goToLogDetail(logId) {
    this.$router.push({ name: 'LogDetail', params: { id: logId } })
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

.trip-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.trip-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trip-date {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.trip-destination {
  font-weight: 600;
  color: #1abc9c;
  margin-bottom: 10px;
}

.trip-members {
  display: flex;
  margin-top: 15px;
}

.member {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: -10px;
  border: 2px solid white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.member img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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