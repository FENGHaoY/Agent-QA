<script setup>
// 登录页：校验账号密码，成功后保存登录态并跳转
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()

const loginForm = reactive({
  username: 'admin',
  password: '123456'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const formRef = ref(null)
const loading = ref(false)

// 提交登录
const handleLogin = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const data = await login(loginForm)
      userStore.setLogin(data.access_token, data.user)
      ElMessage.success('登录成功')
      // 管理员进入数据概览，普通用户进入问答
      router.push(userStore.isAdmin ? '/home' : '/chat')
    } catch (e) {
      // 错误已由拦截器提示
    } finally {
      loading.value = false
    }
  })
}
</script>

<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="brand">
        <h1>企业知识库问答系统</h1>
        <p>RAG · LangChain · Qwen 智能问答平台</p>
      </div>
      <el-form ref="formRef" :model="loginForm" :rules="rules" class="login-form" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" :prefix-icon="'User'" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large"
            show-password :prefix-icon="'Lock'" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="tips">默认账号：admin / user01，密码：123456</div>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}
.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}
.brand {
  text-align: center;
  margin-bottom: 30px;
}
.brand h1 {
  font-size: 24px;
  color: #2a5298;
  margin-bottom: 8px;
}
.brand p {
  font-size: 13px;
  color: #909399;
}
.login-btn {
  width: 100%;
}
.tips {
  text-align: center;
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 10px;
}
</style>
