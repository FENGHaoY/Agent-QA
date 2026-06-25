<script setup>
// 主框架布局：左侧菜单 + 顶栏，根据角色动态显示菜单项
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '../store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 菜单项定义，adminOnly 的项仅管理员可见
const allMenus = [
  { path: '/home', title: '数据概览', icon: 'DataLine', adminOnly: true },
  { path: '/chat', title: '知识库问答', icon: 'ChatDotRound', adminOnly: false },
  { path: '/documents', title: '文档管理', icon: 'Document', adminOnly: true },
  { path: '/users', title: '用户管理', icon: 'User', adminOnly: true }
]

// 根据当前用户角色过滤可见菜单
const menus = computed(() =>
  allMenus.filter((m) => !m.adminOnly || userStore.isAdmin)
)

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
</script>

<template>
  <el-container class="layout">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="aside">
      <div class="logo">企业知识库</div>
      <el-menu :default-active="activeMenu" router class="menu" background-color="#001529"
        text-color="#c0c4cc" active-text-color="#ffffff">
        <el-menu-item v-for="m in menus" :key="m.path" :index="m.path">
          <el-icon><component :is="m.icon" /></el-icon>
          <span>{{ m.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶栏 -->
      <el-header class="header">
        <div class="title">RAG 企业内部知识库问答系统</div>
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
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background-color: #001529;
  overflow: hidden;
}
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 2px;
}
.menu {
  border-right: none;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
.title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #303133;
}
.main {
  background-color: #f5f7fa;
  padding: 20px;
}
</style>
