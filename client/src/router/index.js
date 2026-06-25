// 路由配置与全局守卫
import { createRouter, createWebHistory } from 'vue-router'

// 路由表：meta.requiresAuth 需登录，meta.adminOnly 仅管理员
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    redirect: '/chat',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { title: '数据概览', adminOnly: true, icon: 'DataLine' }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('../views/Chat.vue'),
        meta: { title: '知识库问答', icon: 'ChatDotRound' }
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('../views/Documents.vue'),
        meta: { title: '文档管理', adminOnly: true, icon: 'Document' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理', adminOnly: true, icon: 'User' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：登录校验与管理员权限校验
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }
  // 已登录访问登录页则跳首页
  if (to.path === '/login' && token) {
    return next('/')
  }
  // 管理员专属路由拦截
  if (to.meta.adminOnly && user?.role !== 'admin') {
    return next('/chat')
  }
  next()
})

export default router
