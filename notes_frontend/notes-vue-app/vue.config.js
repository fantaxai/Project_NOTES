const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: '0.0.0.0', // ⬅ОБЯЗАТЕЛЬНО для Docker
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://backend:8000', //  не 127.0.0.1, а имя сервиса
        changeOrigin: true,
      },
    },
    // Разрешаем доступ извне контейнера
    allowedHosts: 'all',
  },
  lintOnSave: false,
  pages: {
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
    },
  },
})
