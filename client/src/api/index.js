// 业务接口封装
import request from './request'

// ===== 认证 =====
export const login = (data) => request.post('/auth/login', data)
export const getMe = () => request.get('/auth/me')

// ===== 用户管理（管理员）=====
export const listUsers = () => request.get('/users')
export const createUser = (data) => request.post('/users', data)
export const updateUser = (id, data) => request.put(`/users/${id}`, data)
export const deleteUser = (id) => request.delete(`/users/${id}`)

// ===== 文档管理（管理员）=====
export const listDocuments = () => request.get('/documents')
export const uploadDocument = (formData) =>
  request.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
export const deleteDocument = (id) => request.delete(`/documents/${id}`)

// ===== 智能问答 =====
export const askQuestion = (data) => request.post('/chat/ask', data)
// 会话历史：按会话聚合的列表，以及单个会话的全部问答
export const getChatSessions = () => request.get('/chat/sessions')
export const getSessionDetail = (sessionId) =>
  request.get(`/chat/sessions/${encodeURIComponent(sessionId)}`)

// ===== 数据统计（管理员）=====
export const getStatsOverview = () => request.get('/stats/overview')
