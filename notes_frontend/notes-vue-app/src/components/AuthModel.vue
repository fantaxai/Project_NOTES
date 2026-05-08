<template>
  <div class="auth-modal-overlay" @click="$emit('close')">
    <div class="auth-modal" @click.stop>
      <button class="close-btn" @click="$emit('close')">×</button>
      
      <div class="auth-tabs">
        <button 
          :class="{ active: activeTab === 'login' }"
          @click="activeTab = 'login'"
        >
          Вход
        </button>
        <button 
          :class="{ active: activeTab === 'register' }"
          @click="activeTab = 'register'"
        >
          Регистрация
        </button>
      </div>
      
      <!-- Форма входа -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <h2>Вход в аккаунт</h2>
        
        <div class="form-group">
          <label>Email</label>
          <input 
            v-model="loginForm.email" 
            type="email" 
            required 
            placeholder="your@email.com"
          />
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
      <form v-else @submit.prevent="handleRegister" class="auth-form">
        <h2>Создать аккаунт</h2>
        
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
          <input 
            v-model="registerForm.email" 
            type="email" 
            required 
            placeholder="your@email.com"
          />
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
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['close'])
const authStore = useAuthStore()

const activeTab = ref('login')
const loading = ref(false)
const error = ref('')

const loginForm = reactive({
  email: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password2: ''
})

async function handleLogin() {
  error.value = ''
  loading.value = true
  
  try {
    const result = await authStore.login(loginForm.email, loginForm.password)
    if (result.success) {
      emit('close')
    } else {
      error.value = result.error
    }
  } catch (err) {
    error.value = 'Ошибка соединения с сервером'
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
  
  loading.value = true
  
  try {
    const result = await authStore.register(
      registerForm.username,
      registerForm.email,
      registerForm.password,
      registerForm.password2
    )
    
    if (result.success) {
      emit('close')
    } else {
      error.value = typeof result.error === 'object' 
        ? Object.values(result.error).flat().join(', ')
        : result.error
    }
  } catch (err) {
    error.value = 'Ошибка соединения с сервером'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  backdrop-filter: blur(4px);
}

.auth-modal {
  background: white;
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 420px;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.auth-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.auth-tabs button {
  flex: 1;
  padding: 10px;
  border: none;
  background: #f5f5f5;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.auth-tabs button.active {
  background: #c9a9e8;
  color: white;
}

.auth-form h2 {
  margin: 0 0 20px 0;
  font-size: 24px;
  color: #333;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.error-message {
  color: #dc3545;
  background: #fee;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #c9a9e8;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 8px;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>