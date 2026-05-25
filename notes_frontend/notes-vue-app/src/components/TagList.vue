<template>
  <div class="tag-list">
    <div class="tag-list-header">
      <h3>Теги</h3>
      <button class="add-tag-btn" title="Добавить тег" @click="$emit('create')">+</button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner-small"></div>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="$emit('retry')">Повторить</button>
    </div>

    <div v-else-if="tags.length === 0" class="empty">
      <p>Нет тегов</p>
    </div>

    <div v-else class="tags-container">
      <div
        v-for="tag in tags"
        :key="tag.id"
        class="tag-item"
        :class="{ selected: selectedTagId === tag.id }"
        @click="$emit('select', tag)"
      >
        <div class="tag-info">
          <span class="tag-color-dot" :style="{ backgroundColor: tag.color || '#7517CC' }"></span>
          <span class="tag-name">{{ tag.name }}</span>
        </div>
        <div class="tag-actions">
          <button class="edit-tag-btn" title="Редактировать" @click.stop="$emit('edit', tag)">
            ✏️
          </button>
          <button class="delete-tag-btn" title="Удалить" @click.stop="$emit('delete', tag)">
            ×
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  tags: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
  selectedTagId: {
    type: Number,
    default: null,
  },
})

defineEmits(['select', 'edit', 'delete', 'create', 'retry'])
</script>

<style scoped>
.tag-list {
  background: var(--bg-primary);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

.tag-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.tag-list-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}

.add-tag-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  border: none;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
}

.add-tag-btn:hover {
  background: var(--primary-hover);
}

.loading {
  text-align: center;
  padding: 20px;
}

.spinner-small {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color);
  border-top: 2px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error,
.empty {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
}

.error {
  color: var(--danger-color);
}

.retry-btn {
  margin-top: 8px;
  padding: 6px 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

/* Главное — скроллируемый контейнер с фиолетовой полоской */
.tags-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
  padding-right: 4px;

  /* Фиолетовый кастомный скроллбар */
  scrollbar-width: thin;
  scrollbar-color: var(--primary-color) transparent;
}

.tags-container::-webkit-scrollbar {
  width: 4px;
}

.tags-container::-webkit-scrollbar-track {
  background: transparent;
}

.tags-container::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 4px;
}

.tags-container::-webkit-scrollbar-thumb:hover {
  background: var(--primary-hover);
}

.tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  flex-shrink: 0;
}

.tag-item:hover {
  background: var(--hover-bg);
}

.tag-item.selected {
  background: var(--active-bg);
  border-color: var(--primary-color);
}

.tag-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.tag-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.tag-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  word-break: break-word;
  overflow-wrap: break-word;
}

.tag-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.tag-item:hover .tag-actions {
  opacity: 1;
}

.edit-tag-btn,
.delete-tag-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 14px;
  transition: background 0.2s;
}

.edit-tag-btn:hover {
  background: var(--primary-light);
}

.delete-tag-btn {
  font-size: 18px;
  font-weight: bold;
  color: var(--danger-color);
}

.delete-tag-btn:hover {
  background: var(--danger-bg);
}

@media (max-width: 768px) {
  .tag-list {
    padding: 16px;
    height: auto;
    max-height: 400px;
  }

  .tag-list-header h3 {
    font-size: 16px;
  }

  .add-tag-btn {
    width: 28px;
    height: 28px;
    font-size: 18px;
  }

  .tag-item {
    padding: 8px 10px;
  }

  .tag-name {
    font-size: 13px;
  }

  .tag-actions {
    opacity: 0.7;
  }

  .edit-tag-btn,
  .delete-tag-btn {
    padding: 4px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .tag-list {
    padding: 12px;
    border-radius: 12px;
    max-height: 350px;
  }

  .tag-list-header {
    margin-bottom: 12px;
  }

  .tag-list-header h3 {
    font-size: 15px;
  }

  .add-tag-btn {
    width: 26px;
    height: 26px;
    font-size: 16px;
  }

  .tags-container {
    gap: 6px;
    padding-right: 2px;
  }

  /* Элемент тега */
  .tag-item {
    padding: 8px 10px;
  }

  .tag-info {
    gap: 6px;
  }

  .tag-color-dot {
    width: 10px;
    height: 10px;
  }

  .tag-name {
    font-size: 12px;
  }

  .tag-actions {
    opacity: 0.8;
  }

  .edit-tag-btn,
  .delete-tag-btn {
    padding: 3px 5px;
    font-size: 11px;
  }

  .delete-tag-btn {
    font-size: 16px;
  }

  .edit-tag-btn,
  .delete-tag-btn,
  .add-tag-btn {
    min-width: 32px;
    min-height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .empty,
  .error {
    padding: 16px;
    font-size: 13px;
  }

  .retry-btn {
    padding: 6px 12px;
    font-size: 11px;
  }
}

</style>
