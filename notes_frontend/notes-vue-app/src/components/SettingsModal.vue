<template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Настройки</h3>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="settings-content">
        <!-- Секция аккаунта -->
        <div class="setting-group">
          <h4>Аккаунт</h4>
          
          <!-- Авторизованный пользователь -->
          <div v-if="authStore.isAuthenticated" class="user-profile">
            <div class="user-avatar">
              {{ authStore.user?.username?.[0]?.toUpperCase() || '?' }}
            </div>
            <div class="user-details">
              <span class="user-name">{{ authStore.user?.username }}</span>
              <span class="user-email">{{ authStore.user?.email }}</span>
            </div>
            <button class="logout-btn" @click="handleLogout" :disabled="loggingOut">
              {{ loggingOut ? 'Выход...' : 'Выйти' }}
            </button>
          </div>

          <!-- Неавторизованный пользователь -->
          <div v-else class="auth-section">
            <p class="auth-hint">
              Войдите или создайте аккаунт для синхронизации ваших идей между устройствами
            </p>
            
            <!-- Табы -->
            <div class="auth-tabs">
              <button 
                :class="{ active: activeTab === 'login' }"
                @click="switchTab('login')"
              >
                Вход
              </button>
              <button 
                :class="{ active: activeTab === 'register' }"
                @click="switchTab('register')"
              >
                Регистрация
              </button>
            </div>

            <!-- Форма входа -->
            <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
              <div class="form-group">
                <label for="login-email">Email</label>
                <input 
                  id="login-email"
                  v-model="loginForm.email" 
                  type="email" 
                  required 
                  placeholder="your@email.com"
                  autocomplete="email"
                />
              </div>
              
              <div class="form-group">
                <label for="login-password">Пароль</label>
                <input 
                  id="login-password"
                  v-model="loginForm.password" 
                  type="password" 
                  required 
                  placeholder="Введите пароль"
                  autocomplete="current-password"
                />
              </div>
              
              <div v-if="error" class="error-message">{{ error }}</div>
              
              <button type="submit" class="auth-submit-btn" :disabled="loading">
                {{ loading ? 'Вход...' : 'Войти' }}
              </button>
            </form>

            <!-- Форма регистрации -->
            <form v-else @submit.prevent="handleRegister" class="auth-form">
              <div class="form-group">
                <label for="reg-username">Имя пользователя</label>
                <input 
                  id="reg-username"
                  v-model="registerForm.username" 
                  type="text" 
                  required 
                  placeholder="Придумайте имя"
                  autocomplete="username"
                />
              </div>
              
              <div class="form-group">
                <label for="reg-email">Email</label>
                <input 
                  id="reg-email"
                  v-model="registerForm.email" 
                  type="email" 
                  required 
                  placeholder="your@email.com"
                  autocomplete="email"
                />
              </div>
              
              <div class="form-group">
                <label for="reg-password">Пароль</label>
                <input 
                  id="reg-password"
                  v-model="registerForm.password" 
                  type="password" 
                  required 
                  placeholder="Минимум 8 символов"
                  autocomplete="new-password"
                />
              </div>
              
              <div class="form-group">
                <label for="reg-password2">Подтвердите пароль</label>
                <input 
                  id="reg-password2"
                  v-model="registerForm.password2" 
                  type="password" 
                  required 
                  placeholder="Повторите пароль"
                  autocomplete="new-password"
                />
              </div>
              
              <div v-if="error" class="error-message">{{ error }}</div>
              
              <button type="submit" class="auth-submit-btn" :disabled="loading">
                {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
              </button>
            </form>
          </div>
        </div>

        <!-- Секция внешнего вида -->
        <div class="setting-group">
          <h4>Внешний вид</h4>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Тема оформления</span>
            </div>
            <div class="theme-selector">
              <button
                :class="['theme-option', { active: settingsStore.theme === 'light' }]"
                @click="setTheme('light')"
              >
                <span class="theme-icon">☀️</span>
                <span>Светлая</span>
              </button>
              <button
                :class="['theme-option', { active: settingsStore.theme === 'dark' }]"
                @click="setTheme('dark')"
              >
                <span class="theme-icon">🌙</span>
                <span>Темная</span>
              </button>
            </div>
          </div>
        </div>

        <!-- О приложении -->
        <div class="setting-group">
          <h4>О приложении</h4>
          <div class="about-info">
            <p><strong>Копилка идей</strong> v1.0.0</p>
            <p>Приложение для сохранения и организации ваших идей</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useSettingsStore } from '../stores/settings'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['close'])
const settingsStore = useSettingsStore()
const authStore = useAuthStore()

// Состояние форм
const activeTab = ref('login')
const loading = ref(false)
const loggingOut = ref(false)
const error = ref('')

// Форма входа
const loginForm = reactive({
  email: '',
  password: ''
})

// Форма регистрации
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password2: ''
})

function switchTab(tab) {
  activeTab.value = tab
  error.value = ''
}

function setTheme(theme) {
  settingsStore.setTheme(theme)
}

function close() {
  emit('close')
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  
  try {
    const result = await authStore.login(loginForm.email, loginForm.password)
    if (result.success) {
      loginForm.email = ''
      loginForm.password = ''
      close()
    } else {
      error.value = result.error
    }
  } catch (err) {
    error.value = 'Ошибка соединения с сервером'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  
  // Валидация
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
    const result = await authStore.register(
      registerForm.username,
      registerForm.email,
      registerForm.password,
      registerForm.password2
    )
    
    if (result.success) {
      registerForm.username = ''
      registerForm.email = ''
      registerForm.password = ''
      registerForm.password2 = ''
      close()
    } else {
      // Обработка разных форматов ошибок от сервера
      if (typeof result.error === 'object') {
        const messages = []
        for (const [key, value] of Object.entries(result.error)) {
          if (Array.isArray(value)) {
            messages.push(...value)
          } else {
            messages.push(value)
          }
        }
        error.value = messages.join('. ')
      } else {
        error.value = result.error
      }
    }
  } catch (err) {
    error.value = 'Ошибка соединения с сервером'
    console.error('Register error:', err)
  } finally {
    loading.value = false
  }
}

async function handleLogout() {
  loggingOut.value = true
  
  try {
    await authStore.logout()
  } catch (err) {
    console.error('Logout error:', err)
  } finally {
    loggingOut.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-primary, white);
  border-radius: 16px;
  padding: 24px;
  min-width: 420px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--border-color, transparent);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary, #333);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary, #666);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--hover-bg, #f0f0f0);
  color: var(--text-primary, #333);
}

.setting-group {
  margin-bottom: 32px;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-group h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--text-primary, #333);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-label {
  font-weight: 500;
  color: var(--text-primary, #333);
}

/* Профиль пользователя */
.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 12px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--primary-color, #c9a9e8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 600;
  color: var(--text-primary, #333);
  font-size: 16px;
}

.user-email {
  font-size: 13px;
  color: var(--text-secondary, #666);
}

.logout-btn {
  padding: 8px 16px;
  background: var(--bg-primary, white);
  border: 1px solid var(--danger-color, #dc3545);
  color: var(--danger-color, #dc3545);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.logout-btn:hover:not(:disabled) {
  background: var(--danger-bg, #fee);
}

.logout-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Секция авторизации */
.auth-section {
  padding: 0;
}

.auth-hint {
  margin: 0 0 16px 0;
  color: var(--text-secondary, #666);
  font-size: 14px;
  line-height: 1.5;
}

.auth-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.auth-tabs button {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--border-color, #e0e0e0);
  background: var(--bg-primary, white);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  color: var(--text-secondary, #666);
}

.auth-tabs button:hover {
  border-color: var(--primary-color, #c9a9e8);
  color: var(--primary-color, #c9a9e8);
}

.auth-tabs button.active {
  background: var(--primary-color, #c9a9e8);
  border-color: var(--primary-color, #c9a9e8);
  color: white;
}

.auth-form {
  margin-top: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--text-primary, #555);
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  background: var(--bg-primary, white);
  color: var(--text-primary, #333);
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color, #c9a9e8);
  box-shadow: 0 0 0 3px rgba(201, 169, 232, 0.1);
}

.form-group input::placeholder {
  color: var(--text-tertiary, #999);
}

.error-message {
  color: var(--danger-color, #dc3545);
  background: var(--danger-bg, #fee);
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  line-height: 1.4;
}

.auth-submit-btn {
  width: 100%;
  padding: 12px;
  background: var(--primary-color, #c9a9e8);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 4px;
}

.auth-submit-btn:hover:not(:disabled) {
  background: var(--primary-hover, #b794d4);
}

.auth-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Тема */
.theme-selector {
  display: flex;
  gap: 8px;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  background: var(--bg-secondary, #f5f5f5);
  border: 2px solid var(--border-color, #e0e0e0);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary, #333);
  min-width: 100px;
}

.theme-option:hover {
  border-color: var(--primary-color, #c9a9e8);
}

.theme-option.active {
  border-color: var(--primary-color, #c9a9e8);
  background: var(--active-bg, #f0e6ff);
}

.theme-icon {
  font-size: 24px;
}

/* О приложении */
.about-info {
  color: var(--text-secondary, #666);
  line-height: 1.6;
}

.about-info p {
  margin: 8px 0;
}

/* Адаптивность */
@media (max-width: 480px) {
  .modal-content {
    min-width: auto;
    width: 95%;
    padding: 20px;
  }
  
  .user-profile {
    flex-wrap: wrap;
  }
  
  .logout-btn {
    width: 100%;
    margin-top: 8px;
  }
}
</style>