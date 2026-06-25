// 用户状态管理：保存 token 与当前用户信息
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    // 从 localStorage 恢复用户信息
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  getters: {
    // 是否已登录
    isLoggedIn: (state) => !!state.token,
    // 是否为管理员
    isAdmin: (state) => state.user?.role === 'admin'
  },
  actions: {
    // 登录成功后保存登录态
    setLogin(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    // 退出登录，清除登录态
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
