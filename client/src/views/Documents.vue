<script setup>
// 文档管理页（管理员）：上传文档入库、列表展示、删除
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listDocuments, uploadDocument, deleteDocument } from '../api'

const docs = ref([])
const loading = ref(false)
const uploading = ref(false)

// 加载文档列表
const loadDocs = async () => {
  loading.value = true
  try {
    docs.value = await listDocuments()
  } finally {
    loading.value = false
  }
}

// 自定义上传：调用后端上传并入库接口
const handleUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  uploading.value = true
  try {
    await uploadDocument(formData)
    ElMessage.success('上传并入库成功')
    loadDocs()
  } catch (e) {
    // 错误已由拦截器提示
  } finally {
    uploading.value = false
  }
}

// 删除文档
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除文档「${row.title}」吗？该操作会同时清理向量数据。`, '提示', {
    type: 'warning'
  }).then(async () => {
    await deleteDocument(row.id)
    ElMessage.success('删除成功')
    loadDocs()
  })
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

onMounted(loadDocs)
</script>

<template>
  <el-card shadow="never">
    <template #header>
      <div class="header">
        <span>文档管理</span>
        <el-upload :show-file-list="false" :http-request="handleUpload"
          accept=".pdf,.txt,.md,.docx">
          <el-button type="primary" :loading="uploading" :icon="'Upload'">上传文档</el-button>
        </el-upload>
      </div>
    </template>

    <el-alert type="info" :closable="false" show-icon
      title="支持 PDF / TXT / Markdown / DOCX 格式，上传后将自动解析、切片并写入 Chroma 向量库。"
      style="margin-bottom:16px" />

    <el-table :data="docs" v-loading="loading" border stripe class="docs-table">
      <el-table-column type="index" label="#" width="55" />
      <el-table-column prop="title" label="标题" min-width="160" />
      <el-table-column prop="filename" label="文件名" min-width="180" show-overflow-tooltip />
      <el-table-column prop="file_type" label="类型" width="90">
        <template #default="{ row }">
          <el-tag size="small">{{ row.file_type.toUpperCase() }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="大小" width="100">
        <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
      </el-table-column>
      <el-table-column prop="chunk_count" label="切片数" width="90" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '已入库' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="上传时间" width="180">
        <template #default="{ row }">{{ row.create_time?.replace('T', ' ').slice(0, 19) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.docs-table {
  width: 100%;
}

@media (max-width: 700px) {
  .header {
    align-items: flex-start;
    flex-direction: column;
  }
  .header :deep(.el-button) {
    width: 100%;
  }
}
</style>
