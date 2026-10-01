import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './stores/appStore'

// 导入全局样式
import './assets/global.css'

// 导入Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import '@fortawesome/fontawesome-free/css/all.min.css'




library.add(fas, far)

const app = createApp(App)

app.use(router)
app.use(store)
app.component('font-awesome-icon', FontAwesomeIcon)

// 先挂载应用，再异步检查认证状态
app.mount('#app')

// 应用启动时检查认证状态（异步进行，不阻塞渲染）
store.dispatch('checkAuth').then(() => {
  console.log('Auth check completed')
}).catch(error => {
  console.error('Initial auth check failed:', error)
})
