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
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tag-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tag-list-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.add-tag-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  border: none;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.add-tag-btn:hover {
  background: #0056b3;
}

.loading {
  text-align: center;
  padding: 20px;
}

.spinner-small {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
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

.error,
.empty {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: #dc3545;
}

.retry-btn {
  margin-top: 8px;
  padding: 6px 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.tags-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.tag-item:hover {
  background: #e9ecef;
}

.tag-item.selected {
  background: #e3f2fd;
  border-color: #007bff;
}

.tag-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.tag-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.tag-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
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
  background: rgba(0, 123, 255, 0.1);
}

.delete-tag-btn {
  font-size: 18px;
  font-weight: bold;
  color: #dc3545;
}

.delete-tag-btn:hover {
  background: rgba(220, 53, 69, 0.1);
}
</style>
