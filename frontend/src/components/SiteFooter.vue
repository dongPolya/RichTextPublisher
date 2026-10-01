<template>
  <footer class="site-footer">
    <!-- 网站图标行 -->
    <div class="footer-icons">
      <a
        v-for="link in socialLinks"
        :key="link.name"
        :href="link.url"
        target="_blank"
        rel="noopener"
        class="footer-icon"
        :title="link.title"
        :aria-label="link.title"
      >
        <i :class="link.icon"></i>
      </a>
    </div>

    <!-- 版权行 -->
    <div class="footer-copyright">
      <span>Copyright © 2026-present travelhub.</span>
      <span class="sep">✧</span>
      <span>tavel_hub.</span>
      <span class="sep">✧</span>
      <a
        href="https://github.com/"
        target="_blank"
        rel="noopener"
        class="footer-github"
      >
        open in Github
      </a>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'SiteFooter',
  data() {
    return {
      // 网址、图标、title 你按需替换
      socialLinks: [
        {
          name: 'github',
          title: 'GitHub',
          icon: 'fab fa-github',
          url: 'https://github.com/'
        },
        {
          name: 'weibo',
          title: '微博',
          icon: 'fab fa-weibo',
          url: 'https://weibo.com/'
        },
        {
          name: 'bilibili',
          title: '哔哩哔哩',
          icon: 'fab fa-bilibili',
          url: 'https://www.bilibili.com/'
        },
        {
          name: 'mail',
          title: '邮箱',
          icon: 'fas fa-envelope',
          url: 'mailto:Cmbself@163.com'
        },
        {
          name: 'rss',
          title: 'RSS',
          icon: 'fas fa-rss',
          url: '#'
        }
      ]
    }
  }
}
</script>

<style scoped>
.site-footer {
  background: #2c3e50;
  color: rgba(255, 255, 255, 0.75);
  padding: 40px 20px 26px;
  margin-top: 60px;
  text-align: center;
}

/* ---------- 图标行 ---------- */
.footer-icons {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 24px;
}

.footer-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  font-size: 1.15rem;
  text-decoration: none;
  transition: all 0.25s ease;
}

.footer-icon:hover {
  color: #1abc9c;
  background: rgba(26, 188, 156, 0.15);
  border-color: #1abc9c;
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(26, 188, 156, 0.35);
}

/* ---------- 版权行 ---------- */
.footer-copyright {
  font-size: 0.9rem;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.sep {
  color: rgba(26, 188, 156, 0.75);
  font-size: 0.85rem;
}

.footer-github {
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all 0.25s ease;
}

.footer-github:hover {
  color: #1abc9c;
  border-bottom-color: #1abc9c;
}

/* ---------- 响应式 ---------- */
@media (max-width: 576px) {
  .site-footer {
    padding: 30px 15px 20px;
  }
  .footer-icons {
    gap: 14px;
    margin-bottom: 18px;
  }
  .footer-icon {
    width: 36px;
    height: 36px;
    font-size: 1rem;
  }
  .footer-copyright {
    font-size: 0.8rem;
    gap: 6px;
  }
}
</style>