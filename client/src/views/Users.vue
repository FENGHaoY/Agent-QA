<script setup>
// 用户管理页（管理员）：新增、编辑、删除用户，重置密码
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listUsers, createUser, updateUser, deleteUser } from '../api'

const users = ref([])
const loading = ref(false)

// 弹窗状态
const dialogVisible = ref(false)
const dialogTitle = ref('新增用户')
const isEdit = ref(false)
const formRef = ref(null)

// 表单数据
const form = reactive({
  id: null,
  username: '',
  password: '',
  real_name: '',
  role: 'user',
  status: 1
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    users.value = await listUsers()
  } finally {
    loading.value = false
  }
}

// 打开新增弹窗
const openCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新增用户'
  Object.assign(form, { id: null, username: '', password: '123456', real_name: '', role: 'user', status: 1 })
  dialogVisible.value = true
}

// 打开编辑弹窗
const openEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑用户'
  Object.assign(form, { id: row.id, username: row.username, password: '', real_name: row.real_name, role: row.role, status: row.status })
  dialogVisible.value = true
}

// 提交表单
const submit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    if (isEdit.value) {
      await updateUser(form.id, {
        password: form.password || null,
        real_name: form.real_name,
        role: form.role,
        status: form.status
      })
      ElMessage.success('修改成功')
    } else {
      await createUser({
        username: form.username,
        password: form.password || '123456',
        real_name: form.real_name,
        role: form.role,
        status: form.status
      })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadUsers()
  })
}

// 删除用户
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除用户「${row.username}」吗？`, '提示', { type: 'warning' }).then(async () => {
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadUsers()
  })
}

onMounted(loadUsers)
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <div class="header">
        <span>用户管理</span>
        <el-button type="primary" :icon="'Plus'" @click="openCreate">新增用户</el-button>
      </div>
    </template>

    <el-table :data="users" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="real_name" label="真实姓名" min-width="120" />
      <el-table-column label="角色" width="110">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'warning'" size="small">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="{ row }">{{ row.create_time?.replace('T', ' ').slice(0, 19) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="openEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password
            :placeholder="isEdit ? '留空则不修改密码' : '默认 123456'" />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="form.role">
            <el-radio value="user">普通用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0"
            active-text="启用" inactive-text="禁用" inline-prompt />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
