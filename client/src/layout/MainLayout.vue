<script setup>
// 主框架布局：左侧分组菜单 + 顶栏，根据角色动态显示菜单项
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '../store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 当前激活的菜单
const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '知识库问答')
const isMobile = ref(false)
const sidebarOpen = ref(false)

// 菜单分组定义，adminOnly 的项仅管理员可见
const menuGroups = [
  {
    title: '智能工作台',
    desc: '日常问答与检索',
    items: [
      { path: '/chat', title: '知识库问答', subtitle: '多轮对话检索', icon: 'ChatDotRound', adminOnly: false }
    ]
  },
  {
    title: '运营管理',
    desc: '内容与数据维护',
    items: [
      { path: '/home', title: '数据概览', subtitle: '指标趋势看板', icon: 'DataLine', adminOnly: true },
      { path: '/documents', title: '文档管理', subtitle: '上传、入库与清理', icon: 'Document', adminOnly: true }
    ]
  },
  {
    title: '系统设置',
    desc: '账号与权限',
    items: [
      { path: '/users', title: '用户管理', subtitle: '角色与账号维护', icon: 'User', adminOnly: true }
    ]
  }
]

// 根据当前用户角色过滤可见菜单
const visibleMenuGroups = computed(() =>
  menuGroups
    .map((group) => ({
      ...group,
      items: group.items.filter((m) => !m.adminOnly || userStore.isAdmin)
    }))
    .filter((group) => group.items.length > 0)
)

const updateViewport = () => {
  isMobile.value = window.innerWidth <= 900
  if (!isMobile.value) sidebarOpen.value = false
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
  })
}

watch(() => route.path, closeSidebar)

onMounted(() => {
  updateViewport()
  window.addEventListener('resize', updateViewport)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateViewport)
})
</script>

<template>
  <el-container class="layout">
    <!-- 侧边栏 -->
    <el-aside width="260px" class="aside" :class="{ 'is-open': sidebarOpen }">
      <div class="brand">
        <div class="brand-mark">知</div>
        <div>
          <div class="brand-title">企业知识库</div>
          <div class="brand-subtitle">Enterprise RAG Center</div>
        </div>
      </div>

      <div class="nav-panel">
        <div v-for="group in visibleMenuGroups" :key="group.title" class="menu-group">
          <div class="group-header">
            <span>{{ group.title }}</span>
            <small>{{ group.desc }}</small>
          </div>
          <el-menu :default-active="activeMenu" router class="menu">
            <el-menu-item v-for="m in group.items" :key="m.path" :index="m.path" @click="closeSidebar">
              <el-icon><component :is="m.icon" /></el-icon>
              <div class="menu-copy">
                <span class="menu-title">{{ m.title }}</span>
                <span class="menu-subtitle">{{ m.subtitle }}</span>
              </div>
            </el-menu-item>
          </el-menu>
        </div>
      </div>

      <div class="aside-footer">
        <div class="status-dot"></div>
        <div>
          <div class="footer-title">知识服务在线</div>
          <div class="footer-desc">RAG Assistant Ready</div>
        </div>
      </div>
    </el-aside>
    <div v-if="isMobile && sidebarOpen" class="sidebar-mask" @click="closeSidebar"></div>

    <el-container>
      <!-- 顶栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-button v-if="isMobile" class="menu-toggle" circle @click="toggleSidebar">
            <el-icon><Menu /></el-icon>
          </el-button>
          <div>
            <div class="eyebrow">RAG 企业内部知识库问答系统</div>
            <div class="title">{{ currentTitle }}</div>
          </div>
        </div>
        <el-dropdown @command="handleLogout">
          <span class="user-info">
            <el-icon><Avatar /></el-icon>
            {{ userStore.user?.real_name || userStore.user?.username }}
            <el-tag size="small" :type="userStore.isAdmin ? 'danger' : 'info'" effect="plain">
              {{ userStore.isAdmin ? '管理员' : '普通用户' }}
            </el-tag>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main">
        <div class="content-shell">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
  background: #f4f7fb;
}
.aside {
  position: relative;
  z-index: 20;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 18% 12%, rgba(80, 160, 255, 0.28), transparent 28%),
    linear-gradient(180deg, #061529 0%, #071a33 52%, #04111f 100%);
  overflow: hidden;
  box-shadow: 18px 0 36px rgba(10, 25, 49, 0.18);
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 22px 18px;
  color: #fff;
}
.brand-mark {
  width: 42px;
  height: 42px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2b8cff, #6bd5ff);
  box-shadow: 0 12px 26px rgba(43, 140, 255, 0.36);
  font-size: 18px;
  font-weight: 700;
}
.brand-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
}
.brand-subtitle {
  margin-top: 3px;
  font-size: 11px;
  color: rgba(226, 238, 255, 0.62);
  letter-spacing: 0.5px;
}
.nav-panel {
  flex: 1;
  overflow-y: auto;
  padding: 6px 14px 18px;
}
.menu-group + .menu-group {
  margin-top: 18px;
}
.group-header {
  padding: 0 10px 8px;
  color: rgba(255, 255, 255, 0.9);
}
.group-header span {
  display: block;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1px;
}
.group-header small {
  display: block;
  margin-top: 3px;
  font-size: 11px;
  color: rgba(202, 221, 246, 0.54);
}
.menu {
  border-right: none;
  background: transparent;
}
.menu :deep(.el-menu-item) {
  height: 58px;
  margin: 5px 0;
  padding: 0 12px !important;
  border-radius: 16px;
  color: rgba(220, 232, 249, 0.78);
  background: transparent;
  transition: all 0.2s ease;
}
.menu :deep(.el-menu-item:hover) {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
  transform: translateX(2px);
}
.menu :deep(.el-menu-item.is-active) {
  color: #fff;
  background: linear-gradient(135deg, rgba(51, 142, 255, 0.95), rgba(32, 202, 255, 0.76));
  box-shadow: 0 14px 28px rgba(16, 114, 220, 0.3);
}
.menu :deep(.el-icon) {
  margin-right: 10px;
  font-size: 18px;
}
.menu-copy {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.menu-title {
  font-size: 14px;
  font-weight: 650;
}
.menu-subtitle {
  margin-top: 4px;
  font-size: 11px;
  color: rgba(230, 241, 255, 0.58);
}
.menu :deep(.el-menu-item.is-active) .menu-subtitle {
  color: rgba(255, 255, 255, 0.78);
}
.aside-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 16px 18px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #31d583;
  box-shadow: 0 0 0 6px rgba(49, 213, 131, 0.12);
}
.footer-title {
  font-size: 13px;
  font-weight: 650;
}
.footer-desc {
  margin-top: 2px;
  font-size: 11px;
  color: rgba(226, 238, 255, 0.58);
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  padding: 0 26px;
  background: rgba(255, 255, 255, 0.88);
  border-bottom: 1px solid rgba(219, 228, 240, 0.8);
  backdrop-filter: blur(16px);
  box-shadow: 0 8px 24px rgba(20, 39, 70, 0.06);
}
.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}
.menu-toggle {
  flex: 0 0 auto;
}
.eyebrow {
  margin-bottom: 4px;
  font-size: 12px;
  color: #7a8799;
}
.title {
  font-size: 20px;
  font-weight: 750;
  color: #16243a;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 10px;
  border-radius: 999px;
  color: #26374f;
  transition: background 0.2s ease;
}
.user-info:hover {
  background: #f0f5fb;
}
.main {
  overflow: auto;
  background:
    radial-gradient(circle at top right, rgba(62, 145, 255, 0.12), transparent 28%),
    linear-gradient(180deg, #f6f9fd 0%, #edf3f9 100%);
  padding: 24px;
}
.content-shell {
  min-height: calc(100vh - 120px);
}
.sidebar-mask {
  position: fixed;
  inset: 0;
  z-index: 15;
  background: rgba(4, 13, 28, 0.42);
  backdrop-filter: blur(3px);
}

@media (max-width: 900px) {
  .aside {
    position: fixed;
    inset: 0 auto 0 0;
    width: 280px !important;
    transform: translateX(-104%);
    transition: transform 0.24s ease;
  }
  .aside.is-open {
    transform: translateX(0);
  }
  .header {
    height: 64px;
    padding: 0 14px;
  }
  .eyebrow {
    display: none;
  }
  .title {
    font-size: 17px;
  }
  .user-info {
    max-width: 154px;
    overflow: hidden;
  }
  .main {
    padding: 14px;
  }
  .content-shell {
    min-height: calc(100vh - 92px);
  }
}

@media (max-width: 560px) {
  .user-info :deep(.el-tag) {
    display: none;
  }
  .title {
    max-width: 140px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
