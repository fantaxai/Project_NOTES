<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNoteStore } from '../stores/notes'
import { useTagStore } from '../stores/tags'
import NoteDisplay from '../components/NoteDisplay.vue'

const route = useRoute()
const router = useRouter()
const noteStore = useNoteStore()
const tagStore = useTagStore()

const loadNote = async () => {
  const id = route.params.id
  if (id) {
    try {
      await Promise.all([noteStore.fetchNoteById(id), tagStore.fetchTags()])
    } catch (error) {
      console.error('Ошибка загрузки:', error)
    }
  }
}

const handleUpdate = async (updatedData) => {
  if (noteStore.currentNote?.id) {
    try {
      await noteStore.updateNote(noteStore.currentNote.id, updatedData)
      await noteStore.fetchNoteById(noteStore.currentNote.id)
    } catch (error) {
      console.error('Ошибка обновления:', error)
    }
  }
}

const handleDelete = async () => {
  if (confirm('Удалить эту идею?')) {
    try {
      await noteStore.deleteNote(noteStore.currentNote.id)
      // Возвращаемся назад с сохранением query-параметров
      goBack()
    } catch (error) {
      console.error('Ошибка удаления:', error)
    }
  }
}

const handleCreateTag = async (tagData) => {
  try {
    const newTag = await tagStore.createTag(tagData)
    // Обновляем список тегов
    await tagStore.fetchTags()
    return newTag
  } catch (error) {
    console.error('Ошибка создания тега:', error)
    throw error
  }
}

const goBack = () => {
  // Всегда возвращаемся на список заметок с сохранением query-параметров
  const currentQuery = route.query
  router.push({ path: '/notes', query: currentQuery })
}

onMounted(() => {
  loadNote()
})

onUnmounted(() => {
  noteStore.clearCurrentNote()
})
</script>

<template>
  <div class="note-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">← Назад к списку</button>
      <h1 class="page-title">Просмотр идеи</h1>
      <div class="placeholder"></div>
    </div>

    <NoteDisplay
      :note="noteStore.currentNote"
      :loading="noteStore.loading"
      :error="noteStore.error"
      :available-tags="tagStore.tags"
      @update="handleUpdate"
      @delete="handleDelete"
      @retry="loadNote"
      @create-tag="handleCreateTag"
    />
  </div>
</template>

<style scoped>
.note-page {
  min-height: 100vh;
  background: var(--bg-secondary, #f5f5f5);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--bg-primary, white);
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  position: sticky;
  top: 64px;
  z-index: 99;
}

.back-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: var(--primary-color, #c9a9e8);
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.back-btn:hover {
  background: var(--primary-light, #f0e6ff);
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: var(--text-secondary, #666);
}

.placeholder {
  width: 120px;
}

@media (max-width: 768px) {
  .page-header {
    top: 120px;
  }

  .page-title {
    display: none;
  }

  .placeholder {
    width: 80px;
  }
}
</style>
