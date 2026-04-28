<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ isEditing ? 'Редактировать тег' : 'Новый тег' }}</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="tagName">Название тега</label>
          <input
            id="tagName"
            v-model="tagName"
            type="text"
            placeholder="Введите название тега"
            class="tag-input"
            autofocus
            required
          />
        </div>

        <div class="form-group">
          <label for="tagColor">Цвет тега</label>
          <div class="color-picker-container">
            <input id="tagColor" v-model="tagColor" type="color" class="color-input" />
            <input
              v-model="tagColor"
              type="text"
              placeholder="#RRGGBB"
              class="color-text"
              pattern="^#[0-9A-Fa-f]{6}$"
            />
          </div>
          <div class="color-presets">
            <button
              v-for="color in presetColors"
              :key="color"
              type="button"
              class="color-preset"
              :style="{ backgroundColor: color }"
              @click="tagColor = color"
            ></button>
          </div>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="modal-actions">
          <button type="button" class="cancel-btn" @click="handleClose">Отмена</button>
          <button type="submit" :disabled="!tagName.trim() || loading" class="save-btn">
            {{ loading ? 'Сохранение...' : isEditing ? 'Сохранить' : 'Создать' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  tag: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['close', 'save'])

const tagName = ref('')
const tagColor = ref('#C9A9E8')
const isEditing = ref(false)

const presetColors = [
  '#FFB3B3', // Пастельный красный (нежно-розовый)
  '#FFD6A5', // Пастельный оранжевый (персиковый)
  '#FDFFB6', // Пастельный желтый (лимонный крем)
  '#CAFFBF', // Пастельный зеленый (мятный)
  '#9BF6FF', // Пастельный голубой (небесный)
  '#A0C4FF', // Пастельный синий (васильковый)
  '#BDB2FF', // Пастельный фиолетовый (лавандовый)
  '#FFC6FF', // Пастельный розовый (розовое облако)
  '#E4C1F9', // Пастельный пурпурный (сиреневый)
  '#D8E2DC', // Пастельный серо-зеленый (шалфей)
  '#FDE2E4', // Пастельный румянец
  '#FAD2E1', // Пастельный персиковый
]

watch(
  () => props.tag,
  (newTag) => {
    if (newTag) {
      tagName.value = newTag.name || ''
      tagColor.value = newTag.color || '#C9A9E8'
      isEditing.value = true
    } else {
      tagName.value = ''
      tagColor.value = '#C9A9E8'
      isEditing.value = false
    }
  },
  { immediate: true }
)

const handleSubmit = () => {
  if (tagName.value.trim()) {
    emit('save', {
      name: tagName.value.trim(),
      color: tagColor.value,
      id: props.tag?.id,
    })
  }
}

const handleClose = () => {
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
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  min-width: 400px;
  max-width: 90%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
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
  background: #f0f0f0;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.tag-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.tag-input:focus {
  outline: none;
  border-color: #c9a9e8;
}

.color-picker-container {
  display: flex;
  gap: 12px;
  align-items: center;
}

.color-input {
  width: 60px;
  height: 40px;
  padding: 4px;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
}

.color-text {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: monospace;
  text-transform: uppercase;
}

.color-presets {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin-top: 12px;
}

.color-preset {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.color-preset:hover {
  transform: scale(1.1);
  border-color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn,
.save-btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.save-btn {
  background: #c9a9e8;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #b794d4;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .modal-content {
    min-width: auto;
    width: 95%;
    padding: 20px;
  }

  .color-presets {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
