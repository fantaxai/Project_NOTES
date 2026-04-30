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
        <p class="empty-message">
          Модуль «Идея дня» работает от 20 заметок-кандидатов
        </p>
        <p class="empty-hint">
          Создайте заметки с отметкой 💡, чтобы увидеть здесь идею дня
          <br>Сейчас кандидатов: {{ totalCandidates }}
        </p>
        <button v-if="error" @click="retry" class="retry-link">Повторить</button>
      </div>
    </div>

    <!-- Идея дня (есть заметка) -->
    <div v-else-if="currentIdea?.note" class="idea-of-day" @click="goToIdea">
      <div class="idea-badge">
        <span class="idea-icon">💡</span>
        <span class="idea-label">Идея дня</span>
      </div>

      <div class="idea-content">
        <h3 class="idea-title">{{ currentIdea.note.title }}</h3>
        <p class="idea-preview">{{ getPreview(currentIdea.note.content) }}</p>

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

          <div v-if="totalCandidates >= 20" class="idea-progress">
            <span class="progress-text">{{ shownCount }} / {{ totalCandidates }}</span>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${(shownCount / totalCandidates) * 100}%` }"
              ></div>
            </div>
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
const shownCount = computed(() => ideaStore.shownCount)

const getPreview = (content) => {
  if (!content) return 'Нет содержания'
  const plainText = content.replace(/<[^>]*>/g, '')
  return plainText.length > 100 ? plainText.substring(0, 100) + '...' : plainText
}

const goToIdea = () => {
  if (currentIdea.value?.note?.id) {
    // При переходе отмечаем как показанную
    ideaStore.markAsShown(currentIdea.value.note.id)
    router.push(`/note/${currentIdea.value.note.id}`)
  }
}

const resetAndRefresh = async () => {
  await ideaStore.resetShownStatus()
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
  padding: 20px;
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

.idea-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: #fff0f0;
  border-radius: 16px;
  color: #dc3545;
}

.retry-link {
  background: none;
  border: none;
  color: #c9a9e8;
  cursor: pointer;
  text-decoration: underline;
  font-size: 14px;
}

.idea-of-day {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px 24px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
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
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
}

.idea-of-day:hover::before {
  opacity: 1;
}

.idea-empty {
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
  border-radius: 16px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: 80px;
}

.empty-content {
  flex: 1;
}

.idea-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.idea-icon {
  font-size: 32px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.idea-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.9;
}

.idea-content {
  flex: 1;
}

.idea-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  line-height: 1.3;
  color: white;
}

.idea-preview {
  margin: 0 0 12px 0;
  font-size: 14px;
  opacity: 0.9;
  line-height: 1.5;
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
  gap: 12px;
}

.idea-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.idea-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(5px);
}

.more-tags {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.8);
}

.idea-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  opacity: 0.8;
  min-width: 45px;
}

.progress-bar {
  width: 60px;
  height: 4px;
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

.next-idea-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  backdrop-filter: blur(5px);
}

.next-idea-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.empty-message {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: #555;
}

.empty-hint {
  margin: 0;
  font-size: 13px;
  color: #888;
  line-height: 1.5;
}

.reset-link {
  background: none;
  border: none;
  color: #c9a9e8;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .idea-of-day-container {
    margin: 0 16px 20px 16px;
  }

  .idea-of-day {
    flex-direction: column;
    padding: 16px;
  }

  .idea-badge {
    flex-direction: row;
    width: 100%;
    justify-content: center;
  }

  .idea-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
