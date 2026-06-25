// axios 实例封装：自动携带 JWT、统一处理后端响应与错误
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 120000 // 问答可能较慢，超时设为 120s
})

// 请求拦截器：注入 Authorization 头
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：解析统一响应结构，处理鉴权失败
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // 后端统一结构 { code, message, data }
    if (res && typeof res.code !== 'undefined') {
      if (res.code === 0) {
        return res.data
      }
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.message
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    } else if (status === 403) {
      ElMessage.error(detail || '没有访问权限')
    } else {
      ElMessage.error(detail || '服务器错误')
    }
    return Promise.reject(error)
  }
)

export default request
