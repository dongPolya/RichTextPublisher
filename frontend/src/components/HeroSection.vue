<template>
  <div class="home-wrapper">
    <!-- ============ 1. 英雄区 ============ -->
    <section class="hero" :style="heroStyle">
      <div class="hero-content">
        <h1 class="hero-title">富文本、多层级</h1>
        <p class="hero-subtitle">
          {{ currentMotto || '基于Vue3+Python的富文本编辑及多层级系统' }}
        </p>
      </div>

      <div class="hero-buttons">
        <button class="btn-primary" @click="scrollToExperience">在线体验</button>
        <button class="btn-secondary btn-github" @click="goToSource">
          <i class="fab fa-github"></i>
          <span>获取源码</span>
        </button>
      </div>

      <!-- 顶部导航全部搬到这里，做成数码风小圆块，从左侧滑入 -->
      <div class="chips-container">
        <template v-if="authChecked">
          <div v-if="user" class="top-nav-item" @click="goToUser">
            <i class="fas fa-user"></i><span>{{ user.username }}</span>
          </div>
          <div v-else class="top-nav-item" @click="goToLogin">
            <i class="fas fa-sign-in-alt"></i><span>Login</span>
          </div>
        </template>
        <div v-else class="top-nav-item"><span>Loading...</span></div>

        <div class="top-nav-item"><i class="fas fa-book"></i><span>Wiki</span></div>
        <div class="top-nav-item" @click="goToData"><i class="fas fa-chart-bar"></i><span>Data</span></div>
        <div class="top-nav-item" @click="goToCommunity"><i class="fas fa-layer-group"></i><span>模板</span></div>
         <div class="top-nav-item" @click="goToQuiz"><i class="fas fa-question-circle"></i><span>Q&A</span></div>
        <div class="top-nav-item" @click="handleControlClick"><i class="fas fa-wrench"></i><span>Control</span></div>
        <div class="top-nav-item" @click="refreshCover" title="随机更换背景">
          <i class="fas fa-image"></i>
        </div>
        <div class="top-nav-item" @click="toggleMusic" title="播放/暂停背景音乐">
          <i :class="isPlaying ? 'fas fa-volume-up' : 'fas fa-music'"></i>
          <span>{{ isPlaying ? 'Playing' : 'Music' }}</span>
        </div>
      </div>

      <!-- 统计：维护天数(动态) / 内容类型 / 模板数量 -->
      <div class="stats-container">
        <StatCounter :number="maintainDays" label="维护天数" />
        <StatCounter number="8" label="内容类型" />
        <StatCounter number="12" label="模板数量" />
      </div>

      <audio ref="musicPlayer" :src="currentMusic" loop></audio>
    </section>

    <!-- ============ 2. 在线体验区 ============ -->
    <section ref="experienceSection" class="experience-section">
      <div class="section-header">
        <h2>在线体验</h2>
        <p>无需注册，即可在下方体验富文本编辑与实时 HTML 源码双向同步</p>
      </div>

      <!-- 2.1 富文本编辑器演示 -->
      <div class="editor-demo">
        <div class="demo-title">
          <h3>富文本编辑系统</h3>
          <span class="demo-tag">TinyMCE + Vue3</span>
        </div>

        <div class="editor-layout">
          <!-- 左：TinyMCE 编辑器 -->
          <div class="editor-pane">
            <div class="pane-label">预览 / 编辑</div>
            <Editor
              v-model="editorContent"
              :api-key="tinyApiKey"
              :init="editorInit"
            />
          </div>

          <!-- 右：可编辑的 HTML 源码，双向同步 -->
          <div class="source-pane">
            <div class="pane-label">HTML 源码（可编辑，实时双向同步）</div>
            <textarea v-model="editorContent" spellcheck="false"></textarea>
          </div>
        </div>

        <div class="demo-footer">
          <button class="btn-more" @click="goToCreateZone">体验更多 →</button>
        </div>
      </div>
      <section class="template-section">
      <div class="section-header">
        <h2>模板素材</h2>
        <p>精选500+免费网站模板,支持各种平台</p>
      </div>

      <!-- 加载中 -->
      <div v-if="templateLoading" class="placeholder-demo">
        <p>模板加载中……</p>
      </div>

      <!-- 有数据：轮播 -->
      <div
        v-else-if="templatePosts.length > 0 && currentPost"
        class="template-carousel"
      >
        <div class="carousel-wrapper">
          <!-- 左箭头 -->
          <button
            class="carousel-arrow arrow-left"
            @click="prevSlide"
            aria-label="上一个"
          >
            <i class="fas fa-chevron-left"></i>
          </button>

          <!-- 大容器：只显示富文本正文 -->
          <div class="carousel-stage">
            <transition name="carousel-slide" mode="out-in">
              <div :key="currentPost.id" class="carousel-item">
                <div class="carousel-content" v-html="currentPost.content"></div>
              </div>
            </transition>
          </div>

          <!-- 右箭头 -->
          <button
            class="carousel-arrow arrow-right"
            @click="nextSlide"
            aria-label="下一个"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>

        <!-- 下方信息：标题 / 创作者 / 获赞 / 获取该模板 -->
        <div class="carousel-meta">
          <h3 class="template-title">{{ currentPost.title || '未命名模板' }}</h3>

          <div class="meta-right">
            <span class="author-name">
             创作者： {{ currentPost.author ? currentPost.author.username : '匿名' }}
            </span>

            <div class="likes-info">
              <i class="fas fa-heart"></i>
              <span>{{ currentPost.likes || 0 }}</span>
            </div>

            <button
              class="btn-more btn-get-template"
              @click="goToTemplate(currentPost.id)"
            >
              获取该模板 →
            </button>
          </div>
        </div>
        <!-- 圆点导航 -->
        <div class="carousel-dots">
          <span
            v-for="(post, index) in templatePosts"
            :key="post.id"
            class="dot"
            :class="{ active: index === currentIndex }"
            @click="goToSlide(index)"
          ></span>
        </div>
      </div>

      <!-- 无数据 -->
      <div v-else class="placeholder-demo">
        <h3>模板展示</h3>
        <p>暂无模板内容，敬请期待……</p>
      </div>
    </section>
           <!-- ============ 2.3 Wiki 展示区（社区 5） ============ -->
      <section class="wiki-section">
        <div class="section-header">
          <h2>Wiki 社区</h2>
          <p>多层级文本发布嵌套系统演示</p>
        </div>

        <div v-if="wikiLoading" class="placeholder-demo">
          <p>Wiki 加载中……</p>
        </div>

        <div
          v-else-if="wikiPosts.length > 0 && currentWikiPost"
          class="wiki-carousel"
        >
          <div class="wiki-stage">
            <transition name="carousel-slide" mode="out-in">
              <div :key="currentWikiPost.id" class="wiki-item">
                <div class="wiki-content" v-html="currentWikiPost.content"></div>
              </div>
            </transition>
          </div>

          <div class="wiki-meta">
            <h3 class="template-title">
              {{ currentWikiPost.title || '未命名条目' }}
            </h3>
            <div class="meta-right">
              <span class="author-name">
                发起者{{ currentWikiPost.author ? currentWikiPost.author.username : '匿名' }}
              </span>
              <div class="likes-info">
                <i class="fas fa-heart"></i>
                <span>{{ currentWikiPost.likes || 0 }}</span>
              </div>
            </div>
          </div>

          <div class="carousel-dots">
            <span
              v-for="(post, index) in wikiPosts"
              :key="post.id"
              class="dot"
              :class="{ active: index === wikiIndex }"
            ></span>
          </div>
        </div>

        <div v-else class="placeholder-demo">
          <h3>Wiki 社区</h3>
          <p>暂无 Wiki 内容，敬请期待……</p>
        </div>
      </section>
     <!-- ============ 2.4 Wiki 模板展示（社区 6） ============ -->
    <section class="wiki-template-section">
      <div class="section-header">
        <h2>Wiki 模板</h2>
        <p>花样社区模板演示 —— 每一页都是一个 Wiki 条目</p>
      </div>

      <div v-if="wikiTemplateLoading" class="placeholder-demo">
        <p>加载中……</p>
      </div>

      <div v-else-if="wikiTemplatePosts.length > 0" class="book-wrap">
        <FlippingBook
          :posts="wikiTemplatePosts"
          cover-title="WIKI"
          cover-subtitle="花样模板演示"
          endpaper-text="欢迎来到 Wiki 世界<br>每一页都是一个新的条目"
        />
      </div>

      <div v-else class="placeholder-demo">
        <h3>Wiki 模板</h3>
        <p>暂无内容，敬请期待……</p>
      </div>
    </section>
           <!-- ============ 2.5 QA 互动展示区 ============ -->
      <section class="qa-section">
        <div class="section-header">
          <h2>QA 互动</h2>
          <p>每日问答演示 —— 进入即随机抽取一道题目</p>
        </div>
        <div class="qa-wrap">
          <Interact />
        </div>
      </section>
       </section>
  </div>
</template>

<script>
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { computed, ref, onMounted,onUnmounted} from 'vue'
import StatCounter from './StatCounter.vue'
import Editor from '@tinymce/tinymce-vue'
import FlippingBook from './FlippingBook.vue'
import Interact from '@/views/interact.vue'

export default {
  name: 'HeroSection',
  components: { StatCounter, Editor, FlippingBook, Interact},
  setup() {
    const store = useStore()
    const router = useRouter()

    /* ---------- 背景 / 座右铭 / 音乐 ---------- */
    const baseUrl = import.meta.env.BASE_URL || ''
    const backgroundImage = ref(`${baseUrl}背景.jpeg`)
    const currentMotto = ref('')
    const currentMusic = ref('')
    const isPlaying = ref(false)
    const musicPlayer = ref(null)

    /* ---------- 在线体验区引用 ---------- */
    const experienceSection = ref(null)

    /* ---------- TinyMCE 配置 ---------- */
    const tinyApiKey = 'ct6il0doy91ptb1u7t6r7z9xuawi1lpl44ukf19fgs18rkk0'

    // 预制内容（纯前端常量，无需后端）
    const defaultContent = [
      '<h1>欢迎体验富文本编辑系统</h1>',
      '<p>这是基于 <strong>TinyMCE</strong> 与 <em>Vue 3</em> 构建的富文本编辑器，支持标题、列表、表格、图片、链接、代码块等。</p>',
      '<ul><li>左侧实时编辑</li><li>右侧实时查看 / 修改 HTML 源码</li></ul>',
      '<blockquote>试着修改右侧源码，左侧预览会同步变化；反之亦然。</blockquote>',
      '<p>更多功能等待你在 <strong>创作专区</strong> 中探索。</p>'
    ].join('')

    const editorContent = ref(defaultContent)

    const editorInit = {
      height: 480,
      menubar: false,
      license_key: 'gpl',
      language: 'zh_CN',
      plugins:
        'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table wordcount',
      toolbar:
        'undo redo | blocks | bold italic forecolor backcolor | alignleft aligncenter alignright | bullist numlist outdent indent | link image media | table | code preview | fullscreen',
      block_formats:
        '段落=p;标题 1=h1;标题 2=h2;标题 3=h3;标题 4=h4;标题 5=h5;标题 6=h6;预格式化=pre',
      // 关键：把编辑器内的输入实时同步到 editorContent
      setup: (editor) => {
        editor.on('input change keyup undo redo', () => {
          const html = editor.getContent()
          if (html !== editorContent.value) {
            editorContent.value = html
          }
        })
      }
    }

    /* ---------- 用户 / 认证状态 ---------- */
    const user = computed(() => store.state.user)
    const authChecked = computed(() => store.state.authChecked)

    /* ---------- 统计数据 ---------- */
    // 维护天数：从起始日动态计算（"日期逻辑不变"）
    const startDate = new Date('2024-01-01') // ← 如需修改起始日，改这里
    const maintainDays = computed(() => {
      const diff = Math.floor((Date.now() - startDate.getTime()) / 86400000)
      return diff > 0 ? String(diff) : '0'
    })

    /* ---------- 源码链接（留空） ---------- */
    const sourceUrl = '' // ← 以后填 GitHub 地址即可

    /* ---------- hero 背景样式 ---------- */
    const heroStyle = computed(() => ({
      background: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.3)), url(${backgroundImage.value}) no-repeat center center/cover`
    }))

    /* ---------- 随机封面 ---------- */
    const loadRandomCover = async () => {
      try {
        const response = await fetch('/api/covers/random')
        if (response.ok) {
          const data = await response.json()
          if (data && data.background_image) {
            backgroundImage.value = data.background_image
            currentMotto.value = data.motto || ''
            currentMusic.value = data.music || ''
          }
        }
      } catch (error) {
        console.error('Failed to load random cover:', error)
      }
    }

    /* ---------- 交互方法 ---------- */
    const refreshCover = async () => {
      await loadRandomCover()
      if (musicPlayer.value) {
        musicPlayer.value.pause()
        isPlaying.value = false
      }
    }

    const toggleMusic = () => {
      if (!currentMusic.value) {
        alert('当前没有背景音乐')
        return
      }
      if (isPlaying.value) {
        musicPlayer.value.pause()
        isPlaying.value = false
      } else {
        musicPlayer.value.play().catch((error) => {
          console.error('Music play failed:', error)
          alert('音乐播放失败')
        })
        isPlaying.value = true
      }
    }

    const goToUser = () => {
      if (user.value && user.value.id) {
        router.push(`/users/${user.value.id}`)
      } else {
        router.push('/login')
      }
    }
    const goToLogin = () => router.push('/login')
    const goToData = () => router.push('/data')


    // 滚动到在线体验区
    const scrollToExperience = () => {
      const el = experienceSection.value
      if (el) {
        window.scrollTo({ top: el.offsetTop, behavior: 'smooth' })
      } else {
        window.scrollTo({ top: window.innerHeight, behavior: 'smooth' })
      }
    }

    // 「体验更多」→ 跳转到创作专区（沿用原来的 community/3）
    const goToCreateZone = () => {
      router.push('/community/3') // ← 如需换成你自己的创作社区 id，改这里
    }
   const goToCommunity = () => {
      router.push('/community/4')
    }
     const goToQuiz = () => {
      router.push('/quiz')
    }

    // 「获取源码」
    const goToSource = () => {
      if (sourceUrl) {
        window.open(sourceUrl, '_blank', 'noopener')
      } else {
        alert('源码仓库地址即将公布')
      }
    }

    /* ---------- 开发者入口 ---------- */
    const handleControlClick = () => {
      const isDeveloperAuthenticated = sessionStorage.getItem('developerAuthenticated')
      if (isDeveloperAuthenticated === 'true') {
        router.push('/developer')
      } else {
        const password = prompt('请输入开发者密码：')
        if (password) verifyDeveloperPassword(password)
      }
    }

    const verifyDeveloperPassword = async (password) => {
      try {
        const response = await fetch('/api/developer/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ password })
        })
        if (response.ok) {
          sessionStorage.setItem('developerAuthenticated', 'true')
          alert('开发者认证成功！')
          router.push('/developer')
        } else {
          alert('开发者密码错误！')
        }
      } catch (error) {
        console.error('Verification failed:', error)
        alert('验证失败，请重试')
      }
    }
        /* ---------- 模板展示区（社区 4） ---------- */
    const templatePosts = ref([])
    const templateLoading = ref(true)
    const currentIndex = ref(0)
    let carouselTimer = null

    const currentPost = computed(() => {
      if (templatePosts.value.length === 0) return null
      return templatePosts.value[currentIndex.value]
    })

    const fetchTemplatePosts = async () => {
      templateLoading.value = true
      try {
        const response = await fetch('/api/communities/4/posts')
        if (response.ok) {
          const data = await response.json()
          templatePosts.value = Array.isArray(data) ? data : []
          currentIndex.value = 0
          if (templatePosts.value.length > 1) {
            startCarousel()
          }
        } else {
          console.error('Failed to fetch template posts, status:', response.status)
        }
      } catch (error) {
        console.error('Failed to fetch template posts:', error)
      } finally {
        templateLoading.value = false
      }
    }

    const startCarousel = () => {
      if (carouselTimer) clearInterval(carouselTimer)
      carouselTimer = setInterval(() => {
        if (templatePosts.value.length > 1) {
          currentIndex.value = (currentIndex.value + 1) % templatePosts.value.length
        }
      }, 3000)
    }

    const goToSlide = (index) => {
      currentIndex.value = index
      // 手动切换后重置计时，避免刚点完就被自动翻走
      if (templatePosts.value.length > 1) startCarousel()
    }

    const truncateContent = (content) => {
      if (!content) return ''
      const plainText = content.replace(/<[^>]*>/g, '').trim()
      return plainText.length > 80 ? plainText.substring(0, 80) + '...' : plainText
    }
    const prevSlide = () => {
      if (templatePosts.value.length <= 1) return
      currentIndex.value =
        (currentIndex.value - 1 + templatePosts.value.length) %
        templatePosts.value.length
      startCarousel() // 手动切换后重置计时
    }

    // 下一个
    const nextSlide = () => {
      if (templatePosts.value.length <= 1) return
      currentIndex.value =
        (currentIndex.value + 1) % templatePosts.value.length
      startCarousel()
    }

    // 获取该模板 → 跳到帖子详情页
    const goToTemplate = (postId) => {
      router.push({ name: 'PostDetail', params: { id: postId } })
    }
     /* ---------- Wiki 展示区（社区 5） ---------- */
    const wikiPosts = ref([])
    const wikiLoading = ref(true)
    const wikiIndex = ref(0)
    let wikiTimer = null

    const currentWikiPost = computed(() => {
      if (wikiPosts.value.length === 0) return null
      return wikiPosts.value[wikiIndex.value]
    })

    const fetchWikiPosts = async () => {
      wikiLoading.value = true
      try {
        const response = await fetch('/api/communities/5/posts')
        if (response.ok) {
          const data = await response.json()
          wikiPosts.value = Array.isArray(data) ? data : []
          wikiIndex.value = 0
          if (wikiPosts.value.length > 1) {
            startWikiCarousel()
          }
        } else {
          console.error('Failed to fetch wiki posts, status:', response.status)
        }
      } catch (error) {
        console.error('Failed to fetch wiki posts:', error)
      } finally {
        wikiLoading.value = false
      }
    }

    const startWikiCarousel = () => {
      if (wikiTimer) clearInterval(wikiTimer)
      wikiTimer = setInterval(() => {
        if (wikiPosts.value.length > 1) {
          wikiIndex.value = (wikiIndex.value + 1) % wikiPosts.value.length
        }
      }, 5000)
    }
        /* ---------- Wiki 模板展示区（社区 6） ---------- */
    const wikiTemplatePosts = ref([])
    const wikiTemplateLoading = ref(true)

    const fetchWikiTemplatePosts = async () => {
      wikiTemplateLoading.value = true
      try {
        const response = await fetch('/api/communities/6/posts')
        if (response.ok) {
          const data = await response.json()
          wikiTemplatePosts.value = Array.isArray(data) ? data : []
        }
      } catch (error) {
        console.error('Failed to fetch wiki template posts:', error)
      } finally {
        wikiTemplateLoading.value = false
      }
    }

    onMounted(() => {
      loadRandomCover()
      fetchTemplatePosts()
       fetchWikiPosts()
       fetchWikiTemplatePosts()
    })
     onUnmounted(() => {       // ← 新增
      if (carouselTimer) clearInterval(carouselTimer)
      if (wikiTimer) clearInterval(wikiTimer)
    })

    return {
      // 状态
      user,
      authChecked,
      backgroundImage,
      currentMotto,
      currentMusic,
      isPlaying,
      musicPlayer,
      experienceSection,
      heroStyle,
      maintainDays,
      // TinyMCE
      tinyApiKey,
      editorContent,
      editorInit,
      // 方法
      goToUser,
      goToLogin,
      goToData,
      goToCommunity,
      goToQuiz,
      scrollToExperience,
      goToCreateZone,
      goToSource,
      handleControlClick,
      refreshCover,
      toggleMusic,
       templatePosts,
      templateLoading,
      currentIndex,
      currentPost,
      goToSlide,
        prevSlide,        // ← 新增
      nextSlide,        // ← 新增
      goToTemplate,
      truncateContent,
            // Wiki 展示
      wikiPosts,
      wikiLoading,
      wikiIndex,
      currentWikiPost,
       wikiTemplatePosts,
      wikiTemplateLoading,
    }
  }
}
</script>

<style scoped>
/* ==================== 英雄区 ==================== */
.hero {
  min-height: 100vh;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  position: relative;
  padding: 80px 20px 60px;
  box-sizing: border-box;
}

.hero-content {
  max-width: 1000px;
  padding: 20px;
  z-index: 1;
}

.hero-title {
  font-size: 3.2rem;
  font-weight: 700;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
  line-height: 1.25;
}

.hero-subtitle {
  font-size: 1.3rem;
  margin-bottom: 40px;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.hero-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 10px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  padding: 12px 30px;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background-color: #1abc9c;
  color: white;
}
.btn-primary:hover {
  background-color: #16a085;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}
.btn-secondary:hover {
  background-color: white;
  color: #2c3e50;
}

.btn-github i {
  font-size: 1.15rem;
}

/* ==================== 数码风小圆块 ==================== */
.chips-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 45px;
  max-width: 900px;
  animation: slideInFromLeft 0.9s ease-out both;
}

@keyframes slideInFromLeft {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.top-nav-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.95);
  font-family: 'Courier New', 'Consolas', monospace;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  cursor: pointer;
  padding: 10px 18px;
  border-radius: 50px;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(26, 188, 156, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  text-shadow: 0 0 6px rgba(26, 188, 156, 0.6);
  user-select: none;
}

.top-nav-item:hover {
  color: #1abc9c;
  background: rgba(26, 188, 156, 0.15);
  border-color: #1abc9c;
  box-shadow: 0 0 12px rgba(26, 188, 156, 0.55);
  transform: translateY(-2px);
}

.top-nav-item i {
  font-size: 0.85rem;
}

/* ==================== 统计 ==================== */
.stats-container {
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* ==================== 在线体验区 ==================== */
.experience-section {
  background: #f8f9fa;
  padding: 90px 20px 60px;
}

.section-header {
  text-align: center;
  margin-bottom: 50px;
}

.section-header h2 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.section-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.editor-demo {
  max-width: 1200px;
  margin: 0 auto 60px;
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.demo-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.demo-title h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0;
}

.demo-tag {
  background: #1abc9c;
  color: white;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.editor-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.editor-pane,
.source-pane {
  display: flex;
  flex-direction: column;
  min-width: 0; /* 防止 grid 子项溢出 */
}

.pane-label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.source-pane textarea {
  width: 100%;
  height: 480px;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: 'Courier New', 'Consolas', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #2c3e50;
  background: #f8f9fa;
  resize: vertical;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.source-pane textarea:focus {
  outline: none;
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26, 188, 156, 0.15);
}

.demo-footer {
  text-align: right;
  margin-top: 20px;
}

.btn-more {
  background: #2c3e50;
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-more:hover {
  background: #1abc9c;
  transform: translateX(4px);
}

.placeholder-demo {
  max-width: 1200px;
  margin: 0 auto 40px;
  background: white;
  border-radius: 12px;
  padding: 60px 30px;
  text-align: center;
  color: #95a5a6;
  border: 2px dashed #ddd;
}

.placeholder-demo h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}
/* ==================== 模板展示区 ==================== */
.template-section {
  max-width: 1200px;          /* ★ 与富文本区严格对齐 */
  width: 100%;
  margin: 80px auto 0;;             /* ★ 居中，不铺满屏幕 */
  box-sizing: border-box;
}

/* 舞台外层包裹 */
.carousel-wrapper {
  position: relative;
  width: 100%;
}

/* ★ 固定尺寸大容器 */
.carousel-stage {
  position: relative;
  width: 100%;
  height: 620px;              /* ★ 固定高度，稍高于富文本区 */
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;  /* ★ 明确轮廓 */
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  overflow: hidden;           /* ★ 超出部分裁掉，不缩放内容 */
  box-sizing: border-box;
}

/* 单张幻灯：绝对定位填满舞台 */
.carousel-item {
  position: absolute;
  inset: 0;
  padding: 40px 70px;         /* 左右多留空间，避免被箭头遮住 */
  overflow-y: auto;
  overflow-x: hidden;           /* ★ 内容过多时裁切，不改变容器大小 */
  box-sizing: border-box;
}

/* 富文本正文——按原始比例展示，不做任何缩放 */
.carousel-content {
  color: #2c3e50;
  line-height: 1.7;
  font-size: 1rem;
  word-break: break-word;
}

.carousel-content :deep(h1),
.carousel-content :deep(h2),
.carousel-content :deep(h3),
.carousel-content :deep(h4) {
  color: #2c3e50;
  margin: 20px 0 12px;
  line-height: 1.35;
}
.carousel-content :deep(p) { margin: 0 0 12px; }
.carousel-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 10px 0;
}
.carousel-content :deep(a) {
  color: #1abc9c;
  text-decoration: underline;
}
.carousel-content :deep(ul),
.carousel-content :deep(ol) {
  padding-left: 24px;
  margin: 10px 0;
}
.carousel-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}
.carousel-content :deep(table td),
.carousel-content :deep(table th) {
  border: 1px solid #ddd;
  padding: 8px 12px;
}
.carousel-content :deep(blockquote) {
  border-left: 4px solid #1abc9c;
  padding: 6px 16px;
  color: #7f8c8d;
  background: #f4fbf9;
  margin: 16px 0;
  border-radius: 0 6px 6px 0;
}
.carousel-content :deep(pre) {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 14px 18px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.9rem;
}

/* 轮播过渡 */
.carousel-slide-enter-active,
.carousel-slide-leave-active {
  transition: transform 0.6s ease, opacity 0.6s ease;
}
.carousel-slide-enter-from { transform: translateX(-100%); opacity: 0; }
.carousel-slide-enter-to   { transform: translateX(0);     opacity: 1; }
.carousel-slide-leave-from { transform: translateX(0);     opacity: 1; }
.carousel-slide-leave-to   { transform: translateX(100%);  opacity: 0; }

/* 左右箭头 */
.carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: none;
  background: rgba(44, 62, 80, 0.55);
  color: white;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
.carousel-arrow:hover {
  background: #1abc9c;
  transform: translateY(-50%) scale(1.08);
}
.arrow-left  { left: 14px; }
.arrow-right { right: 14px; }

/* 下方信息栏 */
.carousel-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
  padding: 18px 26px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06);
  flex-wrap: wrap;
}

.template-title {
  font-size: 1.2rem;
  color: #2c3e50;
  margin: 0;
  flex: 1;
  min-width: 200px;
}

.meta-right {
  display: flex;
  align-items: center;
  gap: 22px;
  flex-wrap: wrap;
}

.author-name {
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.95rem;
}

.likes-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #e74c3c;
  font-weight: 600;
  font-size: 0.95rem;
}

/* "获取该模板" 按钮：沿用 .btn-more 的观感 */
.btn-get-template {
  padding: 10px 24px;
  font-size: 0.95rem;
}

/* 圆点导航 */
.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ccc;
  cursor: pointer;
  transition: all 0.3s;
}
.dot.active {
  background: #1abc9c;
  width: 28px;
  border-radius: 5px;
}
/* ==================== Wiki 展示区 ==================== */
.wiki-section {
  max-width: 1200px;      /* 与模板区、富文本区对齐 */
  width: 100%;
  margin: 80px auto 0;
  box-sizing: border-box;
}

.wiki-carousel {
  width: 100%;
}

.wiki-stage {
  position: relative;
  width: 100%;
  height: 620px;          /* 与模板区容器一致 */
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  box-sizing: border-box;
}

.wiki-item {
  position: absolute;
  inset: 0;
  padding: 40px 50px;     /* 无箭头，左右只留 50px 即可 */
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 富文本内容样式：复用模板区规则的话可以直接删掉这段，
   但 scoped 下 class 不同，这里给一份等价样式更稳妥 */
.wiki-content {
  color: #2c3e50;
  line-height: 1.7;
  font-size: 1rem;
  word-break: break-word;
}
.wiki-content :deep(h1),
.wiki-content :deep(h2),
.wiki-content :deep(h3),
.wiki-content :deep(h4) {
  color: #2c3e50;
  margin: 20px 0 12px;
  line-height: 1.35;
}
.wiki-content :deep(p) { margin: 0 0 12px; }
.wiki-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 10px 0;
}
.wiki-content :deep(a) {
  color: #1abc9c;
  text-decoration: underline;
}
.wiki-content :deep(ul),
.wiki-content :deep(ol) {
  padding-left: 24px;
  margin: 10px 0;
}
.wiki-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}
.wiki-content :deep(table td),
.wiki-content :deep(table th) {
  border: 1px solid #ddd;
  padding: 8px 12px;
}
.wiki-content :deep(blockquote) {
  border-left: 4px solid #1abc9c;
  padding: 6px 16px;
  color: #7f8c8d;
  background: #f4fbf9;
  margin: 16px 0;
  border-radius: 0 6px 6px 0;
}
.wiki-content :deep(pre) {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 14px 18px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.9rem;
}

/* 下方信息栏：标题 / 创作者 / 获赞（无按钮） */
.wiki-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
  padding: 18px 26px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06);
  flex-wrap: wrap;
}

/* 响应式 */
@media (max-width: 992px) {
  .wiki-stage { height: 500px; }
  .wiki-item  { padding: 30px 40px; }
}
@media (max-width: 768px) {
  .wiki-stage { height: 400px; }
  .wiki-item  { padding: 20px 24px; }
  .wiki-meta  { padding: 14px 18px; }
}
@media (max-width: 576px) {
  .wiki-stage { height: 320px; }
}

/* ==================== 响应式 ==================== */
@media (max-width: 992px) {
  .hero-title {
    font-size: 2.4rem;
  }
  .stats-container {
    right: 30px;
    gap: 30px;
  }
  .editor-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  .hero-subtitle {
    font-size: 1.1rem;
  }
  .stats-container {
    position: relative;
    flex-direction: row;
    justify-content: center;
    right: auto;
    top: auto;
    transform: none;
    margin-top: 40px;
    gap: 30px;
  }
  .editor-demo {
    padding: 20px;
  }
  .source-pane textarea {
    height: 320px;
  }
}

@media (max-width: 576px) {
  .hero {
    padding: 60px 15px 40px;
  }
  .hero-title {
    font-size: 1.6rem;
  }
  .top-nav-item {
    padding: 8px 14px;
    font-size: 0.75rem;
    letter-spacing: 1px;
  }
}
/* ==================== Wiki 模板展示区 ==================== */
.wiki-template-section {
  max-width: 1200px;
  width: 100%;
  margin: 80px auto 0;
  box-sizing: border-box;
}

.book-wrap {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}
/* ==================== QA 互动展示区 ==================== */
.qa-section {
  max-width: 1200px;
  width: 100%;
  margin: 80px auto 0;
  box-sizing: border-box;
}

.qa-wrap {
  /* Interact 内部自己有 .page-content 的卡片样式（来自 App.vue 全局） */
  /* 这里只需要保证宽度受控、上下留白合适 */
  padding: 20px 0 40px;
}

/* Interact 里的 quiz-container 本来 max-width 是 800px，
   在展示区里给它更宽松一些，视觉上和上方容器更协调 */
.qa-wrap :deep(.quiz-container) {
  max-width: 900px;
}

</style>