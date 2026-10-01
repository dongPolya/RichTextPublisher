<template>
  <div class="book-stage">
    <div class="scene">
      <div class="book" :style="bookStyle" @click="nextPage">
        <div class="base-right"></div>

        <div
          v-for="(leaf, i) in leaves"
          :key="i"
          class="leaf"
          :style="leafTransform(i)"
        >
          <!-- 正面 -->
          <div class="face front">
            <div v-if="leaf.front.type === 'cover'" class="cover-front">
              <div class="cover-frame"></div>
              <div class="cover-title">{{ coverTitle }}</div>
              <div class="cover-rule"></div>
              <div class="cover-sub">{{ coverSubtitle }}</div>
              <div class="cover-mark">✦</div>
            </div>
            <div v-else-if="leaf.front.type === 'post'" class="pg">
              <div class="pg-head">
                <span class="pg-date">{{ formatDate(leaf.front.post.created_at) }}</span>
                <span class="pg-weather">{{ authorName(leaf.front.post) }}</span>
              </div>
              <div class="pg-body" v-html="sanitize(leaf.front.post.content)"></div>
              <div class="pg-num">{{ leaf.front.pageNum }}</div>
            </div>
            <div v-else class="pg pg-blank"></div>
          </div>

          <!-- 背面 -->
          <div class="face back">
            <div v-if="leaf.back.type === 'endpaper'" class="endpaper">
              <div class="exlibris" v-html="endpaperText"></div>
            </div>
            <div v-else-if="leaf.back.type === 'post'" class="pg">
              <div class="pg-head">
                <span class="pg-date">{{ formatDate(leaf.back.post.created_at) }}</span>
                <span class="pg-weather">{{ authorName(leaf.back.post) }}</span>
              </div>
              <div class="pg-body" v-html="sanitize(leaf.back.post.content)"></div>
              <div class="pg-num">{{ leaf.back.pageNum }}</div>
            </div>
            <div v-else class="pg pg-blank"></div>
          </div>
        </div>
      </div>
    </div>

    <button class="reset-btn" @click.stop="reset">重新翻阅</button>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import DOMPurify from 'dompurify'

export default {
  name: 'FlippingBook',
  props: {
    posts: { type: Array, default: () => [] },
    coverTitle: { type: String, default: 'WIKI' },
    coverSubtitle: { type: String, default: '花样模板演示' },
    endpaperText: {
      type: String,
      default: '欢迎来到 Wiki 世界<br>每一页都是一个新的条目'
    }
  },
  setup(props) {
    // B 方案：进入即停在第一组内容
    const current = ref(0)

    const leaves = computed(() => {
      const result = []
      // 第 0 张：封面 / 环衬
      result.push({
        front: { type: 'cover' },
        back: { type: 'endpaper' }
      })
      // 剩下的 post 两张一组
      const total = props.posts.length
      for (let i = 0; i < total; i += 2) {
        const frontPost = props.posts[i]
        const backPost = props.posts[i + 1]
        result.push({
          front: frontPost
            ? { type: 'post', post: frontPost, pageNum: i + 1 }
            : { type: 'blank' },
          back: backPost
            ? { type: 'post', post: backPost, pageNum: i + 2 }
            : { type: 'blank' }
        })
      }
      return result
    })

    const totalLeaves = computed(() => leaves.value.length)

    const nextPage = () => {
      if (current.value < totalLeaves.value) current.value++
    }

    const reset = () => {
      current.value = 0
    }

    const leafTransform = (i) => {
      const flipped = i < current.value
      const rot = flipped ? -180 : 0
      let z
      if (flipped) {
        z = 0.8 + (i - (current.value - 1)) * 1.5
      } else {
        z = -(i - current.value) * 1.5
      }
      return { transform: `translateZ(${z}px) rotateY(${rot}deg)` }
    }

    const bookStyle = computed(() => ({
      transform: `translateX(${current.value > 0 ? 0 : -165}px) rotateX(40deg) rotateZ(-1.5deg)`
    }))

    const formatDate = (iso) => {
      if (!iso) return ''
      const d = new Date(iso)
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${y}年${m}月${day}日`
    }
    const authorName = (post) => {
      if (!post || !post.author) return ''
      return post.author.username || ''
    }
    const sanitize = (html) => (html ? DOMPurify.sanitize(html) : '')

    return {
      current, leaves, leafTransform, bookStyle,
      nextPage, reset, formatDate, authorName, sanitize
    }
  }
}
</script>

<style scoped>
/* ============ 外层容器：只负责布局 ============ */
.book-stage {
  --pw: 330px;
  --ph: 450px;
  /* 书体倾斜角的正切值，需与 bookStyle 里的 rotateX(40deg) 保持一致：tan(40deg) ≈ 0.8391 */
  --tilt-tan: 0.8391;
  /* 封底内衬相对纸页平面的后退深度（4px 足够分层，又不至于被视角拉开） */
  --depth: 4px;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0 40px;
  box-sizing: border-box;
  width: 100%;
}

/* ============ 3D 场景：perspective 唯一归属层 ============ */
.scene {
  position: relative;
  perspective: 2400px;
  perspective-origin: 50% 40%;
}

/* 场景阴影 */
.scene::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 55%;
  transform: translate(-50%, 30%);
  width: 700px;
  height: 80px;
  background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.55), transparent 70%);
  filter: blur(30px);
  z-index: -1;
  pointer-events: none;
}

/* ============ 书本体 ============ */
.book {
  position: relative;
  width: calc(var(--pw) * 2);
  height: var(--ph);
  transform-style: preserve-3d;
  transition: transform 0.85s cubic-bezier(0.4, 0.08, 0.2, 1);
  cursor: pointer;
  will-change: transform;
}

/* 右侧底层（封底内衬） */
.base-right {
  position: absolute;
  top: 0;
  left: var(--pw);
  width: var(--pw);
  height: var(--ph);
  border-radius: 2px 8px 8px 2px;
  background:
    radial-gradient(circle at 75% 25%, rgba(255, 200, 140, 0.1), transparent 60%),
    linear-gradient(150deg, #6b4326 0%, #4b2c17 55%, #341e0e 100%);
  box-shadow:
    inset 0 0 0 1px rgba(255, 215, 160, 0.12),
    inset 0 0 70px rgba(0, 0, 0, 0.6);
  /*
   * 对齐修正：
   * 书本体带着 rotateX(40deg)，同一块平面只要 z 不同，投影到屏幕上的高度就不同 ——
   * z = -depth 的平面会比 z = 0 的纸页低 depth · sin(40deg)，
   * 原先 depth = 60px，于是右侧书皮整整低了约 38px，这就是「书皮没和纸页对齐」的根因。
   * 这里用两步解决：
   *   1) depth 由 60px 收到 4px：既保留前后层次（避免与封面同面抢渲染），
   *      又让深度差引起的透视缩放小到看不见；
   *   2) 再用 translateY 抵消 depth · tan(40deg) 的投影位移，旋转之后即与左侧纸页齐平。
   *   注意 translateY 必须写在 translateZ 之前/之后都等价（纯平移可交换），
   *   关键是这个位移要发生在本地坐标系里、被父级 rotateX 之后才生效。
   */
  transform: translateY(calc(var(--depth) * var(--tilt-tan) * -1)) translateZ(calc(var(--depth) * -1));
}

/* ============ 可翻转的纸 ============ */
.leaf {
  position: absolute;
  top: 0;
  left: var(--pw);
  width: var(--pw);
  height: var(--ph);
  transform-origin: left center;
  transform-style: preserve-3d;
  transition: transform 0.95s cubic-bezier(0.44, 0.06, 0.22, 1);
  will-change: transform;
}

.face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  overflow: hidden;
  border-radius: 2px 7px 7px 2px;
  background: linear-gradient(160deg, #fdfaf1 0%, #f8f1de 55%, #f1e7ce 100%);
  box-shadow:
    inset 0 0 0 1px rgba(190, 160, 110, 0.2),
    inset 0 0 44px rgba(180, 145, 90, 0.1);
}
.face.back {
  transform: rotateY(180deg);
}

/* ============ 内页排版 ============ */
.pg {
  position: absolute;
  inset: 0;
  padding: 40px 34px 30px 44px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  background-image: repeating-linear-gradient(
    180deg,
    transparent 0 33px,
    rgba(168, 132, 80, 0.13) 33px 34px
  );
  background-position: 0 108px;
}
.face.back .pg {
  padding: 40px 44px 30px 34px;
}

.pg::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  width: 46px;
  background: linear-gradient(
    90deg,
    rgba(120, 88, 48, 0.26),
    rgba(120, 88, 48, 0.05) 55%,
    transparent
  );
  pointer-events: none;
}
.face.back .pg::before {
  left: auto;
  right: 0;
  background: linear-gradient(
    270deg,
    rgba(120, 88, 48, 0.26),
    rgba(120, 88, 48, 0.05) 55%,
    transparent
  );
}

.pg-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-bottom: 9px;
  margin-bottom: 22px;
  border-bottom: 1px solid rgba(165, 125, 72, 0.38);
  color: #8a6335;
  font-size: 15px;
  letter-spacing: 0.1em;
  flex: 0 0 auto;
}
.pg-weather {
  font-size: 12.5px;
  color: #ad9674;
  letter-spacing: 0.14em;
}

.pg-body {
  flex: 1;
  min-height: 0;
  font-size: 15px;
  line-height: 1.95;
  color: #3d2e1d;
  letter-spacing: 0.03em;
  overflow: hidden;
  word-break: break-word;
}

.pg-body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 6px 0;
}
.pg-body :deep(a) {
  color: #8a6335;
  text-decoration: underline;
}
.pg-body :deep(h1),
.pg-body :deep(h2),
.pg-body :deep(h3),
.pg-body :deep(h4) {
  font-size: 1.05em;
  margin: 6px 0 4px;
  color: #3d2e1d;
}
.pg-body :deep(p) { margin: 0 0 6px; }
.pg-body :deep(ul),
.pg-body :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}
.pg-body :deep(blockquote) {
  border-left: 3px solid rgba(138, 99, 53, 0.5);
  padding: 2px 10px;
  color: #7a634a;
  margin: 6px 0;
}
.pg-body :deep(pre) {
  background: rgba(60, 45, 28, 0.9);
  color: #f1e7ce;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 0.85em;
  overflow-x: auto;
}

.pg-num {
  flex: 0 0 auto;
  text-align: center;
  font-size: 11px;
  color: #bda88a;
  letter-spacing: 0.28em;
  padding-top: 8px;
}
.pg-blank {
  background: linear-gradient(160deg, #fdfaf1 0%, #f8f1de 55%, #f1e7ce 100%);
}

/* ============ 封面 ============ */
.cover-front {
  position: absolute;
  inset: 0;
  border-radius: 2px 8px 8px 2px;
  background:
    radial-gradient(circle at 22% 12%, rgba(255, 208, 152, 0.16), transparent 55%),
    radial-gradient(circle at 85% 95%, rgba(0, 0, 0, 0.4), transparent 60%),
    linear-gradient(150deg, #7e4d2a 0%, #5d3620 46%, #442510 100%);
  box-shadow:
    inset 0 0 0 1px rgba(255, 215, 160, 0.2),
    inset 0 0 70px rgba(0, 0, 0, 0.55);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.cover-front::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 38px;
  background: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.62),
    rgba(0, 0, 0, 0.18) 55%,
    transparent
  );
}
.cover-front::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    repeating-linear-gradient(115deg, rgba(255, 255, 255, 0.022) 0 2px, transparent 2px 6px),
    repeating-linear-gradient(25deg, rgba(0, 0, 0, 0.05) 0 2px, transparent 2px 7px);
  pointer-events: none;
}

.cover-frame {
  position: absolute;
  inset: 28px 28px 28px 50px;
  border: 1px solid rgba(236, 202, 142, 0.42);
  pointer-events: none;
}
.cover-frame::after {
  content: '';
  position: absolute;
  inset: 6px;
  border: 1px solid rgba(236, 202, 142, 0.18);
}

.cover-title {
  position: relative;
  z-index: 2;
  font-family: 'STKaiti', 'KaiTi', 'Kaiti SC', 'Songti SC', 'SimSun', serif;
  font-size: 44px;
  font-weight: 700;
  letter-spacing: 0.34em;
  text-indent: 0.34em;
  background: linear-gradient(180deg, #fdf2c8 0%, #dcb667 46%, #9c7528 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.55));
}
.cover-rule {
  position: relative;
  z-index: 2;
  width: 96px;
  height: 1px;
  margin: 26px 0 22px;
  background: linear-gradient(90deg, transparent, rgba(233, 199, 138, 0.75), transparent);
}
.cover-sub {
  position: relative;
  z-index: 2;
  font-size: 12.5px;
  letter-spacing: 0.3em;
  text-indent: 0.3em;
  color: rgba(235, 205, 150, 0.68);
}
.cover-mark {
  position: absolute;
  bottom: 44px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 15px;
  color: rgba(233, 199, 138, 0.42);
  letter-spacing: 0.5em;
  text-indent: 0.5em;
  z-index: 2;
}

/* ============ 环衬 ============ */
.endpaper {
  position: absolute;
  inset: 0;
  border-radius: 2px;
  background:
    radial-gradient(circle at 70% 30%, rgba(255, 200, 140, 0.1), transparent 60%),
    linear-gradient(150deg, #6d4529 0%, #4c2c17 60%, #341e0e 100%);
  box-shadow:
    inset 0 0 0 1px rgba(255, 215, 160, 0.14),
    inset 0 0 70px rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
}
.exlibris {
  font-family: 'STKaiti', 'KaiTi', 'Kaiti SC', 'Songti SC', 'SimSun', serif;
  font-size: 14px;
  line-height: 2.4;
  letter-spacing: 0.18em;
  text-align: center;
  color: rgba(238, 208, 155, 0.72);
  border: 1px solid rgba(238, 208, 155, 0.28);
  padding: 26px 30px;
  border-radius: 2px;
}

/* ============ 重置按钮 ============ */
.reset-btn {
  margin-top: 40px;
  padding: 9px 26px;
  font-family: inherit;
  font-size: 13px;
  letter-spacing: 0.3em;
  text-indent: 0.3em;
  color: rgba(120, 90, 55, 0.85);
  background: rgba(120, 90, 55, 0.05);
  border: 1px solid rgba(120, 90, 55, 0.3);
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.reset-btn:hover {
  color: #6b4326;
  border-color: rgba(120, 90, 55, 0.65);
  background: rgba(120, 90, 55, 0.12);
}

/* ============ 响应式：整体等比缩放，不碰 .book ============ */
@media (max-width: 820px) {
  .scene { transform: scale(0.78); }
}
@media (max-width: 600px) {
  .scene { transform: scale(0.56); }
}
@media (max-width: 420px) {
  .scene { transform: scale(0.42); }
}
</style>
