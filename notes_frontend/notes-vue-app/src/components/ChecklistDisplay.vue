<template>
  <div class="checklist-display checklist-root">
    <div v-if="checklistStore.loading" class="checklist-loading">
      <div class="spinner-small"></div>
      <span>Загрузка...</span>
    </div>

    <div v-else-if="!checklistStore.currentChecklist" class="checklist-empty">
      <span class="empty-icon">📝</span>
      <p class="empty-text">Здесь будет ваш чеклист</p>
      <p class="empty-hint">Нажмите "Чеклист" в меню, чтобы сгенерировать</p>
    </div>

    <div v-else class="checklist-content">
      <div class="checklist-header">
        <div class="checklist-title-row">
          <span class="checklist-icon">📋</span>
          <h3 class="checklist-title">Чеклист</h3>
          <button
            class="checklist-action-btn"
            title="Выбрать чеклист"
            @click.stop="showListModal = true"
          >
            📋
          </button>
        </div>
        <div class="checklist-meta">
          <span class="checklist-date">{{
            formatDate(checklistStore.currentChecklist.creation_date)
          }}</span>
          <span class="checklist-divider">·</span>
          <span class="checklist-count"
            >{{ checklistStore.currentChecklist.items?.length || 0 }} идей</span
          >
        </div>
      </div>
      <div v-if="checklistStore.currentChecklist.items?.length" class="checklist-items">
        <div
          v-for="item in checklistStore.currentChecklist.items"
          :key="item.id"
          class="checklist-item"
          :class="{ completed: item.completed }"
          @click="toggleItem(item)"
        >
          <div class="item-checkbox">
            <span v-if="item.completed" class="checkbox-done">☑</span>
            <span v-else class="checkbox-todo">☐</span>
          </div>
          <div class="item-content">
            <p class="item-text">{{ item.idea_text }}</p>
            <span class="item-category">{{ item.category_display }}</span>
          </div>
        </div>
      </div>
      <div v-else class="checklist-empty-list">
        <p>Нет пунктов в чеклисте</p>
      </div>
    </div>

    <!-- Модальное окно: список всех чеклистов -->
    <div v-if="showListModal" class="modal-overlay" @click="showListModal = false">
      <div class="modal-content modal-list" @click.stop>
        <div class="modal-header">
          <h3>📋 Все чеклисты</h3>
          <button class="close-btn" @click="showListModal = false">×</button>
        </div>

        <div v-if="checklistsLoading" class="checklist-loading">
          <span>Загрузка...</span>
        </div>

        <div v-else-if="checklistStore.checklists.length === 0" class="empty-list">
          <p>Нет чеклистов</p>
        </div>

        <div v-else class="checklist-list">
          <div
            v-for="checklist in checklistStore.checklists"
            :key="checklist.id"
            class="checklist-list-item"
            :class="{ active: checklistStore.currentChecklist?.id === checklist.id }"
          >
            <div class="checklist-list-info" @click="selectChecklist(checklist)">
              <span class="checklist-list-date">{{ formatDate(checklist.creation_date) }}</span>
              <span class="checklist-list-count">{{ checklist.items?.length || 0 }} идей</span>
              <span v-if="checklistStore.currentChecklist?.id === checklist.id" class="active-badge"
                >текущий</span
              >
            </div>
            <div class="checklist-list-actions">
              <button
                class="list-action-btn"
                title="Просмотреть"
                @click.stop="previewChecklist(checklist)"
              >
                🔍
              </button>
              <button
                class="list-action-btn delete-action"
                title="Удалить"
                @click.stop="deleteChecklist(checklist)"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно: просмотр одного чеклиста -->
    <div
      v-if="showPreviewModal && previewChecklistData"
      class="modal-overlay"
      @click="showPreviewModal = false"
    >
      <div class="modal-content modal-preview" @click.stop>
        <div class="modal-header modal-header-fixed">
          <h3>📋 Чеклист от {{ formatDate(previewChecklistData.creation_date) }}</h3>
          <button class="close-btn" @click="showPreviewModal = false">×</button>
        </div>

        <div class="modal-body-scroll">
          <div v-if="previewChecklistData.items?.length" class="preview-items">
            <div
              v-for="item in previewChecklistData.items"
              :key="item.id"
              class="preview-item"
              :class="{ completed: item.completed }"
            >
              <div class="preview-checkbox">
                <span v-if="item.completed">✅</span>
                <span v-else>⬜</span>
              </div>
              <div class="preview-item-content">
                <p class="preview-item-text">{{ item.idea_text }}</p>
                <span class="preview-item-category">{{ item.category_display }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-list">
            <p>Нет пунктов в чеклисте</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useChecklistStore } from '../stores/checklist'

const checklistStore = useChecklistStore()
const showListModal = ref(false)
const showPreviewModal = ref(false)
const previewChecklistData = ref(null)
const checklistsLoading = ref(false)

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

const toggleItem = async (item) => {
  if (!checklistStore.currentChecklist?.id) return
  try {
    await checklistStore.toggleItem(checklistStore.currentChecklist.id, item.id)
  } catch (err) {
    console.error('Ошибка переключения пункта:', err)
  }
}

const selectChecklist = (checklist) => {
  checklistStore.selectChecklist(checklist)
  showListModal.value = false
  showPreviewModal.value = false
}

const previewChecklist = (checklist) => {
  previewChecklistData.value = JSON.parse(JSON.stringify(checklist))
  showPreviewModal.value = true
}

const deleteChecklist = async (checklist) => {
  if (!confirm(`Удалить чеклист от ${formatDate(checklist.creation_date)}?`)) return
  try {
    await checklistStore.deleteChecklist(checklist.id)
    if (previewChecklistData.value?.id === checklist.id) {
      showPreviewModal.value = false
      previewChecklistData.value = null
    }
  } catch (err) {
    alert('Ошибка удаления чеклиста')
  }
}

onMounted(async () => {
  checklistsLoading.value = true
  await checklistStore.fetchChecklists()
  checklistsLoading.value = false
})
</script>

<style scoped>
.checklist-display {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.checklist-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  color: var(--text-secondary, #666);
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-light, #f3f3f3);
  border-top: 2px solid var(--primary-color, #c9a9e8);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.checklist-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
  color: var(--text-secondary, #666);
}

.empty-icon {
  font-size: 40px;
  opacity: 0.5;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 6px 0;
  color: var(--text-primary, #333);
}

.empty-hint {
  font-size: 12px;
  margin: 0;
  color: var(--text-tertiary, #999);
}

.checklist-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.checklist-header {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  flex-shrink: 0;
}

.checklist-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.checklist-icon {
  font-size: 16px;
}

.checklist-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
}

.checklist-action-btn {
  margin-left: auto;
  background: none;
  border: 1px solid var(--border-color, #e0e0e0);
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  opacity: 0.7;
}

.checklist-action-btn:hover {
  opacity: 1;
  background: var(--hover-bg, #f5f5f5);
}

.checklist-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

.checklist-date {
  color: var(--text-secondary, #666);
  font-weight: 500;
}

.checklist-divider {
  color: var(--text-tertiary, #999);
  font-size: 14px;
}

.checklist-count {
  color: var(--text-tertiary, #999);
}

.checklist-items {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 0;
  padding-right: 4px;
}

.checklist-items::-webkit-scrollbar {
  width: 5px;
}

.checklist-items::-webkit-scrollbar-track {
  background: transparent;
}

.checklist-items::-webkit-scrollbar-thumb {
  background: var(--primary-color, #c9a9e8);
  border-radius: 3px;
}

.checklist-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px;
  background: var(--bg-tertiary, #f8f9fa);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.checklist-item:hover {
  background: var(--hover-bg, #e9ecef);
}

.checklist-item.completed {
  opacity: 0.7;
}

.checklist-item.completed .item-text {
  text-decoration: line-through;
  color: var(--text-tertiary, #999);
}

.item-checkbox {
  font-size: 18px;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-text {
  margin: 0 0 3px 0;
  font-size: 13px;
  line-height: 1.3;
  color: var(--text-primary, #333);
  word-break: break-word;
}

.item-category {
  font-size: 10px;
  color: var(--primary-color, #c9a9e8);
  background: var(--primary-light, #f0e6ff);
  padding: 1px 6px;
  border-radius: 10px;
}

.checklist-empty-list {
  padding: 20px;
  text-align: center;
  color: var(--text-tertiary, #999);
}

/* Модальные окна */
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
  z-index: 3000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-primary, white);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--border-color, transparent);
}

.modal-list {
  width: 450px;
}

.modal-preview {
  width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Фиксированная шапка */
.modal-header-fixed {
  flex-shrink: 0;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  background: var(--bg-primary, white);
  border-radius: 16px 16px 0 0;
  z-index: 1;
}

/* Прокручиваемое тело */
.modal-body-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-top: 16px;
  min-height: 0;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.modal-body-scroll::-webkit-scrollbar {
  width: 6px;
}

.modal-body-scroll::-webkit-scrollbar-track {
  background: transparent;
  margin: 4px 0;
}

.modal-body-scroll::-webkit-scrollbar-thumb {
  background: var(--primary-color, #c9a9e8);
  border-radius: 3px;
}

.modal-body-scroll::-webkit-scrollbar-thumb:hover {
  background: var(--primary-hover, #b794d4);
}

.modal-body-scroll {
  scrollbar-width: thin;
  scrollbar-color: var(--primary-color, #c9a9e8) transparent;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header-fixed h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary, #333);
}

.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: var(--text-secondary, #666);
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--hover-bg, #f0f0f0);
}

.empty-list {
  padding: 30px;
  text-align: center;
  color: var(--text-tertiary, #999);
}

/* Список чеклистов */
.checklist-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checklist-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: var(--bg-tertiary, #f8f9fa);
  border-radius: 10px;
  border: 2px solid transparent;
}

.checklist-list-item.active {
  border-color: var(--primary-color, #c9a9e8);
  background: var(--primary-light, #f0e6ff);
}

.checklist-list-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  cursor: pointer;
}

.checklist-list-date {
  font-weight: 500;
  color: var(--text-primary, #333);
  font-size: 14px;
}

.checklist-list-count {
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

.active-badge {
  font-size: 10px;
  background: var(--primary-color, #c9a9e8);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
}

.checklist-list-actions {
  display: flex;
  gap: 4px;
}

.list-action-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 6px;
  opacity: 0.6;
  transition: all 0.2s;
}

.list-action-btn:hover {
  opacity: 1;
  background: var(--hover-bg, #e9ecef);
}

.delete-action:hover {
  background: var(--danger-bg, #fee);
}

/* Просмотр чеклиста */
.preview-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 8px;
  transform: translateZ(0);
  will-change: transform;
}

.preview-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-tertiary, #f8f9fa);
  border-radius: 10px;
  border: 1px solid var(--border-color, #e0e0e0);
  transition: background-color 0.2s ease;
}

.preview-item:hover {
  background: var(--hover-bg, #e9ecef);
}

.preview-item.completed {
  opacity: 0.7;
}

.preview-item.completed .preview-item-text {
  text-decoration: line-through;
  color: var(--text-tertiary, #999);
}

.preview-checkbox {
  font-size: 22px;
  flex-shrink: 0;
  margin-top: 2px;
  user-select: none;
}

.preview-item-content {
  flex: 1;
  min-width: 0;
}

.preview-item-text {
  margin: 0 0 4px 0;
  font-size: 16px;
  line-height: 1.5;
  color: var(--text-primary, #222);
  font-weight: 500;
  word-break: break-word;
}

.preview-item-category {
  display: inline-block;
  font-size: 12px;
  color: var(--primary-color, #5700b3);
  background: var(--primary-light, #f0e6ff);
  padding: 3px 12px;
  border-radius: 12px;
  font-weight: 500;
}
</style>
