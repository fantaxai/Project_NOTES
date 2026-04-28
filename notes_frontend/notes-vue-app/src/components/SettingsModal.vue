<template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Настройки</h3>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="settings-content">
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
import { useSettingsStore } from '../stores/settings'

const emit = defineEmits(['close'])
const settingsStore = useSettingsStore()

const setTheme = (theme) => {
  settingsStore.setTheme(theme)
}

const close = () => {
  emit('close')
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
  min-width: 400px;
  max-width: 90%;
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

.about-info {
  color: var(--text-secondary, #666);
  line-height: 1.6;
}

.about-info p {
  margin: 8px 0;
}
</style>
