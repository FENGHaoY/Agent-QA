<script setup>
// 知识库问答页：对话气泡、来源展示、联网搜索开关、历史记录
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { askQuestion, getChatSessions, getSessionDetail } from '../api'

// 对话消息列表，每项 { role: 'user'|'assistant', content, sources }
const messages = ref([])
const question = ref('')
const useWeb = ref(false)
const loading = ref(false)
const listRef = ref(null)

// 会话 ID：用于后端维持本次会话的多轮上下文记忆
const newSessionId = () =>
  (crypto?.randomUUID?.() || `s-${Date.now()}-${Math.random().toString(16).slice(2)}`)
const sessionId = ref(newSessionId())

// 新建会话：重置会话 ID 并清空当前对话（开启全新的记忆上下文）
const startNewSession = () => {
  sessionId.value = newSessionId()
  messages.value = []
  ElMessage.success('已开启新会话')
}

// 历史记录抽屉（按会话聚合）
const historyVisible = ref(false)
const historyLoading = ref(false)
const sessionList = ref([])

// 打开历史抽屉并加载当前用户的会话列表
const openHistory = async () => {
  historyVisible.value = true
  historyLoading.value = true
  try {
    sessionList.value = await getChatSessions()
  } catch (e) {
    ElMessage.error('加载历史会话失败')
  } finally {
    historyLoading.value = false
  }
}

// 点击某个会话：加载整段对话到窗口，并恢复为当前会话以便继续追问
const loadSession = async (session) => {
  try {
    const detail = await getSessionDetail(session.session_id)
    const restored = []
    for (const m of detail) {
      restored.push({ role: 'user', content: m.question })
      restored.push({ role: 'assistant', content: m.answer || '（无回答记录）', sources: m.sources || [] })
    }
    messages.value = restored
    // 兼容旧数据：legacy-* 会话无法继续记忆，则开启新会话 ID
    sessionId.value = session.session_id.startsWith('legacy-') ? newSessionId() : session.session_id
    historyVisible.value = false
    scrollToBottom()
  } catch (e) {
    ElMessage.error('加载会话内容失败')
  }
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (listRef.value) {
    listRef.value.scrollTop = listRef.value.scrollHeight
  }
}

// 发送提问
const send = async () => {
  const q = question.value.trim()
  if (!q) {
    ElMessage.warning('请输入问题')
    return
  }
  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const data = await askQuestion({ question: q, use_web: useWeb.value, session_id: sessionId.value })
    messages.value.push({
      role: 'assistant',
      content: data.answer,
      sources: data.sources || []
    })
  } catch (e) {
    messages.value.push({ role: 'assistant', content: '抱歉，回答失败，请稍后重试。', sources: [] })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <el-card class="chat-card" shadow="never">
    <template #header>
      <div class="chat-header">
        <span>知识库智能问答</span>
        <div class="chat-header-right">
          <el-switch v-model="useWeb" active-text="联网搜索" inline-prompt />
          <el-button text type="primary" @click="startNewSession">
            <el-icon><Plus /></el-icon>
            <span>新建会话</span>
          </el-button>
          <el-button text type="primary" @click="openHistory">
            <el-icon><Clock /></el-icon>
            <span>历史记录</span>
          </el-button>
        </div>
      </div>
    </template>

    <!-- 消息列表 -->
    <div ref="listRef" class="message-list">
      <el-empty v-if="messages.length === 0" description="向我提问企业知识库相关问题吧～" />
      <div v-for="(m, i) in messages" :key="i" class="message-row" :class="m.role">
        <div class="bubble">
          <div class="content">{{ m.content }}</div>
          <!-- 来源展示 -->
          <div v-if="m.sources && m.sources.length" class="sources">
            <div class="sources-title">引用来源：</div>
            <el-tag v-for="(s, idx) in m.sources" :key="idx" size="small" class="source-tag"
              type="info" effect="plain">
              <a v-if="s.url" :href="s.url" target="_blank">{{ s.title }}</a>
              <span v-else>{{ s.title }}</span>
            </el-tag>
          </div>
        </div>
      </div>
      <div v-if="loading" class="message-row assistant">
        <div class="bubble"><el-icon class="is-loading"><Loading /></el-icon> 正在思考...</div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <el-input v-model="question" type="textarea" :rows="2" resize="none"
        placeholder="请输入问题，按 Enter 发送（Shift+Enter 换行）"
        @keydown.enter.exact.prevent="send" />
      <el-button type="primary" :loading="loading" @click="send">发送</el-button>
    </div>

    <!-- 历史会话抽屉：一个会话一项 -->
    <el-drawer v-model="historyVisible" title="我的会话历史" size="420px">
      <div v-loading="historyLoading" class="history-wrap">
        <el-empty v-if="!historyLoading && sessionList.length === 0" description="暂无会话历史" />
        <div v-for="s in sessionList" :key="s.session_id" class="history-item" @click="loadSession(s)">
          <div class="history-question">{{ s.title }}</div>
          <div class="history-meta">
            <el-tag size="small" type="info" effect="plain">{{ s.count }} 轮对话</el-tag>
            <span class="history-time">{{ s.last_time }}</span>
          </div>
        </div>
      </div>
    </el-drawer>
  </el-card>
</template>

<style scoped>
.chat-card {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
}
.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.history-wrap {
  min-height: 200px;
}
.history-item {
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.history-item:hover {
  border-color: #409eff;
  background: #f5f9ff;
}
.history-question {
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
  word-break: break-word;
}
.history-answer {
  font-size: 13px;
  color: #606266;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}
.history-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.history-time {
  font-size: 12px;
  color: #909399;
}
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}
.message-row {
  display: flex;
  margin-bottom: 16px;
}
.message-row.user {
  justify-content: flex-end;
}
.message-row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 10px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.message-row.user .bubble {
  background: #409eff;
  color: #fff;
}
.message-row.assistant .bubble {
  background: #f4f4f5;
  color: #303133;
}
.sources {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed #dcdfe6;
}
.sources-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.source-tag {
  margin: 2px 4px 2px 0;
}
.input-area {
  display: flex;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}
</style>
