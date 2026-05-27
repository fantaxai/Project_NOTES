<template>
  <div class="tags-page">
    <div class="page-header">
      <button class="back-btn" @click="goBack">← Назад</button>
      <h1 class="page-title">Управление тегами</h1>
      <div class="placeholder"></div>
    </div>

    <div class="tags-content">
      <div class="tags-sidebar">
        <div class="tag-list-wrapper">
          <TagList
            :tags="tagStore.tags"
            :loading="tagStore.loading"
            :error="tagStore.error"
            :selected-tag-id="selectedTag?.id"
            @select="handleSelectTag"
            @edit="handleEditTag"
            @delete="handleDeleteTag"
            @create="handleCreateTag"
            @retry="loadTags"
          />
        </div>
      </div>

      <div class="tags-main">
        <div v-if="!selectedTag" class="no-selection">
          <p>Выберите тег для просмотра связанных заметок</p>
        </div>

        <div v-else class="tag-notes">
          <div class="tag-notes-header">
            <h2>Заметки с тегом "{{ selectedTag.name }}"</h2>
            <button class="refresh-btn" :disabled="notesLoading" @click="refreshNotes">🔄</button>
          </div>

          <div v-if="notesLoading" class="loading">
            <div class="spinner"></div>
          </div>

          <div v-else-if="notesError" class="error">
            <p>{{ notesError }}</p>
          </div>

          <div v-else-if="tagNotes.length === 0" class="empty">
            <p>Нет заметок с этим тегом</p>
          </div>

          <div v-else class="notes-list">
            <div
              v-for="note in tagNotes"
              :key="note.id"
              class="note-item"
              @click="goToNote(note.id)"
            >
              <h3>{{ note.title }}</h3>
              <p class="note-preview">{{ note.content.substring(0, 100) }}...</p>
              <span class="note-date">{{ formatDate(note.last_change_date) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <TagForm
      :show="showModal"
      :tag="editingTag"
      :loading="modalLoading"
      :error="modalError"
      @close="closeModal"
      @save="handleSaveTag"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTagStore } from '../stores/tags'
import TagList from '../components/TagList.vue'
import TagForm from '../components/TagForm.vue'

const router = useRouter()
const tagStore = useTagStore()

const selectedTag = ref(null)
const tagNotes = ref([])
const notesLoading = ref(false)
const notesError = ref(null)

const showModal = ref(false)
const editingTag = ref(null)
const modalLoading = ref(false)
const modalError = ref(null)

const loadTags = async () => {
  try {
    await tagStore.fetchTags()
  } catch (error) {
    console.error('Ошибка загрузки тегов:', error)
  }
}

const handleSelectTag = async (tag) => {
  selectedTag.value = tag
  await loadNotesForTag(tag.id)
}

const loadNotesForTag = async (tagId) => {
  notesLoading.value = true
  notesError.value = null
  try {
    const notes = await tagStore.fetchNotesByTag(tagId)
    tagNotes.value = notes
  } catch (error) {
    notesError.value = 'Ошибка загрузки заметок'
    console.error('Ошибка загрузки заметок:', error)
  } finally {
    notesLoading.value = false
  }
}

const refreshNotes = () => {
  if (selectedTag.value) {
    loadNotesForTag(selectedTag.value.id)
  }
}

const handleCreateTag = () => {
  editingTag.value = null
  showModal.value = true
}

const handleEditTag = (tag) => {
  editingTag.value = tag
  showModal.value = true
}

const handleDeleteTag = async (tag) => {
  if (confirm(`Удалить тег "${tag.name}"?`)) {
    try {
      await tagStore.deleteTag(tag.id)
      if (selectedTag.value?.id === tag.id) {
        selectedTag.value = null
        tagNotes.value = []
      }
    } catch (error) {
      alert('Ошибка удаления тега')
    }
  }
}

const handleSaveTag = async (tagData) => {
  modalLoading.value = true
  modalError.value = null

  try {
    const dataToSave = {
      name: tagData.name,
      color: tagData.color,
    }

    if (tagData.id) {
      await tagStore.updateTag(tagData.id, dataToSave)
    } else {
      await tagStore.createTag(dataToSave)
    }

    closeModal()

    if (tagData.id && selectedTag.value?.id === tagData.id) {
      selectedTag.value = tagStore.tags.find((t) => t.id === tagData.id)
    }
  } catch (error) {
    modalError.value = error.message || 'Ошибка сохранения тега'
  } finally {
    modalLoading.value = false
  }
}

const closeModal = () => {
  showModal.value = false
  editingTag.value = null
  modalError.value = null
}

const goToNote = (noteId) => {
  router.push(`/note/${noteId}`)
}

const goBack = () => {
  router.push('/')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
/* Стили остаются те же */
.tags-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #007bff;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #f0f0f0;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #1a1a1a;
}

.placeholder {
  width: 70px;
}

.tags-content {
  display: flex;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  gap: 24px;
}

.tags-sidebar {
  width: 300px;
  flex-shrink: 0;
}

.tags-main {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #666;
  text-align: center;
}

.tag-notes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.tag-notes-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.refresh-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #f0f0f0;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
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
  padding: 40px;
  color: #666;
}

.error {
  color: #dc3545;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.note-item {
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.note-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
}

.note-item h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #333;
}

.note-preview {
  margin: 0 0 12px 0;
  color: #666;
  line-height: 1.5;
}

.note-date {
  font-size: 12px;
  color: #999;
}

@media (max-width: 768px) {
  .page-header {
    padding: 12px 16px;
  }

  .back-btn {
    font-size: 14px;
    padding: 6px 10px;
  }

  .page-title {
    font-size: 18px;
  }

  .placeholder {
    width: 60px;
  }

  .tags-content {
    flex-direction: column;
    padding: 16px;
    gap: 16px;
  }

  .tags-sidebar {
    width: 100%;
  }

  .tag-list-wrapper :deep(.tag-list) {
    max-height: 400px;
  }

  .tags-main {
    padding: 16px;
  }

  .tag-notes-header h2 {
    font-size: 20px;
  }

  .note-item {
    padding: 16px;
  }

  .note-item h3 {
    font-size: 16px;
  }

  .note-preview {
    font-size: 13px;
    -webkit-line-clamp: 2;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 10px 12px;
  }

  .back-btn {
    font-size: 13px;
    padding: 5px 8px;
  }

  .page-title {
    font-size: 16px;
  }

  .placeholder {
    width: 50px;
  }

  .tags-content {
    padding: 12px;
    gap: 12px;
  }

  .tags-sidebar {
    width: 100%;
  }

  .tag-list-wrapper :deep(.tag-list) {
    max-height: 350px;
  }

  .tags-main {
    padding: 12px;
    border-radius: 12px;
  }

  .tag-notes-header {
    margin-bottom: 16px;
    flex-wrap: wrap;
    gap: 10px;
  }

  .tag-notes-header h2 {
    font-size: 16px;
    word-break: break-word;
  }

  .refresh-btn {
    font-size: 18px;
    padding: 6px;
  }

  .loading {
    padding: 30px;
  }

  .spinner {
    width: 30px;
    height: 30px;
  }

  .error,
  .empty {
    padding: 30px 20px;
    font-size: 14px;
  }

  .notes-list {
    gap: 12px;
  }

  .note-item {
    padding: 12px;
  }

  .note-item h3 {
    font-size: 15px;
    margin-bottom: 6px;
  }

  .note-preview {
    font-size: 12px;
    margin-bottom: 8px;
    -webkit-line-clamp: 2;
  }

  .note-date {
    font-size: 11px;
  }
}
</style>
