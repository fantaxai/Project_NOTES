<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-header">
        <h1>📝 Копилка идей</h1>
        <p>Сохраняйте и организуйте ваши идеи</p>
      </div>

      <div class="auth-tabs">
        <button :class="{ active: activeTab === 'login' }" @click="switchTab('login')">Вход</button>
        <button :class="{ active: activeTab === 'register' }" @click="switchTab('register')">
          Регистрация
        </button>
      </div>

      <!-- Форма входа -->
      <form v-if="activeTab === 'login'" class="auth-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Email</label>
          <input v-model="loginForm.email" type="email" required placeholder="your@email.com" />
        </div>

        <div class="form-group">
          <label>Пароль</label>
          <input
            v-model="loginForm.password"
            type="password"
            required
            placeholder="Введите пароль"
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>

      <!-- Форма регистрации -->
      <form v-else class="auth-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label>Имя пользователя</label>
          <input
            v-model="registerForm.username"
            type="text"
            required
            placeholder="Придумайте имя"
          />
        </div>

        <div class="form-group">
          <label>Email</label>
          <input v-model="registerForm.email" type="email" required placeholder="your@email.com" />
        </div>

        <div class="form-group">
          <label>Пароль</label>
          <input
            v-model="registerForm.password"
            type="password"
            required
            placeholder="Минимум 8 символов"
          />
        </div>

        <div class="form-group">
          <label>Подтвердите пароль</label>
          <input
            v-model="registerForm.password2"
            type="password"
            required
            placeholder="Повторите пароль"
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const loading = ref(false)
const error = ref('')

const loginForm = reactive({
  email: '',
  password: '',
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password2: '',
})

function switchTab(tab) {
  activeTab.value = tab
  error.value = ''
}

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    console.log('Отправка входа:', loginForm.email)
    const result = await authStore.login(loginForm.email, loginForm.password)
    console.log('Результат входа:', result)

    if (result.success) {
      router.push('/')
    } else {
      error.value = result.error
      console.error('Ошибка входа:', result.error)
    }
  } catch (err) {
    console.error('Исключение при входе:', err)
    error.value = 'Ошибка соединения с сервером: ' + (err.message || '')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''

  if (registerForm.password !== registerForm.password2) {
    error.value = 'Пароли не совпадают'
    return
  }

  if (registerForm.password.length < 8) {
    error.value = 'Пароль должен быть не менее 8 символов'
    return
  }

  loading.value = true

  try {
    console.log('Отправка регистрации:', registerForm.email)
    const result = await authStore.register(
      registerForm.username,
      registerForm.email,
      registerForm.password,
      registerForm.password2
    )

    console.log('Результат регистрации:', result)

    if (result.success) {
      router.push('/')
    } else {
      error.value =
        typeof result.error === 'object'
          ? Object.values(result.error).flat().join(', ')
          : result.error
      console.error('Ошибка регистрации:', result.error)
    }
  } catch (err) {
    console.error('Исключение при регистрации:', err)
    error.value = 'Ошибка соединения с сервером: ' + (err.message || '')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-container {
  background: white;
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-header h1 {
  font-size: 32px;
  margin: 0 0 8px 0;
  color: #333;
}

.auth-header p {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.auth-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.auth-tabs button {
  flex: 1;
  padding: 12px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s;
  color: #666;
}

.auth-tabs button:hover {
  border-color: #667eea;
  color: #667eea;
}

.auth-tabs button.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 16px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.error-message {
  background: #fee;
  color: #dc3545;
  padding: 12px 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
