<template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>📋 Генерация чеклиста</h3>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="modal-body">
        <!-- Количество идей -->
        <div class="form-group">
          <label for="amount">Количество идей (1-20)</label>
          <div class="amount-control">
            <input
              id="amount"
              v-model.number="amount"
              type="range"
              min="1"
              max="20"
              step="1"
              class="amount-slider"
            />
            <span class="amount-value">{{ amount }}</span>
          </div>
        </div>

        <!-- Выбор категорий -->
        <div class="form-group">
          <label>Категории</label>
          <div class="categories-grid">
            <label v-for="cat in categories" :key="cat.value" class="category-checkbox">
              <input v-model="selectedCategories" type="checkbox" :value="cat.value" />
              <span class="category-label">{{ cat.label }}</span>
            </label>
          </div>
          <button class="select-all-btn" @click="selectAll">Выбрать все</button>
        </div>

        <!-- Режим генерации -->
        <div class="form-group">
          <label>Режим генерации</label>
          <div class="mode-selector">
            <button :class="['mode-option', { active: mode === 'smart' }]" @click="mode = 'smart'">
              <span class="mode-icon">🧠</span>
              <span class="mode-title">Умный подбор</span>
              <span class="mode-desc">70% по интересам + 30% разнообразие</span>
            </button>
            <button
              :class="['mode-option', { active: mode === 'random' }]"
              @click="mode = 'random'"
            >
              <span class="mode-icon">🎲</span>
              <span class="mode-title">Случайный</span>
              <span class="mode-desc">Равномерная выборка из категорий</span>
            </button>
          </div>
        </div>

        <!-- Информация об интересах (только для smart) -->
        <div v-if="mode === 'smart' && userInterests.length > 0" class="interests-info">
          <div class="interests-header">
            <span>🎯 Ваши интересы:</span>
          </div>
          <div class="interests-tags">
            <span
              v-for="(weight, category) in categoryWeights"
              :key="category"
              class="interest-tag"
              :style="{ opacity: Math.min(0.5 + weight / 50, 1) }"
            >
              {{ getCategoryLabel(category) }} ({{ weight }})
            </span>
          </div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="cancel-btn" @click="close">Отмена</button>
        <button :disabled="!canGenerate || loading" class="generate-btn" @click="generate">
          {{ loading ? 'Генерация...' : 'Создать чеклист' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNoteListStore } from '../stores/notelist'

const emit = defineEmits(['close', 'generate'])

const noteListStore = useNoteListStore()

const amount = ref(10)
const mode = ref('smart')
const selectedCategories = ref([])
const loading = ref(false)

const categories = [
  { value: 'study', label: '📚 Учеба' },
  { value: 'travel', label: '✈️ Путешествия' },
  { value: 'art', label: '🎨 Искусство' },
  { value: 'friends', label: '👥 Друзья' },
  { value: 'family', label: '👨‍👩‍👧 Семья' },
  { value: 'sport', label: '🏃 Спорт' },
  { value: 'work', label: '💼 Работа' },
  { value: 'self_development', label: '🌱 Саморазвитие' },
]

// Маппинг тегов на категории
const tagToCategoryMap = {
  работа: ['work'],
  проекты: ['work'],
  карьера: ['work'],
  задачи: ['work'],
  изучить: ['study', 'self_development'],
  обучение: ['study', 'self_development'],
  книги: ['study'],
  курсы: ['study'],
  навыки: ['self_development'],
  идеи: ['art'],
  творчество: ['art'],
  дизайн: ['art'],
  личное: ['friends', 'family'],
  друзья: ['friends'],
  семья: ['family'],
  отношения: ['friends', 'family'],
  спорт: ['sport'],
  здоровье: ['sport'],
  тренировки: ['sport'],
  путешествия: ['travel'],
  поездки: ['travel'],
  отдых: ['travel'],
}

// Веса категорий на основе тегов пользователя
const categoryWeights = computed(() => {
  const weights = {}
  const notes = noteListStore.notes

  // Подсчёт частоты тегов
  const tagFrequency = {}
  notes.forEach((note) => {
    if (note.tags) {
      note.tags.forEach((tag) => {
        const tagLower = tag.name.toLowerCase()
        tagFrequency[tagLower] = (tagFrequency[tagLower] || 0) + 1
      })
    }
  })

  // Преобразование в веса категорий
  Object.entries(tagFrequency).forEach(([tag, count]) => {
    const mappedCategories = tagToCategoryMap[tag] || []
    mappedCategories.forEach((cat) => {
      weights[cat] = (weights[cat] || 0) + count
    })
  })

  return weights
})

// Интересы пользователя для отображения
const userInterests = computed(() => {
  return Object.entries(categoryWeights.value)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
})

const canGenerate = computed(() => {
  return amount.value >= 1 && amount.value <= 20
})

const getCategoryLabel = (value) => {
  return categories.find((c) => c.value === value)?.label || value
}

const selectAll = () => {
  if (selectedCategories.value.length === categories.length) {
    selectedCategories.value = []
  } else {
    selectedCategories.value = categories.map((c) => c.value)
  }
}

const generate = async () => {
  loading.value = true

  const config = {
    amount_of_ideas: amount.value,
    categories: selectedCategories.value.length > 0 ? selectedCategories.value : null,
    mode: mode.value,
    category_weights: mode.value === 'smart' ? categoryWeights.value : null,
  }

  emit('generate', config)
}

const close = () => {
  emit('close')
}

onMounted(() => {
  // По умолчанию выбираем все категории
  selectedCategories.value = categories.map((c) => c.value)
})
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
  border-radius: 20px;
  padding: 24px;
  min-width: 500px;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
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
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--hover-bg, #f0f0f0);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary, #333);
}

.amount-control {
  display: flex;
  align-items: center;
  gap: 16px;
}

.amount-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--border-color, #e0e0e0);
  -webkit-appearance: none;
  appearance: none;
}

.amount-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color, #c9a9e8);
  cursor: pointer;
}

.amount-value {
  min-width: 40px;
  text-align: center;
  font-weight: 600;
  color: var(--primary-color, #c9a9e8);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.category-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-tertiary, #f8f9fa);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.category-checkbox:hover {
  background: var(--hover-bg, #e9ecef);
}

.category-checkbox input {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color, #c9a9e8);
}

.select-all-btn {
  margin-top: 8px;
  padding: 8px 16px;
  background: none;
  border: 1px solid var(--primary-color, #c9a9e8);
  border-radius: 8px;
  color: var(--primary-color, #c9a9e8);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.select-all-btn:hover {
  background: var(--primary-light, #f0e6ff);
}

.mode-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mode-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--bg-tertiary, #f8f9fa);
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.mode-option:hover {
  background: var(--hover-bg, #e9ecef);
}

.mode-option.active {
  border-color: var(--primary-color, #c9a9e8);
  background: var(--primary-light, #f0e6ff);
}

.mode-icon {
  font-size: 28px;
}

.mode-title {
  font-weight: 600;
  color: var(--text-primary, #333);
}

.mode-desc {
  font-size: 13px;
  color: var(--text-secondary, #666);
  margin-left: auto;
}

.interests-info {
  padding: 16px;
  background: linear-gradient(135deg, #f0e6ff 0%, #e8d5f5 100%);
  border-radius: 12px;
}

.interests-header {
  font-weight: 600;
  margin-bottom: 10px;
  color: var(--primary-color, #5700b3);
}

.interests-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.interest-tag {
  padding: 6px 14px;
  background: white;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--primary-color, #5700b3);
  border: 1px solid var(--primary-color, #c9a9e8);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color, #e0e0e0);
}

.cancel-btn,
.generate-btn {
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: var(--bg-tertiary, #f5f5f5);
  border: none;
  color: var(--text-secondary, #666);
}

.cancel-btn:hover {
  background: var(--border-color, #e0e0e0);
}

.generate-btn {
  background: var(--primary-color, #c9a9e8);
  border: none;
  color: white;
}

.generate-btn:hover:not(:disabled) {
  background: var(--primary-hover, #b794d4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(201, 169, 232, 0.3);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
