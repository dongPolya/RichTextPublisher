import { createRouter, createWebHistory } from 'vue-router'
import store from '../stores/appStore'


const routes = [
  {
    path: '/',
    redirect: '/communication'
  },
  {
    path: '/communication',
    name: 'Communication',
    component: () => import('../views/Communication.vue')
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('../views/Community.vue')
  },
  {
    path: '/data',
    name: 'Data',
    component: () => import('../views/Data.vue')
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: () => import('../views/Interact.vue')
  },
   {
    path: '/community/:id',
    name: 'CommunityDetail',
    component: () => import('../views/CommunityDetail.vue')
  },
  {
    path: '/post/:id',
    name: 'PostDetail',
    component: () => import('../views/PostDetail.vue')
  },
  {
    path: '/log/:id',
    name: 'LogDetail',
    component: () => import('../views/LogDetail.vue')
  },
  {
    path: '/users/:id',
    name: 'User',
    component: () => import('../views/User.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'LoginRegister',
    component: () => import('@/views/LoginRegister.vue'),
    meta: { requiresGuest: true }
  },
   {
    path: '/developer',
    name: 'Developer',
    component: () => import('@/views/Developer.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  // 确保认证检查已完成
  if (!store.state.authChecked) {
    try {
      await store.dispatch('checkAuth')
    } catch (error) {
      console.error('Auth check failed in router guard:', error)
    }
  }

  const isAuthenticated = !!store.state.user

  // 需要认证的路由
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  }
  // 访客专用路由（如登录页）
  else if (to.meta.requiresGuest && isAuthenticated) {
    next('/')
  }
  // 其他情况允许访问
  else {
    next()
  }
})


export default router