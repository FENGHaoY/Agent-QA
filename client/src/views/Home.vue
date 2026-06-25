<script setup>
// 管理后台首页：统计卡片 + ECharts 图表（问答趋势、文档类型、用户角色）
import { onMounted, ref, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getStatsOverview } from '../api'

// 统计卡片数据
const cards = ref({ users: 0, documents: 0, chats: 0, chunks: 0 })

// 图表 DOM 引用
const trendRef = ref(null)
const docTypeRef = ref(null)
const roleRef = ref(null)

// 渲染近 7 天问答折线图
const renderTrend = (data) => {
  const chart = echarts.init(trendRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: data.dates, boundaryGap: false },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '问答次数',
        type: 'line',
        smooth: true,
        data: data.counts,
        areaStyle: { color: 'rgba(64,158,255,0.2)' },
        lineStyle: { color: '#409eff' },
        itemStyle: { color: '#409eff' }
      }
    ]
  })
}

// 渲染饼图（文档类型 / 用户角色通用）
const renderPie = (dom, title, data) => {
  const chart = echarts.init(dom)
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [
      {
        name: title,
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '45%'],
        data,
        label: { formatter: '{b}\n{c}' }
      }
    ]
  })
}

onMounted(async () => {
  const data = await getStatsOverview()
  cards.value = data.cards
  await nextTick()
  renderTrend(data.chat_trend)
  renderPie(docTypeRef.value, '文档类型', data.doc_types)
  renderPie(roleRef.value, '用户角色', data.user_roles)
})
</script>

<template>
  <div>
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background:#409eff"><el-icon><User /></el-icon></div>
          <div class="stat-info"><div class="num">{{ cards.users }}</div><div class="label">用户总数</div></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background:#67c23a"><el-icon><Document /></el-icon></div>
          <div class="stat-info"><div class="num">{{ cards.documents }}</div><div class="label">文档总数</div></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background:#e6a23c"><el-icon><ChatDotRound /></el-icon></div>
          <div class="stat-info"><div class="num">{{ cards.chats }}</div><div class="label">问答总数</div></div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background:#f56c6c"><el-icon><Files /></el-icon></div>
          <div class="stat-info"><div class="num">{{ cards.chunks }}</div><div class="label">向量切片数</div></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>近 7 天问答趋势</template>
          <div ref="trendRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>文档类型分布</template>
          <div ref="docTypeRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>用户角色分布</template>
          <div ref="roleRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 26px;
}
.stat-info .num {
  font-size: 26px;
  font-weight: bold;
  color: #303133;
}
.stat-info .label {
  font-size: 13px;
  color: #909399;
}
.chart {
  height: 320px;
}
</style>
