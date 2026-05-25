<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ isEditing ? 'Редактировать тег' : 'Новый тег' }}</h3>
        <button type="button" class="close-btn" @click="handleClose">×</button>
      </div>

      <!-- ВАЖНО: убрали <form>, используем div — иначе браузер может триггерить навигацию -->
      <div class="form-body">
        <div class="form-group">
          <label for="tagName">Название тега</label>
          <input
            id="tagName"
            v-model="tagName"
            type="text"
            placeholder="Введите название тега"
            class="tag-input"
            autofocus
            @keydown.enter.prevent="handleSubmit"
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
          <button
            type="button"
            :disabled="!tagName.trim() || loading"
            class="save-btn"
            @click="handleSubmit"
          >
            {{ loading ? 'Сохранение...' : isEditing ? 'Сохранить' : 'Создать' }}
          </button>
        </div>
      </div>
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
  '#FFB3B3',
  '#FFD6A5',
  '#FDFFB6',
  '#CAFFBF',
  '#9BF6FF',
  '#A0C4FF',
  '#BDB2FF',
  '#FFC6FF',
  '#E4C1F9',
  '#D8E2DC',
  '#FDE2E4',
  '#FAD2E1',
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
  if (!tagName.value.trim() || props.loading) return
  emit('save', {
    name: tagName.value.trim(),
    color: tagColor.value,
    id: props.tag?.id,
  })
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
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-primary);
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
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
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
  background: var(--hover-bg);
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.tag-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: border-color 0.2s;
}

.tag-input:focus {
  outline: none;
  border-color: var(--primary-color);
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
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  background: var(--bg-secondary);
}

.color-text {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  font-family: monospace;
  text-transform: uppercase;
  background: var(--bg-secondary);
  color: var(--text-primary);
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
  color: var(--danger-color);
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
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.cancel-btn:hover {
  background: var(--hover-bg);
}

.save-btn {
  background: var(--primary-color);
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: var(--primary-hover);
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

@media (max-width: 768px) {
  .modal-content {
    min-width: auto;
    width: 90%;
    max-width: 90%;
    padding: 20px;
    border-radius: 20px;
  }

  .modal-header h3 {
    font-size: 18px;
  }

  .close-btn {
    width: 28px;
    height: 28px;
    font-size: 20px;
  }

  .form-group {
    margin-bottom: 16px;
  }

  .form-group label {
    font-size: 14px;
    margin-bottom: 6px;
  }

  .tag-input {
    padding: 8px 12px;
    font-size: 13px;
  }

  .color-picker-container {
    gap: 8px;
  }

  .color-input {
    width: 50px;
    height: 36px;
  }

  .color-text {
    padding: 8px 10px;
    font-size: 13px;
  }

  .color-presets {
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;
    margin-top: 10px;
  }

  .modal-actions {
    gap: 10px;
    margin-top: 8px;
  }

  .cancel-btn,
  .save-btn {
    padding: 8px 16px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .modal-overlay {
    backdrop-filter: blur(2px);
  }

  .modal-content {
    width: 92%;
    max-width: 92%;
    padding: 16px;
    border-radius: 16px;
    margin: 16px;
  }

  .modal-header {
    margin-bottom: 14px;
  }

  .modal-header h3 {
    font-size: 16px;
  }

  .close-btn {
    width: 24px;
    height: 24px;
    font-size: 18px;
  }

  .form-group {
    margin-bottom: 14px;
  }

  .form-group label {
    font-size: 13px;
    margin-bottom: 5px;
  }

  .tag-input {
    padding: 8px 10px;
    font-size: 13px;
    border-radius: 6px;
  }

  .color-picker-container {
    gap: 6px;
  }

  .color-input {
    width: 44px;
    height: 32px;
    border-radius: 6px;
  }

  .color-text {
    padding: 8px 8px;
    font-size: 12px;
    border-radius: 6px;
  }

  .color-presets {
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    margin-top: 8px;
  }

  .color-preset {
    border-radius: 6px;
  }

  .error-message {
    font-size: 12px;
    margin-bottom: 12px;
  }

  .modal-actions {
    gap: 8px;
    margin-top: 4px;
  }

  .cancel-btn,
  .save-btn {
    padding: 7px 14px;
    font-size: 12px;
    border-radius: 6px;
  }
}
</style>
