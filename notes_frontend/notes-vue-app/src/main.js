import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { initUserId, setupAxiosInterceptors } from './utils/session'

// Настраиваем интерсепторы axios
setupAxiosInterceptors()

// Инициализируем приложение
async function bootstrap() {
  // Получаем или создаём user_id до загрузки данных
  await initUserId()
  
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)
  app.use(router)
  app.mount('#app')
}

bootstrap()