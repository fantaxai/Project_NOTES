<template>
  <div class="create-note-page">
    <div class="create-form">
      <h1 class="form-title">Новая идея</h1>

      <div class="form-group">
        <label for="title">Заголовок</label>
        <input
          id="title"
          v-model="title"
          type="text"
          placeholder="Введите заголовок идеи"
          class="title-input"
          autofocus
        />
      </div>

      <div class="form-group">
        <label for="content">Содержание</label>
        <textarea
          id="content"
          v-model="content"
          placeholder="Опишите вашу идею..."
          rows="8"
          class="content-input"
        ></textarea>
      </div>

      <!-- Секция прикрепления файлов -->
      <div class="form-group">
        <label>Файлы</label>
        <div class="files-upload-area">
          <div class="drop-zone" @drop="handleDrop" @dragover.prevent @click="triggerFileInput">
            <input
              ref="fileInput"
              type="file"
              multiple
              accept=".pdf,.txt,.jpg,.jpeg"
              style="display: none"
              @change="handleFileSelect"
            />
            <div class="drop-zone-content">
              <span class="upload-icon">📎</span>
              <p class="upload-text">Нажмите или перетащите файлы сюда</p>
              <p class="upload-hint">PDF, TXT, JPG до 10 МБ</p>
            </div>
          </div>

          <!-- Список выбранных файлов -->
          <div v-if="pendingFiles.length > 0" class="files-list">
            <div v-for="(file, index) in pendingFiles" :key="index" class="file-item">
              <div class="file-preview">
                <img
                  v-if="file.preview && ['jpg', 'jpeg'].includes(file.format)"
                  :src="file.preview"
                  :alt="file.name"
                  class="file-thumbnail"
                />
                <span v-else class="file-icon">{{ getFileIcon(file.format) }}</span>
              </div>

              <div class="file-info">
                <div class="file-name" :title="file.name">{{ file.name }}</div>
                <div class="file-meta">
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  <span class="file-format">{{ file.format.toUpperCase() }}</span>
                  <span v-if="file.uploading" class="uploading-badge">Загрузка...</span>
                </div>
              </div>

              <button
                class="file-remove-btn"
                :disabled="file.uploading"
                title="Удалить"
                @click="removeFile(index)"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label class="checkbox-label">
          <input v-model="isIdeaCandidate" type="checkbox" class="idea-checkbox" />
          <span class="checkbox-text">
            <span class="checkbox-icon">💡</span>
            Отметить как кандидата для "Идеи дня"
          </span>
        </label>
        <p class="checkbox-hint">Заметки с этой отметкой могут быть выбраны как "Идея дня"</p>
      </div>

      <div class="form-group">
        <div class="tags-header">
          <label>Теги</label>
          <button class="add-tag-btn" type="button" @click="showNewTagForm = !showNewTagForm">
            {{ showNewTagForm ? '− Отмена' : '+ Новый тег' }}
          </button>
        </div>

        <!-- Форма создания нового тега -->
        <div v-if="showNewTagForm" class="new-tag-form">
          <div class="new-tag-inputs">
            <input
              v-model="newTagName"
              type="text"
              placeholder="Название тега"
              class="new-tag-name"
              @keyup.enter.prevent="createNewTag"
            />
            <div class="new-tag-color">
              <input v-model="newTagColor" type="color" class="color-picker" />
              <div class="color-presets-mini">
                <button
                  v-for="color in quickColors"
                  :key="color"
                  type="button"
                  class="color-dot"
                  :style="{ backgroundColor: color }"
                  @click="newTagColor = color"
                ></button>
              </div>
            </div>
            <button
              :disabled="!newTagName.trim() || creatingTag"
              class="create-tag-btn"
              @click="createNewTag"
            >
              {{ creatingTag ? '...' : 'Создать' }}
            </button>
          </div>
          <div v-if="newTagError" class="tag-error">{{ newTagError }}</div>
        </div>

        <!-- Выбор тегов -->
        <div v-if="tagStore.loading" class="tags-loading">Загрузка тегов...</div>
        <div v-else class="tags-selector">
          <button
            v-for="tag in tagStore.tags"
            :key="tag.id"
            type="button"
            :class="['tag-option', { selected: selectedTags.includes(tag.id) }]"
            :style="
              selectedTags.includes(tag.id)
                ? {
                    backgroundColor: tag.color,
                    borderColor: tag.color,
                    color: 'white',
                  }
                : {
                    borderColor: tag.color,
                    color: tag.color,
                  }
            "
            @click="toggleTag(tag.id)"
          >
            #{{ tag.name }}
          </button>
          <div v-if="tagStore.tags.length === 0 && !showNewTagForm" class="no-tags-hint">
            💡 Нет тегов. Нажмите "+ Новый тег" чтобы создать
          </div>
        </div>
      </div>

      <div class="form-actions">
        <router-link to="/notes" class="cancel-link">Отмена</router-link>
        <button
          :disabled="!title.trim() || creating || hasUploadingFiles"
          class="create-btn"
          @click="handleCreate"
        >
          {{ creating ? 'Создание...' : 'Создать идею' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useNoteListStore } from '../stores/notelist'
import { useTagStore } from '../stores/tags'
import { useFileStore } from '../stores/files'

const router = useRouter()
const noteListStore = useNoteListStore()
const tagStore = useTagStore()
const fileStore = useFileStore()

const title = ref('')
const content = ref('')
const selectedTags = ref([])
const isIdeaCandidate = ref(true)
const error = ref(null)
const creating = ref(false)

// Состояние для файлов
const fileInput = ref(null)
const pendingFiles = ref([])

// Создание нового тега
const showNewTagForm = ref(false)
const newTagName = ref('')
const newTagColor = ref('#C9A9E8')
const creatingTag = ref(false)
const newTagError = ref(null)

const quickColors = [
  '#FFB3B3',
  '#FFD6A5',
  '#FDFFB6',
  '#CAFFBF',
  '#9BF6FF',
  '#A0C4FF',
  '#BDB2FF',
  '#FFC6FF',
]

// Проверка, есть ли файлы в процессе загрузки
const hasUploadingFiles = computed(() => {
  return pendingFiles.value.some((f) => f.uploading)
})

onMounted(async () => {
  try {
    await tagStore.fetchTags()
  } catch (err) {
    console.error('Ошибка загрузки тегов:', err)
  }
})

const toggleTag = (tagId) => {
  const index = selectedTags.value.indexOf(tagId)
  if (index === -1) {
    selectedTags.value.push(tagId)
  } else {
    selectedTags.value.splice(index, 1)
  }
}

const createNewTag = async () => {
  if (!newTagName.value.trim()) return

  creatingTag.value = true
  newTagError.value = null

  try {
    const newTag = await tagStore.createTag({
      name: newTagName.value.trim(),
      color: newTagColor.value,
    })

    selectedTags.value.push(newTag.id)

    newTagName.value = ''
    newTagColor.value = '#C9A9E8'
    showNewTagForm.value = false
  } catch (err) {
    newTagError.value = err.response?.data?.detail || 'Ошибка создания тега'
  } finally {
    creatingTag.value = false
  }
}

// Функции для работы с файлами
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addFiles(files)
  fileInput.value.value = ''
}

const handleDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  addFiles(files)
}

const addFiles = (files) => {
  const allowedFormats = ['pdf', 'txt', 'jpg', 'jpeg']
  const maxSize = 10 * 1024 * 1024

  for (const file of files) {
    const format = file.name.split('.').pop().toLowerCase()

    if (!allowedFormats.includes(format)) {
      alert(`Файл ${file.name} имеет недопустимый формат. Разрешены: PDF, TXT, JPG`)
      continue
    }

    if (file.size > maxSize) {
      alert(`Файл ${file.name} слишком большой. Максимальный размер: 10 МБ`)
      continue
    }

    // Создаем превью для изображений
    let preview = null
    if (['jpg', 'jpeg'].includes(format)) {
      preview = URL.createObjectURL(file)
    }

    pendingFiles.value.push({
      file,
      name: file.name,
      size: file.size,
      format: format,
      preview: preview,
      uploading: false,
    })
  }
}

const removeFile = (index) => {
  const file = pendingFiles.value[index]
  if (file.preview) {
    URL.revokeObjectURL(file.preview)
  }
  pendingFiles.value.splice(index, 1)
}

const createThumbnail = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')

        const size = 100
        canvas.width = size
        canvas.height = size

        let width = img.width
        let height = img.height
        let x = 0,
          y = 0

        if (width > height) {
          width = (height / img.height) * img.width
          x = -(width - size) / 2
        } else {
          height = (width / img.width) * img.height
          y = -(height - size) / 2
        }

        ctx.fillStyle = '#f0f0f0'
        ctx.fillRect(0, 0, size, size)
        ctx.drawImage(img, x, y, width, height)
        resolve(canvas.toDataURL('image/jpeg', 0.7))
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  })
}

const uploadFilesForNote = async (noteId) => {
  for (let i = 0; i < pendingFiles.value.length; i++) {
    const fileData = pendingFiles.value[i]
    fileData.uploading = true

    try {
      let thumbnail = null
      if (['jpg', 'jpeg'].includes(fileData.format)) {
        thumbnail = await createThumbnail(fileData.file)
      }

      await fileStore.uploadFile({
        name: fileData.name,
        size: fileData.size,
        format: fileData.format,
        note: noteId,
        thumbnail: thumbnail,
      })

      fileData.uploading = false
      fileData.uploaded = true
    } catch (err) {
      console.error('Ошибка загрузки файла:', err)
      fileData.uploading = false
      fileData.error = true
      throw err
    }
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileIcon = (format) => {
  const icons = {
    pdf: '📄',
    jpg: '🖼️',
    jpeg: '🖼️',
    txt: '📝',
  }
  return icons[format] || '📎'
}

const handleCreate = async () => {
  if (!title.value.trim()) {
    error.value = 'Введите заголовок идеи'
    return
  }

  creating.value = true
  error.value = null

  const noteData = {
    title: title.value.trim(),
    content: content.value,
    tag_ids: selectedTags.value,
    is_idea_candidate: isIdeaCandidate.value,
  }

  try {
    // Создаем заметку
    const newNote = await noteListStore.createNote(noteData)

    if (newNote && newNote.id) {
      // Если есть файлы, загружаем их
      if (pendingFiles.value.length > 0) {
        try {
          await uploadFilesForNote(newNote.id)
        } catch (err) {
          console.error('Ошибка загрузки файлов:', err)
          // Даже если файлы не загрузились, заметка уже создана
        }
      }

      // Переходим к заметке
      router.push(`/note/${newNote.id}`)
    } else {
      error.value = 'Ошибка: сервер не вернул ID заметки'
    }
  } catch (err) {
    error.value = 'Ошибка создания идеи: ' + (err.response?.data?.detail || err.message)
    console.error('Детали ошибки:', err.response)
  } finally {
    creating.value = false
  }
}

// Очистка превью при уничтожении компонента
import { onBeforeUnmount } from 'vue'
onBeforeUnmount(() => {
  pendingFiles.value.forEach((file) => {
    if (file.preview) {
      URL.revokeObjectURL(file.preview)
    }
  })
})
</script>

<style scoped>
.create-note-page {
  min-height: 100vh;
  background: var(--bg-secondary, #f5f5f5);
  padding: 40px 20px;
}

.create-form {
  max-width: 800px;
  margin: 0 auto;
  background: var(--bg-primary, white);
  border-radius: 24px;
  padding: 40px;
  box-shadow: var(--card-shadow, 0 4px 20px rgba(0, 0, 0, 0.08));
  border: 1px solid var(--border-color, transparent);
}

.form-title {
  margin: 0 0 32px 0;
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
}

.form-group {
  margin-bottom: 28px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.title-input,
.content-input {
  width: 100%;
  padding: 14px 16px;
  border: 1.5px solid var(--border-color, #e0e0e0);
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.2s;
  font-family: inherit;
  box-sizing: border-box;
  background: var(--bg-primary, white);
  color: var(--text-primary, #1a1a1a);
}

.title-input:focus,
.content-input:focus {
  outline: none;
  border-color: var(--primary-color, #c9a9e8);
  box-shadow: 0 0 0 3px rgba(201, 169, 232, 0.1);
}

.title-input::placeholder,
.content-input::placeholder {
  color: var(--text-tertiary, #999);
}

.content-input {
  resize: vertical;
  line-height: 1.6;
}

/* Секция файлов */
.files-upload-area {
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 12px;
  overflow: hidden;
}

.drop-zone {
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-tertiary, #fafafa);
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.drop-zone:hover {
  background: var(--primary-light, #f0e6ff);
  border-color: var(--primary-color, #c9a9e8);
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  font-size: 32px;
  opacity: 0.6;
}

.upload-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-primary, #333);
}

.upload-hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

.files-list {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 250px;
  overflow-y: auto;
  background: var(--bg-primary, white);
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: var(--bg-tertiary, #f8f9fa);
  border-radius: 8px;
}

.file-preview {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--border-color, #e0e0e0);
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.file-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  font-size: 20px;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #333);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.file-meta {
  display: flex;
  gap: 10px;
  font-size: 11px;
  color: var(--text-tertiary, #999);
}

.uploading-badge {
  color: var(--primary-color, #c9a9e8);
  font-weight: 500;
}

.file-remove-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  opacity: 0.5;
  transition: all 0.2s;
  flex-shrink: 0;
  color: var(--text-secondary, #666);
}

.file-remove-btn:hover:not(:disabled) {
  opacity: 1;
  background: var(--danger-bg, #fee);
  color: var(--danger-color, #dc3545);
}

.file-remove-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Чекбокс идеи дня */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px 16px;
  border: 2px solid var(--border-color, #e0e0e0);
  border-radius: 12px;
  transition: all 0.2s;
  background: var(--bg-primary, white);
}

.checkbox-label:hover {
  border-color: var(--primary-color, #c9a9e8);
  background: var(--primary-light, #f8f4ff);
}

.idea-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: var(--primary-color, #c9a9e8);
}

.checkbox-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.checkbox-icon {
  font-size: 20px;
}

.checkbox-hint {
  margin: 8px 0 0 32px;
  font-size: 13px;
  color: var(--text-secondary, #666);
  font-style: italic;
}

/* Заголовок секции тегов */
.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.add-tag-btn {
  background: none;
  border: 1.5px dashed var(--primary-color, #c9a9e8);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  color: var(--primary-color, #c9a9e8);
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.add-tag-btn:hover {
  background: var(--primary-light, #f0e6ff);
  border-style: solid;
}

/* Форма создания тега */
.new-tag-form {
  background: var(--bg-tertiary, #f8f9fa);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.new-tag-inputs {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.new-tag-name {
  flex: 1;
  min-width: 180px;
  padding: 10px 14px;
  border: 1.5px solid var(--border-color, #e0e0e0);
  border-radius: 10px;
  font-size: 14px;
  background: var(--bg-primary, white);
  color: var(--text-primary, #333);
}

.new-tag-name:focus {
  outline: none;
  border-color: var(--primary-color, #c9a9e8);
}

.new-tag-color {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-picker {
  width: 44px;
  height: 44px;
  padding: 2px;
  border: 1.5px solid var(--border-color, #e0e0e0);
  border-radius: 10px;
  cursor: pointer;
  background: var(--bg-primary, white);
}

.color-presets-mini {
  display: flex;
  gap: 4px;
}

.color-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid var(--bg-primary, white);
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.color-dot:hover {
  transform: scale(1.15);
}

.create-tag-btn {
  padding: 10px 20px;
  background: var(--primary-color, #c9a9e8);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.create-tag-btn:hover:not(:disabled) {
  background: var(--primary-hover, #b794d4);
}

.create-tag-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tag-error {
  margin-top: 10px;
  color: var(--danger-color, #dc3545);
  font-size: 13px;
}

/* Выбор тегов */
.tags-loading {
  color: var(--text-tertiary, #999);
  font-size: 14px;
  padding: 8px 0;
}

.tags-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tag-option {
  background: var(--bg-primary, white);
  border: 2px solid;
  padding: 8px 18px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-option:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tag-option.selected {
  color: white !important;
}

.no-tags-hint {
  color: var(--text-tertiary, #999);
  font-size: 14px;
  font-style: italic;
  padding: 8px 0;
  width: 100%;
}

/* Действия */
.form-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color, #e0e0e0);
}

.cancel-link {
  padding: 12px 24px;
  color: var(--text-secondary, #666);
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  border-radius: 10px;
  transition: all 0.2s;
}

.cancel-link:hover {
  background: var(--hover-bg, #f5f5f5);
}

.create-btn {
  padding: 12px 32px;
  background: var(--primary-color, #c9a9e8);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.create-btn:hover:not(:disabled) {
  background: var(--primary-hover, #b794d4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(201, 169, 232, 0.3);
}

.create-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffb3b3;
  color: #333;
  padding: 14px 28px;
  border-radius: 12px;
  font-size: 14px;
  z-index: 1000;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

@media (max-width: 640px) {
  .create-form {
    padding: 24px;
  }

  .new-tag-inputs {
    flex-direction: column;
    align-items: stretch;
  }

  .new-tag-name {
    min-width: auto;
  }

  .new-tag-color {
    justify-content: space-between;
  }

  .form-actions {
    flex-direction: column-reverse;
    gap: 12px;
  }

  .cancel-link,
  .create-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
