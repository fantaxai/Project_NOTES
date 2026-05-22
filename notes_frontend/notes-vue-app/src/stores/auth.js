// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const isAuthChecked = ref(false)
  
  const isAuthenticated = computed(() => {
    return !!accessToken.value && !!user.value
  })
  
 function setTokens(access, refresh) {
  accessToken.value = access
  refreshToken.value = refresh
  localStorage.setItem('access_token', access)
  if (refresh) {
    localStorage.setItem('refresh_token', refresh)
  }
  // Больше ничего не нужно — интерцептор читает из localStorage сам
}

function clearTokens() {
  accessToken.value = null
  refreshToken.value = null
  user.value = null
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('currentChecklist') // ← чистим чеклист при выходе
}
  
  async function register(username, email, password, password2) {
    try {
      console.log('Отправка запроса регистрации:', {
        username,
        email,
        password: '***',
        password2: '***'
      })
      
      const response = await authAPI.register({
        username,
        email,
        password,
        password2
      })
      
      console.log('Ответ сервера при регистрации:', response.data)
      
      const { access, refresh, user: userData } = response.data
      
      if (access && refresh) {
        user.value = userData || null
        setTokens(access, refresh)
        return { success: true }
      } else {
        return { 
          success: false, 
          error: 'Сервер не вернул токены авторизации' 
        }
      }
    } catch (error) {
      console.error('Ошибка при регистрации:', error)
      console.error('Детали ошибки:', error.response?.data)
      
      // Проверяем, есть ли ответ от сервера
      if (error.response) {
        // Сервер ответил с ошибкой
        const errorData = error.response.data
        
        // Обработка разных форматов ошибок Django REST
        if (typeof errorData === 'object') {
          // Формат: {"email": ["уже существует"], "password": ["слишком короткий"]}
          const messages = []
          for (const [field, errors] of Object.entries(errorData)) {
            if (Array.isArray(errors)) {
              messages.push(`${field}: ${errors.join(', ')}`)
            } else if (typeof errors === 'string') {
              messages.push(`${field}: ${errors}`)
            } else {
              messages.push(`${field}: ${JSON.stringify(errors)}`)
            }
          }
          return { 
            success: false, 
            error: messages.join('; ') || 'Ошибка валидации'
          }
        } else if (typeof errorData === 'string') {
          return { success: false, error: errorData }
        }
        
        return { success: false, error: 'Ошибка сервера' }
      } else if (error.request) {
        // Запрос был отправлен, но ответа нет
        return { 
          success: false, 
          error: 'Сервер недоступен. Проверьте подключение.' 
        }
      }
      
      return { 
        success: false, 
        error: 'Неизвестная ошибка при регистрации' 
      }
    }
  }
  
  // Остальные методы остаются без изменений...
  async function login(email, password) {
    try {
      const response = await authAPI.login({ email, password })
      const { access, refresh, user: userData } = response.data
      user.value = userData || null
      setTokens(access, refresh)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Ошибка входа' 
      }
    }
  }
  
  async function logout() {
    try {
      if (refreshToken.value) {
        await authAPI.logout(refreshToken.value)
      }
    } catch (error) {
      console.error('Ошибка при выходе:', error)
    } finally {
      clearTokens()
    }
  }
  
  async function checkAuth() {
    if (accessToken.value) {
      try {
        const response = await authAPI.getProfile()
        user.value = response.data
      } catch (error) {
        console.error('Ошибка проверки авторизации:', error)
        clearTokens()
      }
    }
    isAuthChecked.value = true
  }
  
  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isAuthChecked,
    register,
    login,
    logout,
    checkAuth
  }
})