import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite 配置：开发服务器将 /api 代理到后端 FastAPI（localhost:8000）
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
