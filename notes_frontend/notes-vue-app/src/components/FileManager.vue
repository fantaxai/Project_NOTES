<script setup>
import { ref, onMounted, computed } from 'vue'
import { useFileStore } from '../stores/files'

const props = defineProps({
  noteId: {
    type: [Number, String],
    required: true,
  },
})

const emit = defineEmits(['file-uploaded', 'file-deleted'])

const fileStore = useFileStore()
const fileInput = ref(null)
const uploading = ref(false)

const files = computed(() => fileStore.currentNoteFiles)
const loading = computed(() => fileStore.loading)

onMounted(() => {
  loadFiles()
})

const loadFiles = async () => {
  if (!props.noteId) return

  try {
    await fileStore.fetchNoteFiles(props.noteId)
  } catch (err) {
    console.error('Ошибка загрузки файлов:', err)
  }
}

// Метод для внешнего вызова
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event) => {
  const selectedFiles = Array.from(event.target.files)
  await uploadFiles(selectedFiles)
}

const uploadFiles = async (selectedFiles) => {
  const allowedFormats = ['pdf', 'txt', 'jpg', 'jpeg']
  const maxSize = 10 * 1024 * 1024

  for (const file of selectedFiles) {
    const format = file.name.split('.').pop().toLowerCase()

    if (!allowedFormats.includes(format)) {
      alert(`Файл ${file.name} имеет недопустимый формат. Разрешены: PDF, TXT, JPG`)
      continue
    }

    if (file.size > maxSize) {
      alert(`Файл ${file.name} слишком большой. Максимальный размер: 10 МБ`)
      continue
    }

    uploading.value = true

    try {
      let thumbnail = null
      if (['jpg', 'jpeg'].includes(format)) {
        thumbnail = await createThumbnail(file)
      }

      const fileData = {
        name: file.name,
        size: file.size,
        format: format,
        note: props.noteId,
        thumbnail: thumbnail,
      }

      const uploadedFile = await fileStore.uploadFile(fileData)
      emit('file-uploaded', uploadedFile)
    } catch (err) {
      console.error('Ошибка загрузки файла:', err)
      alert(`Не удалось загрузить файл ${file.name}`)
    }
  }

  uploading.value = false
  if (fileInput.value) {
    fileInput.value.value = ''
  }
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

const handleDeleteFile = async (fileId) => {
  if (!confirm('Вы уверены, что хотите удалить этот файл?')) {
    return
  }

  try {
    await fileStore.deleteFile(fileId)
    emit('file-deleted', fileId)
  } catch (err) {
    alert('Не удалось удалить файл')
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

// Заменяет старую downloadFile
const openFile = (file) => {
  if (!file.file_url) {
    alert('Ссылка на файл недоступна')
    return
  }

  const imageFormats = ['jpg', 'jpeg', 'png', 'gif', 'webp']
  if (imageFormats.includes(file.format?.toLowerCase())) {
    // Открываем картинку в новой вкладке
    window.open(file.file_url, '_blank')
    return
  }

  if (file.format?.toLowerCase() === 'pdf') {
    // PDF открываем в новой вкладке для просмотра
    window.open(file.file_url, '_blank')
    return
  }

  // Остальные файлы — скачиваем
  const link = document.createElement('a')
  link.href = file.file_url
  link.download = file.name
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
const downloadFileDirectly = (file) => {
  if (!file.file_url) return
  const link = document.createElement('a')
  link.href = file.file_url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Экспортируем метод для родительского компонента
defineExpose({
  triggerFileInput,
})
</script>

<template>
  <div class="file-manager">
    <!-- Скрытый input для выбора файлов -->
    <input
      ref="fileInput"
      type="file"
      multiple
      accept=".pdf,.txt,.jpg,.jpeg"
      style="display: none"
      @change="handleFileSelect"
    />

    <!-- Состояние загрузки -->
    <div v-if="loading" class="loading-files">
      <div class="spinner-small"></div>
      <span>Загрузка файлов...</span>
    </div>

    <!-- Список файлов -->
    <div v-else-if="files.length > 0" class="files-list">
      <div v-for="file in files" :key="file.id" class="file-item" @click="openFile(file)">
        <div class="file-preview">
          <img
            v-if="file.thumbnail && ['jpg', 'jpeg'].includes(file.format)"
            :src="file.thumbnail"
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
          </div>
        </div>

        <button
          class="file-download-btn"
          title="Скачать файл"
          @click.stop="downloadFileDirectly(file)"
        >
          ⬇️
        </button>

        <button
          class="file-delete-btn"
          title="Удалить файл"
          @click.stop="handleDeleteFile(file.id)"
        >
          🗑️
        </button>
      </div>
    </div>

    <!-- Нет файлов -->
    <div v-else class="empty-files">
      <span class="empty-icon">📎</span>
      <p>Нет прикрепленных файлов</p>
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="uploading" class="uploading-indicator">
      <div class="spinner-small"></div>
      <span>Загрузка файла...</span>
    </div>
  </div>
</template>

<style scoped>
.file-manager {
  width: 100%;
}

.loading-files {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  color: #666;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #5700b3;
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

.files-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.file-item:hover {
  background: #f8f4ff;
  border-color: #5700b3;
}

.file-preview {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
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
  font-size: 24px;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.file-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.file-download-btn {
  background: none;
  border: none;
  font-size: 14px;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  opacity: 0.6;
  transition: all 0.2s;
  flex-shrink: 0;
}

.file-download-btn:hover {
  opacity: 1;
  background: #e8f4ff;
}

.file-delete-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  opacity: 0.6;
  transition: all 0.2s;
  flex-shrink: 0;
}

.file-delete-btn:hover {
  opacity: 1;
  background: #fee;
}

.empty-files {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  color: #999;
  text-align: center;
}

.empty-icon {
  font-size: 32px;
  opacity: 0.5;
  margin-bottom: 8px;
}

.empty-files p {
  margin: 0;
  font-size: 14px;
}

.uploading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  margin-top: 12px;
  background: #f8f4ff;
  border-radius: 8px;
  color: #5700b3;
  font-size: 14px;
}
</style>
