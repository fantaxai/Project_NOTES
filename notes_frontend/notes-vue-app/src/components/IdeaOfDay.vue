<template>
  <div class="idea-of-day-container">
    <!-- Загрузка -->
    <div v-if="loading" class="idea-loading">
      <div class="spinner-small"></div>
      <span>Загрузка идеи дня...</span>
    </div>

    <!-- Ошибка (нет кандидатов) -->
    <div v-else-if="!loading && !currentIdea?.note" class="idea-empty">
      <div class="idea-badge">
        <span class="idea-icon">💡</span>
        <span class="idea-label">Идея дня</span>
      </div>
      <div class="empty-content">
        <p class="empty-message">Модуль «Идея дня» работает от 20 заметок-кандидатов</p>
        <p class="empty-hint">
          Создайте заметки с отметкой 💡, чтобы увидеть здесь идею дня
          <br />Сейчас кандидатов: {{ totalCandidates }}
        </p>
        <button v-if="error" class="retry-link" @click="retry">Повторить</button>
      </div>
    </div>

    <!-- Идея дня (есть заметка) -->
    <div v-else-if="currentIdea?.note" class="idea-of-day" @click="goToIdea">
      <div class="idea-badge">
        <span class="idea-icon">💡</span>
        <span class="idea-label">Идея дня</span>
      </div>

      <div class="idea-content">
        <div class="idea-title-row">
          <h3 class="idea-title">{{ currentIdea.note.title }}</h3>
        </div>
        <!-- idea-preview УДАЛИТЬ отсюда -->

        <div class="idea-footer">
          <div v-if="currentIdea.note.tags?.length" class="idea-tags">
            <span
              v-for="tag in currentIdea.note.tags.slice(0, 3)"
              :key="tag.id"
              class="idea-tag"
              :style="{ backgroundColor: tag.color + '20', color: tag.color }"
            >
              #{{ tag.name }}
            </span>
            <span v-if="currentIdea.note.tags.length > 3" class="more-tags">
              +{{ currentIdea.note.tags.length - 3 }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useIdeaStore } from '../stores/ideas'

const router = useRouter()
const ideaStore = useIdeaStore()

const currentIdea = computed(() => ideaStore.currentIdea)
const loading = computed(() => ideaStore.loading)
const error = computed(() => ideaStore.error)
const totalCandidates = computed(() => ideaStore.totalCandidates)

const goToIdea = () => {
  if (currentIdea.value?.note?.id) {
    ideaStore.markAsShown(currentIdea.value.note.id)
    router.push(`/note/${currentIdea.value.note.id}`)
  }
}

const retry = async () => {
  await ideaStore.fetchIdeaOfDay()
}

onMounted(async () => {
  await ideaStore.fetchIdeaOfDay()
})
</script>

<style scoped>
.idea-of-day-container {
  margin: 0;
  height: 100%;
  position: relative;
  z-index: 1;
}

.idea-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px;
  background: white;
  border-radius: 16px;
  color: #666;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #c9a9e8;
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

/* Компактная версия идеи дня */
.idea-of-day {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 10px 16px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center; /* иконка и текст на одной оси */
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.idea-of-day::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s;
}

.idea-of-day:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.idea-of-day:hover::before {
  opacity: 1;
}

/* Пустое состояние - компактное */
.idea-empty {
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  border-radius: 16px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: auto;
}

.empty-content {
  flex: 1;
}

.idea-badge {
  display: flex;
  flex-direction: row; /* иконка + подпись в строку */
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  flex-shrink: 0;
}

.idea-icon {
  font-size: 20px;
}

.idea-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.idea-content {
  flex: 1;
  min-width: 0;
}

.idea-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.3;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.idea-preview {
  margin: 0 0 8px 0;
  font-size: 12px;
  opacity: 0.85;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: rgba(255, 255, 255, 0.9);
}

.idea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.idea-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.idea-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
}

.more-tags {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
}

.idea-progress {
  display: flex;
  align-items: center;
  gap: 6px;
}

.progress-text {
  font-size: 10px;
  opacity: 0.8;
  min-width: 40px;
}

.progress-bar {
  width: 50px;
  height: 3px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: white;
  border-radius: 2px;
  transition: width 0.3s;
}

.empty-message {
  margin: 0 0 4px 0;
  font-size: 13px;
  font-weight: 500;
  color: #555;
}

.empty-hint {
  margin: 0;
  font-size: 11px;
  color: #888;
  line-height: 1.4;
}

.retry-link {
  background: none;
  border: none;
  color: #c9a9e8;
  cursor: pointer;
  text-decoration: underline;
  font-size: 12px;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .idea-of-day-container {
    margin: 0;
  }

  .idea-of-day {
    padding: 10px 12px;
    gap: 10px;
  }

  .idea-empty {
    padding: 10px 12px;
    gap: 10px;
  }

  .idea-badge {
    padding: 6px 8px;
  }

  .idea-icon {
    font-size: 20px;
  }

  .idea-label {
    font-size: 9px;
  }

  .idea-title {
    font-size: 14px;
  }

  .idea-preview {
    font-size: 11px;
    -webkit-line-clamp: 1;
  }

  .idea-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
