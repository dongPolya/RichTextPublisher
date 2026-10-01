<template>
  <div class="page-content">
    <h2 class="page-title">每日问答</h2>
    <p class="page-description">丰富知识，获取积分奖励</p>
     <button class="create-btn" @click="showCreateModal = true">
        <font-awesome-icon :icon="['fas', 'plus']" /> 出题
      </button>


    <div class="quiz-container">
      <!-- 添加加载状态和空状态处理 -->
      <div v-if="loading" class="card quiz-card">
        <div class="card-body">
          <div class="loading-text">加载题目中...</div>
        </div>
      </div>

      <div v-else-if="currentQuestion" class="card quiz-card">
        <div class="card-header">
          今日问答
        </div>
        <div class="card-body">
          <div class="quiz-question">
            {{ currentQuestion.question }}
          </div>

          <div class="quiz-options">
            <div
              v-for="(option, index) in currentQuestion.options"
              :key="index"
              class="quiz-option"
              :class="{
                selected: selectedOption === index,
                correct: showResult && index === currentQuestion.correct_answer,
                incorrect: showResult && selectedOption === index && index !== currentQuestion.correct_answer
              }"
              @click="selectOption(index)"
            >
              {{ option }}
            </div>
          </div>

          <button
            class="quiz-submit"
            @click="submitAnswer"
            :disabled="selectedOption === null && !showResult"
          >
            {{ showResult ? '下一题' : '提交答案' }}
          </button>
        </div>
      </div>

      <div v-else class="card quiz-card">
        <div class="card-body">
          <div class="error-text">无法加载题目，请稍后重试</div>
        </div>
      </div>
      <CreateModal
      :visible="showCreateModal"
      title="新建题目"
      @close="showCreateModal = false"
      @submit="createQuestion"
    >
      <form class="create-form">
        <div class="form-group">
          <label for="questionTitle">题目</label>
          <textarea id="questionTitle" v-model="newQuestion.question" rows="3" required></textarea>
        </div>
        <div class="form-group">
          <label for="questionCategory">主题分类</label>
          <select id="questionCategory" v-model="newQuestion.sub" required>
            <option value="geography">地理知识</option>
            <option value="culture">文化常识</option>
            <option value="history">历史知识</option>
            <option value="common">常规问题</option>
          </select>
        </div>
        <div class="form-group">
          <label>选项</label>
          <div v-for="(option, index) in newQuestion.options" :key="index" class="option-input">
            <input
              type="text"
              :placeholder="'选项 ' + String.fromCharCode(65 + index)"
              v-model="newQuestion.options[index]"
              required
            >
          </div>
        </div>
        <div class="form-group">
          <label for="correctAnswer">正确答案</label>
          <select id="correctAnswer" v-model="newQuestion.correct_answer" required>
            <option v-for="(option, index) in newQuestion.options" :key="index" :value="index">
              {{ String.fromCharCode(65 + index) }}. {{ option }}
            </option>
          </select>
        </div>
      </form>
    </CreateModal>


      <!-- 排行榜保持不变 -->
      <div class="card">
        <div class="card-header">
          排行榜
        </div>
        <div class="card-body">
          <div class="ranking-list">
            <div v-for="(user, index) in ranking" :key="index" class="ranking-item">
              <div class="ranking-position">{{ index + 1 }}</div>
              <div class="ranking-avatar">
                <img :src="user.avatar" :alt="user.name">
              </div>
              <div class="ranking-info">
                <div class="ranking-name">{{ user.name }}</div>
                <div class="ranking-score">{{ user.score }} 分</div>
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
import CreateModal from '@/components/CreateModal.vue'

export default {
  name: 'Interact',
  components: {
    CreateModal
  },
  data() {
    return {
      selectedOption: null,
      showResult: false,
      showCreateModal: false,
      loading: false,
      newQuestion: {
        question: '',
        options: ['', '', '', ''],
        correct_answer: 0,
        type: 'single',
        sub: 'geography'
      },
      ranking: [
        {
          name: 'porridge',
          avatar: 'https://randomuser.me/api/portraits/men/22.jpg',
          score: 12
        },
        {
          name: 'cmbself',
          avatar: 'https://randomuser.me/api/portraits/women/23.jpg',
          score: 0
        },
        {
          name: '德源',
          avatar: 'https://randomuser.me/api/portraits/men/24.jpg',
          score: 0
        },
        {
          name: '宋孟奇',
          avatar: 'https://randomuser.me/api/portraits/women/25.jpg',
          score: 0
        },
        {
          name: '摄影爱好者',
          avatar: 'https://randomuser.me/api/portraits/men/26.jpg',
          score: 760
        }
      ]
    }
  },
  computed: {
    ...mapState(['currentQuestion']),
    isFormValid() {
      return (
        this.newQuestion.question.trim() !== '' &&
        this.newQuestion.options.every(opt => opt.trim() !== '') &&
        this.newQuestion.sub.trim() !== ''
      )
    }
  },
  async created() {
    await this.loadQuestion()
  },
  methods: {
    ...mapActions(['fetchRandomQuestion']),
     async createQuestion() {
      if (!this.isFormValid) {
        alert('请填写完整的题目信息')
        return
      }

      try {
        await this.$store.dispatch('createQuestion', this.newQuestion)
        alert('题目创建成功！')

        // 重置表单
        this.newQuestion = {
          question: '',
          options: ['', '', '', ''],
          correct_answer: 0,
          type: 'single',
          sub: '地理知识'
        }
        this.showCreateModal = false

        // 可选：重新加载题目以包含新创建的题目
        await this.loadQuestion()

      } catch (error) {
        console.error('Failed to create question:', error)
        alert('创建失败，请重试')
      }
    },
    async loadQuestion() {
      this.loading = true
      this.selectedOption = null
      this.showResult = false

      try {
        console.log('开始加载题目...')
        await this.fetchRandomQuestion()
        console.log('题目加载完成:', this.currentQuestion)
      } catch (error) {
        console.error('加载题目失败:', error)
        // 这里可以添加用户提示
      } finally {
        this.loading = false
      }
    },

    selectOption(index) {
      if (!this.showResult && !this.loading) {
        this.selectedOption = index
      }
    },

    async submitAnswer() {
      if (this.showResult) {
        // 下一题逻辑
        await this.loadQuestion()
      } else {
        // 提交答案逻辑
        this.showResult = true
        if (this.selectedOption === this.currentQuestion.correct_answer) {
          this.$store.commit('incrementScore')
          console.log('答案正确！当前分数:', this.$store.state.score)
        }
      }
    }
  }
}
</script>

<style scoped>
.quiz-container {
  max-width: 800px;
  margin: 0 auto;
}

.quiz-card {
  margin-bottom: 30px;
}

.quiz-question {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 15px;
  color: #2c3e50;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quiz-option {
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.quiz-option:hover {
  background-color: #f8f9fa;
}

.quiz-option.selected {
  background-color: #e8f4fc;
  border-color: #3498db;
}

.quiz-option.correct {
  background-color: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.quiz-option.incorrect {
  background-color: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.quiz-submit {
  background-color: #1abc9c;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  margin-top: 20px;
  transition: background-color 0.3s;
}

.quiz-submit:hover:not(:disabled) {
  background-color: #16a085;
}

.quiz-submit:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.loading-text, .error-text {
  text-align: center;
  padding: 40px;
  font-size: 1.1rem;
  color: #7f8c8d;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 5px;
  background-color: #f8f9fa;
}

.ranking-position {
  font-weight: bold;
  font-size: 1.2rem;
  width: 30px;
  text-align: center;
  color: #1abc9c;
}

.ranking-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 15px;
}

.ranking-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ranking-info {
  flex: 1;
}

.ranking-name {
  font-weight: 600;
}

.ranking-score {
  color: #7f8c8d;
  font-size: 0.9rem;
}
</style>