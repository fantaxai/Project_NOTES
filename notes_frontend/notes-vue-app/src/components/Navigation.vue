<template>
  <nav v-if="!isAuthPage" class="main-nav">
    <div class="nav-container">
      <div class="nav-left">
        <router-link to="/notes" class="nav-brand">💭 Копилка идей</router-link>
      </div>

      <div class="nav-center">
        <router-link to="/notes" class="nav-link" active-class="active">
          Все идеи
          <span v-if="totalCount > 0" class="nav-count">{{ totalCount }}</span>
        </router-link>
        <router-link to="/create" class="nav-link" active-class="active">
          <span class="btn-icon">+</span>
          Новая идея
        </router-link>
        <button class="nav-link" title="Сгенерировать чеклист" @click="generateChecklist">
          <span class="btn-icon">📋</span>
          Чеклист
        </button>
      </div>

      <div class="nav-right">
        <div class="user-info">
          <div class="user-avatar">
            {{ authStore.user?.username?.[0]?.toUpperCase() || '?' }}
          </div>
          <span class="user-name">{{ authStore.user?.username || 'Пользователь' }}</span>
          <button class="logout-btn" title="Выйти" @click="handleLogout">Выйти</button>
        </div>
        <button class="settings-btn" title="Настройки" @click="openSettings">⚙️</button>
      </div>
    </div>

    <SettingsModal v-if="showSettings" @close="showSettings = false" />
    <CheckList
      v-if="showCheckList"
      @close="showCheckList = false"
      @generate="handleGenerateChecklist"
    />
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNoteListStore } from '../stores/notelist'
import { useAuthStore } from '../stores/auth'
import SettingsModal from './SettingsModal.vue'
import CheckList from './CheckList.vue'
import { useChecklistStore } from '../stores/checklist'
import { useRouter, useRoute } from 'vue-router'

const noteListStore = useNoteListStore()
const authStore = useAuthStore()
const checklistStore = useChecklistStore()
const router = useRouter()
const route = useRoute()
const isAuthPage = computed(() => route.path === '/auth')

const showSettings = ref(false)
const showCheckList = ref(false)
const totalCount = computed(() => noteListStore.totalCount)

const openSettings = () => { showSettings.value = true }
const generateChecklist = () => { showCheckList.value = true }

const handleLogout = async () => {
  await authStore.logout()
  router.push('/auth')
}

const handleGenerateChecklist = async (config) => {
  try {
    await checklistStore.generateChecklist({
      amount_of_ideas: config.amount_of_ideas,
      categories: config.categories,
    })
    showCheckList.value = false
  } catch (err) {
    alert('Ошибка генерации: ' + (err.response?.data?.error || err.message))
  }
}
</script>

<style scoped>
.main-nav {
  background: var(--bg-primary, white);
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-brand {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary-color, #c9a9e8);
  text-decoration: none;
  white-space: nowrap;
}
.nav-brand:hover { opacity: 0.8; }

.nav-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Все три кнопки — одинаковый стиль как у Чеклиста */
.nav-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;

  /* Стиль как у Чеклиста: светлый фон + фиолетовая обводка */
  background: var(--primary-light, #f0e6ff);
  color: var(--primary-color, #c9a9e8);
  border: 1px solid var(--primary-color, #c9a9e8);
}

.nav-link:hover {
  background: var(--primary-color, #c9a9e8);
  color: white;
}

/* Активная кнопка — залитая */
.nav-link.active {
  background: var(--primary-color, #c9a9e8);
  color: white;
  border-color: var(--primary-color, #c9a9e8);
}

.nav-count {
  background: rgba(255, 255, 255, 0.4);
  color: inherit;
  padding: 2px 7px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.nav-link.active .nav-count {
  background: rgba(255,255,255,0.3);
}

.btn-icon {
  font-size: 16px;
  font-weight: 600;
  line-height: 1;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 30px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-color, #c9a9e8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #333);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  padding: 4px 12px;
  background: none;
  border: 1px solid var(--danger-color, #dc3545);
  color: var(--danger-color, #dc3545);
  border-radius: 16px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}
.logout-btn:hover { background: var(--danger-bg, #fee); }

.settings-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary, #333);
}
.settings-btn:hover { background: var(--hover-bg, #f5f5f5); }

@media (max-width: 768px) {
  .nav-container {
    flex-wrap: wrap;
    height: auto;
    padding: 12px 16px;
    gap: 12px;
  }
  .nav-center {
    order: 3;
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  .nav-link {
    flex: 1;
    min-width: 90px;
    justify-content: center;
  }
  .user-info { padding: 4px 6px; }
  .user-name { display: none; }
}
</style>
