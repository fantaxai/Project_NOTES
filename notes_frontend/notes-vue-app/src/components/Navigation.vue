<template>
  <nav class="main-nav">
    <div class="nav-container">
      <div class="nav-left">
        <router-link to="/notes" class="nav-brand"> 💭 Копилка идей </router-link>
      </div>

      <div class="nav-center">
        <router-link to="/notes" class="nav-link" active-class="active">
          Все идеи
          <span v-if="totalCount > 0" class="nav-count">{{ totalCount }}</span>
        </router-link>
        <router-link to="/create" class="nav-link nav-primary" active-class="active">
          <span class="plus-icon">+</span>
          Новая идея
        </router-link>
        <button
          class="nav-link nav-secondary"
          title="Сгенерировать чеклист"
          @click="generateChecklist"
        >
          <span class="checklist-icon">📋</span>
          Чеклист
        </button>
      </div>

      <div class="nav-right">
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
import SettingsModal from './SettingsModal.vue'
import CheckList from './CheckList.vue'
import { useChecklistStore } from '../stores/checklist'

const noteListStore = useNoteListStore()
const checklistStore = useChecklistStore()

const showSettings = ref(false)
const showCheckList = ref(false)

const totalCount = computed(() => noteListStore.totalCount)

const openSettings = () => {
  showSettings.value = true
}

const generateChecklist = () => {
  showCheckList.value = true
}

const handleGenerateChecklist = async (config) => {
  console.log('Генерация чеклиста с конфигом:', config)

  try {
    const checklist = await checklistStore.generateChecklist({
      amount_of_ideas: config.amount_of_ideas,
      categories: config.categories,
    })

    console.log('✅ Чеклист создан:', checklist)
    showCheckList.value = false
  } catch (err) {
    console.error('❌ Ошибка генерации:', err)
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

.nav-left,
.nav-center,
.nav-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-brand {
  font-size: 20px;
  font-weight: 600;
  color: var(--primary-color, #c9a9e8);
  text-decoration: none;
  transition: opacity 0.2s;
}

.nav-brand:hover {
  opacity: 0.8;
}

.nav-link {
  color: var(--text-secondary, #666);
  text-decoration: none;
  font-size: 15px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  cursor: pointer;
}

.nav-link:hover {
  background: var(--hover-bg, #f5f5f5);
  color: var(--primary-color, #c9a9e8);
}

.nav-link.active {
  color: var(--primary-color, #c9a9e8);
  background: var(--active-bg, #f0e6ff);
}

.nav-primary {
  background: var(--primary-color, #c9a9e8) !important;
  color: white !important;
}

.nav-primary:hover {
  background: var(--primary-hover, #b794d4) !important;
  color: white !important;
}

.nav-primary.active {
  background: var(--primary-hover, #b794d4) !important;
  color: white !important;
}

.nav-secondary {
  background: var(--primary-light, #f0e6ff);
  color: var(--primary-color, #c9a9e8) !important;
  border: 1px solid var(--primary-color, #c9a9e8);
}

.nav-secondary:hover {
  background: var(--primary-color, #c9a9e8) !important;
  color: white !important;
}

.nav-count {
  background: rgba(201, 169, 232, 0.2);
  color: var(--primary-color, #c9a9e8);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-left: 6px;
}

.plus-icon {
  font-size: 18px;
  font-weight: 600;
}

.checklist-icon {
  font-size: 16px;
}

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

.settings-btn:hover {
  background: var(--hover-bg, #f5f5f5);
}

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
    justify-content: center;
    min-width: 100px;
  }
}
</style>
