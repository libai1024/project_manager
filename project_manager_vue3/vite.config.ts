import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0', // 允许局域网访问
    port: 5173,
    strictPort: false, // 如果端口被占用，自动尝试下一个可用端口
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        // 确保所有自定义 headers 都被转发
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            // 打印所有请求头（仅开发环境）
            if (process.env.NODE_ENV === 'development') {
              console.log('[Vite Proxy] 📥 Incoming request headers:', Object.keys(req.headers))
              const authHeader = req.headers.authorization || req.headers.Authorization
              console.log('[Vite Proxy] Authorization header:', authHeader ? authHeader.substring(0, 30) + '...' : 'NOT FOUND')
            }
            
            // 确保 Authorization header 被转发（检查多种可能的大小写）
            const authHeader = req.headers.authorization || req.headers.Authorization || req.headers['authorization'] || req.headers['Authorization']
            if (authHeader) {
              // 明确设置 Authorization header
              proxyReq.setHeader('Authorization', authHeader)
              if (process.env.NODE_ENV === 'development') {
                console.log('[Vite Proxy] ✅ Forwarding Authorization header to backend')
              }
            } else {
              if (process.env.NODE_ENV === 'development') {
                console.warn('[Vite Proxy] ⚠️ No Authorization header found in incoming request!')
                console.warn('[Vite Proxy] All incoming headers:', JSON.stringify(req.headers, null, 2))
              }
            }
            
            // 确保所有其他重要 headers 也被转发
            const importantHeaders = ['content-type', 'accept', 'user-agent']
            importantHeaders.forEach(headerName => {
              const headerValue = req.headers[headerName] || req.headers[headerName.toLowerCase()]
              if (headerValue && !proxyReq.getHeader(headerName)) {
                proxyReq.setHeader(headerName, headerValue)
              }
            })
          })
          
          // 监听代理响应，用于调试
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            if (process.env.NODE_ENV === 'development') {
              console.log('[Vite Proxy] 📤 Backend response status:', proxyRes.statusCode)
              if (proxyRes.statusCode === 401) {
                console.warn('[Vite Proxy] ⚠️ Backend returned 401 - checking if Authorization header was sent')
                console.warn('[Vite Proxy] Request URL:', req.url)
                console.warn('[Vite Proxy] Request method:', req.method)
              }
            }
          })
        },
      },
    },
  },
})
