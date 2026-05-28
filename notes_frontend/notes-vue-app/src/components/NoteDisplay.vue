<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import FileManager from './FileManager.vue'
import { useFileStore } from '../stores/files'

const props = defineProps({
  note: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: null },
  availableTags: { type: Array, default: () => [] },
})

const emit = defineEmits(['update', 'delete', 'retry', 'create-tag'])

const isEditing = ref(false)
const editContent = ref('')
const editTitle = ref('')
const editTags = ref([])
const textareaRef = ref(null)
const fileManagerRef = ref(null)
const editIsIdeaCandidate = ref(false)
const showExportMenu = ref(false)
const showNewTagForm = ref(false)
const newTagName = ref('')
const newTagColor = ref('#C9A9E8')
const creatingTag = ref(false)

const fileStore = useFileStore()

const loadFiles = async () => {
  if (props.note?.id) await fileStore.fetchNoteFiles(props.note.id)
}

onMounted(() => {
  loadFiles()
  window.addEventListener('click', closeExportMenu)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', closeExportMenu)
})

watch(() => props.note, (newNote) => {
  if (newNote?.id) loadFiles()
  else fileStore.clearCurrentFiles()
})

const closeExportMenu = (e) => {
  if (!e.target.closest('.export-menu-container')) showExportMenu.value = false
}

const quickColors = [
  '#FFB3B3','#FFD6A5','#FDFFB6','#CAFFBF','#9BF6FF','#A0C4FF',
  '#BDB2FF','#FFC6FF','#E4C1F9','#D8E2DC','#FDE2E4','#FAD2E1',
]

const startEditing = () => {
  editTitle.value = props.note?.title || ''
  editContent.value = props.note?.content || ''
  editTags.value = props.note?.tags?.map((t) => t.id) || []
  editIsIdeaCandidate.value = props.note?.is_idea_candidate || false
  isEditing.value = true
  showNewTagForm.value = false
  nextTick(() => { if (textareaRef.value) textareaRef.value.focus() })
}

const saveEditing = () => {
  const updates = {}
  if (editTitle.value !== props.note?.title) updates.title = editTitle.value
  if (editContent.value !== props.note?.content) updates.content = editContent.value
  const currentTagIds = props.note?.tags?.map((t) => t.id) || []
  if (JSON.stringify(editTags.value.sort()) !== JSON.stringify(currentTagIds.sort()))
    updates.tag_ids = editTags.value
  if (editIsIdeaCandidate.value !== props.note?.is_idea_candidate)
    updates.is_idea_candidate = editIsIdeaCandidate.value
  if (Object.keys(updates).length > 0) emit('update', updates)
  isEditing.value = false
  showNewTagForm.value = false
}

const cancelEditing = () => {
  isEditing.value = false
  editTitle.value = ''
  editContent.value = ''
  editTags.value = []
  showNewTagForm.value = false
}

const toggleTag = (tagId) => {
  const index = editTags.value.indexOf(tagId)
  if (index === -1) editTags.value.push(tagId)
  else editTags.value.splice(index, 1)
}

const triggerFileUpload = () => {
  if (fileManagerRef.value && typeof fileManagerRef.value.triggerFileInput === 'function')
    fileManagerRef.value.triggerFileInput()
}

const createNewTag = async () => {
  if (!newTagName.value.trim()) return
  creatingTag.value = true
  try {
    const newTag = await emit('create-tag', { name: newTagName.value.trim(), color: newTagColor.value })
    if (newTag) editTags.value.push(newTag.id)
    newTagName.value = ''
    newTagColor.value = '#C9A9E8'
    showNewTagForm.value = false
  } catch (error) {
    console.error('Ошибка создания тега:', error)
  } finally {
    creatingTag.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

const toggleExportMenu = () => { showExportMenu.value = !showExportMenu.value }

const getNoteText = () => {
  let text = `${props.note.title}\n\n${'='.repeat(props.note.title.length)}\n\n${props.note.content}\n\n`
  if (props.note.tags?.length) text += `Теги: ${props.note.tags.map((t) => '#' + t.name).join(', ')}\n`
  text += `\nСоздано: ${formatDate(props.note.creation_date)}\n`
  text += `Обновлено: ${formatDate(props.note.last_change_date)}\n`

  // Прикреплённые файлы
  const files = fileStore.currentNoteFiles
  if (files?.length) {
    text += `\nПрикреплённые файлы:\n`
    files.forEach(f => { text += `  - ${f.name} (${f.format.toUpperCase()}, ${formatFileSize(f.size)})\n` })
  }
  return text
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const exportToTxt = () => {
  const text = getNoteText()
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.note.title || 'заметка'}.txt`
  link.click()
  URL.revokeObjectURL(url)
  showExportMenu.value = false
}

// ── PDF: генерируем через jsPDF + html2canvas, файл скачивается сразу ──
const isPdfExporting = ref(false)

const exportToPdf = async () => {
  const note = props.note
  if (!note || isPdfExporting.value) return

  isPdfExporting.value = true
  showExportMenu.value = false

  try {
    // Динамически загружаем библиотеки только при первом вызове
    const [{ default: jsPDF }, { default: html2canvas }] = await Promise.all([
      import('jspdf'),
      import('html2canvas'),
    ])

    // Создаём временный div с контентом заметки
    const container = document.createElement('div')
    container.style.cssText = `
      position: fixed;
      top: -9999px;
      left: -9999px;
      width: 794px;
      background: white;
      font-family: Arial, sans-serif;
      color: #1a1a1a;
      padding: 48px;
      font-size: 15px;
      line-height: 1.7;
      box-sizing: border-box;
    `

    // Теги
    const tagsHtml = note.tags?.length
      ? note.tags.map(t =>
          `<span style="display:inline-block;padding:3px 10px;border-radius:20px;font-size:12px;
           font-weight:500;background:${t.color}20;color:${t.color};border:1px solid ${t.color};
           margin:2px 3px 2px 0">#${t.name}</span>`
        ).join('')
      : ''

    // Контент (экранируем HTML, переводим переносы)
    const contentSafe = (note.content || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\n/g, '<br>')

    // Файлы
    const files = fileStore.currentNoteFiles
    const filesHtml = files?.length
      ? `<div style="border-top:1px solid #e0e0e0;padding-top:16px;margin-top:24px">
          <div style="font-size:14px;font-weight:600;color:#666;margin-bottom:12px">Прикреплённые файлы</div>
          ${files.map(f => `
            <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #f0f0f0">
              <span style="font-size:16px">${f.format === 'pdf' ? '📄' : f.format === 'txt' ? '📝' : '🖼️'}</span>
              <span style="flex:1;font-size:14px;font-weight:500;color:#333">${f.name}</span>
              <span style="font-size:12px;color:#999">${f.format.toUpperCase()} · ${formatFileSize(f.size)}</span>
            </div>`).join('')}
        </div>`
      : ''

    container.innerHTML = `
      <div style="border-bottom:2px solid #c9a9e8;padding-bottom:16px;margin-bottom:20px">
        <div style="font-size:26px;font-weight:700;line-height:1.3;margin-bottom:12px;word-break:break-word">
          ${note.title || 'Без названия'}
        </div>
        ${tagsHtml ? `<div style="display:flex;flex-wrap:wrap;margin-bottom:10px">${tagsHtml}</div>` : ''}
        <div style="font-size:12px;color:#999;display:flex;gap:16px;flex-wrap:wrap">
          ${note.creation_date ? `<span>Создано: ${formatDate(note.creation_date)}</span>` : ''}
          ${note.last_change_date ? `<span>Изменено: ${formatDate(note.last_change_date)}</span>` : ''}
        </div>
      </div>
      <div style="font-size:15px;line-height:1.8;color:#333;word-break:break-word;margin-bottom:24px">
        ${contentSafe}
      </div>
      ${filesHtml}
    `

    document.body.appendChild(container)

    // Рендерим в canvas
    const canvas = await html2canvas(container, {
      scale: 2,          // Высокое разрешение
      useCORS: true,
      backgroundColor: '#ffffff',
      logging: false,
    })

    document.body.removeChild(container)

    // A4 в мм: 210 × 297
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pageW = pdf.internal.pageSize.getWidth()
    const pageH = pdf.internal.pageSize.getHeight()
    const margin = 0

    const imgW = pageW - margin * 2
    const imgH = (canvas.height * imgW) / canvas.width

    const imgData = canvas.toDataURL('image/jpeg', 0.95)

    // Если контент длиннее одной страницы — нарезаем
    if (imgH <= pageH) {
      pdf.addImage(imgData, 'JPEG', margin, margin, imgW, imgH)
    } else {
      let y = 0
      while (y < imgH) {
        if (y > 0) pdf.addPage()
        pdf.addImage(imgData, 'JPEG', margin, -(y), imgW, imgH)
        y += pageH
      }
    }

    const filename = `${(note.title || 'заметка').replace(/[\\/:*?"<>|]/g, '_')}.pdf`
    pdf.save(filename)

  } catch (err) {
    console.error('Ошибка экспорта PDF:', err)
    alert('Не удалось создать PDF. Попробуйте ещё раз.')
  } finally {
    isPdfExporting.value = false
  }
}

const escapeHtml = (text) => {
  if (!text) return ''
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
</script>

<template>
  <div class="note-display">
    <div v-if="loading" class="loading"><div class="spinner"></div></div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="$emit('retry')">Повторить</button>
    </div>
    <div v-else-if="!note" class="empty"><p>Заметка не найдена</p></div>

    <div v-else class="note-content">
      <div class="note-header">
        <div v-if="!isEditing" class="title-view">
          <h2 class="note-title">{{ note.title }}</h2>
        </div>
        <div v-else class="title-edit">
          <input v-model="editTitle" type="text" class="title-input" placeholder="Заголовок заметки" />
        </div>

        <div class="note-actions">
          <button v-if="!isEditing" class="attach-file-btn" title="Прикрепить файл" @click="triggerFileUpload">📎</button>

          <div v-if="!isEditing" class="export-menu-container">
            <button class="export-btn" title="Экспортировать" @click.stop="toggleExportMenu">📤</button>
            <div v-if="showExportMenu" class="export-menu" @click.stop>
              <button class="export-option" @click="exportToTxt">
                <span class="export-icon">📄</span>Сохранить как TXT
              </button>
              <button class="export-option" :disabled="isPdfExporting" @click="exportToPdf">
                <span class="export-icon">{{ isPdfExporting ? '⏳' : '📑' }}</span>
                {{ isPdfExporting ? 'Создаём PDF...' : 'Сохранить как PDF' }}
              </button>
            </div>
          </div>

          <button v-if="!isEditing" class="edit-btn" title="Редактировать" @click="startEditing">✏️</button>
          <button class="delete-btn" title="Удалить" @click="$emit('delete')">🗑️</button>
        </div>
      </div>

      <div v-if="!isEditing && note.is_idea_candidate" class="idea-badge-display">
        <span class="idea-icon">💡</span><span>Кандидат для идеи дня</span>
      </div>

      <div v-if="!isEditing && note.tags && note.tags.length > 0" class="tags-section">
        <div class="tags-label">Теги:</div>
        <div class="tags-list">
          <span v-for="tag in note.tags" :key="tag.id" class="tag"
            :style="{ backgroundColor: tag.color + '20', color: tag.color, borderColor: tag.color }">
            #{{ tag.name }}
          </span>
        </div>
      </div>

      <div v-if="isEditing" class="tags-edit-section">
        <div class="tags-edit-header">
          <label class="tags-label">Теги:</label>
          <button class="add-tag-inline-btn" type="button" @click="showNewTagForm = !showNewTagForm">
            {{ showNewTagForm ? '− Отмена' : '+ Новый тег' }}
          </button>
        </div>
        <div v-if="showNewTagForm" class="new-tag-inline-form">
          <div class="new-tag-inputs">
            <input v-model="newTagName" type="text" placeholder="Название тега" class="new-tag-name-input" @keyup.enter.prevent="createNewTag" />
            <div class="new-tag-color-picker">
              <input v-model="newTagColor" type="color" class="color-picker-input" />
              <div class="color-presets-mini">
                <button v-for="color in quickColors" :key="color" type="button" class="color-dot"
                  :style="{ backgroundColor: color }" @click="newTagColor = color"></button>
              </div>
            </div>
            <button :disabled="!newTagName.trim() || creatingTag" class="create-tag-inline-btn" @click="createNewTag">
              {{ creatingTag ? '...' : 'Создать' }}
            </button>
          </div>
        </div>
        <div v-if="availableTags.length > 0" class="tags-selector">
          <button v-for="tag in availableTags" :key="tag.id" type="button"
            :class="['tag-option', { selected: editTags.includes(tag.id) }]"
            :style="editTags.includes(tag.id)
              ? { backgroundColor: tag.color, borderColor: tag.color, color: 'white' }
              : { borderColor: tag.color, color: tag.color }"
            @click="toggleTag(tag.id)">
            #{{ tag.name }}
          </button>
        </div>
        <div v-else class="no-tags-hint">💡 Нет тегов. Создайте новый тег</div>
      </div>

      <div v-if="isEditing" class="idea-candidate-section">
        <label class="checkbox-label">
          <input v-model="editIsIdeaCandidate" type="checkbox" class="idea-checkbox" />
          <span class="checkbox-icon">💡</span>
          <span class="checkbox-text">Кандидат для "Идеи дня"</span>
        </label>
      </div>

      <div class="content-wrapper">
        <div v-if="!isEditing" class="content-view">
          <p class="content-text">{{ note.content || 'Нет содержания...' }}</p>
        </div>
        <div v-else class="content-edit">
          <textarea ref="textareaRef" v-model="editContent" class="content-textarea"
            placeholder="Введите содержание заметки..." rows="10"></textarea>
          <div class="edit-actions">
            <button class="cancel-edit-btn" @click="cancelEditing">Отмена</button>
            <button class="save-edit-btn" @click="saveEditing">Сохранить</button>
          </div>
        </div>
      </div>

      <div v-if="!isEditing" class="files-section">
        <div class="files-header"><h3 class="files-title">Прикреплённые файлы</h3></div>
        <FileManager ref="fileManagerRef" :note-id="note.id" />
      </div>

      <div class="note-footer">
        <span v-if="note.creation_date" class="date">Создано: {{ formatDate(note.creation_date) }}</span>
        <span v-if="note.last_change_date" class="date">Обновлено: {{ formatDate(note.last_change_date) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.note-display { max-width: 800px; margin: 0 auto; padding: 20px; }
.loading { text-align: center; padding: 40px; }
.spinner {
  display: inline-block; width: 40px; height: 40px;
  border: 3px solid var(--border-light, #f3f3f3);
  border-top: 3px solid var(--primary-color, #c9a9e8);
  border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { 0%{transform:rotate(0deg)} 100%{transform:rotate(360deg)} }
.error,.empty { text-align: center; padding: 40px; color: var(--text-secondary, #666); }
.error { color: var(--danger-color, #dc3545); }
.retry-btn {
  margin-top: 12px; padding: 8px 20px; background: var(--primary-color, #c9a9e8);
  color: white; border: none; border-radius: 8px; cursor: pointer;
}
.note-content {
  background: var(--bg-primary, white); border-radius: 16px;
  box-shadow: var(--card-shadow, 0 2px 8px rgba(0,0,0,0.05));
  overflow: hidden; border: 1px solid var(--border-color, #e0e0e0);
}
.note-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 24px; border-bottom: 1px solid var(--border-color, #e0e0e0);
  background: var(--bg-primary, white); gap: 16px;
}
.title-view { flex: 1; min-width: 0; }
.note-title {
  font-size: 26px; font-weight: 700; color: var(--text-primary, #1a1a1a);
  line-height: 1.3; word-break: break-word; margin: 0;
}
.title-edit { flex: 1; }
.title-input {
  width: 100%; font-size: 22px; font-weight: 700; border: 2px solid var(--primary-color, #c9a9e8);
  border-radius: 8px; padding: 8px 12px; background: var(--bg-primary, white);
  color: var(--text-primary, #333); font-family: inherit;
}
.title-input:focus { outline: none; }
.note-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.attach-file-btn,.export-btn,.edit-btn,.delete-btn {
  background: none; border: none; font-size: 18px; cursor: pointer;
  padding: 6px; border-radius: 8px; transition: all 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.attach-file-btn:hover { background: var(--hover-bg, #f5f5f5); }
.export-btn:hover { background: var(--hover-bg, #f5f5f5); }
.edit-btn:hover { background: var(--primary-light, #f0e6ff); }
.delete-btn:hover { background: var(--danger-bg, #fee); }
.export-menu-container { position: relative; }
.export-menu {
  position: absolute; top: calc(100% + 4px); right: 0;
  background: var(--bg-primary, white); border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  min-width: 200px; z-index: 100; overflow: hidden;
}
.export-option {
  display: flex; align-items: center; gap: 10px; width: 100%;
  padding: 12px 16px; background: none; border: none; cursor: pointer;
  font-size: 14px; color: var(--text-primary, #333); text-align: left; transition: all 0.15s;
}
.export-option:hover { background: var(--hover-bg, #f5f5f5); }
.export-icon { font-size: 16px; }
.idea-badge-display {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 24px; background: var(--active-bg, #f0e6ff);
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  font-size: 14px; color: var(--primary-color, #5700b3);
}
.idea-badge-display .idea-icon { font-size: 18px; }
.tags-section,.tags-edit-section {
  padding: 16px 24px; border-bottom: 1px solid var(--border-color, #e0e0e0);
  background: var(--bg-tertiary, #fafafa);
}
.tags-label { font-size: 14px; font-weight: 500; color: var(--text-secondary, #666); margin-bottom: 8px; }
.tags-list { display: flex; flex-wrap: wrap; gap: 8px; }
.tag {
  display: inline-block; padding: 6px 14px; border-radius: 20px;
  font-size: 14px; font-weight: 500; border: 1px solid;
}
.tags-edit-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.add-tag-inline-btn {
  background: none; border: 1.5px dashed var(--primary-color, #c9a9e8);
  padding: 4px 12px; border-radius: 16px; font-size: 12px;
  color: var(--primary-color, #c9a9e8); cursor: pointer; transition: all 0.2s; font-weight: 500;
}
.add-tag-inline-btn:hover { background: var(--primary-light, #f0e6ff); border-style: solid; }
.new-tag-inline-form { background: var(--bg-secondary, #f8f9fa); border-radius: 10px; padding: 12px; margin-bottom: 16px; }
.new-tag-inputs { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.new-tag-name-input {
  flex: 1; min-width: 150px; padding: 8px 12px;
  border: 1.5px solid var(--border-color, #e0e0e0); border-radius: 8px; font-size: 13px;
  background: var(--bg-primary, white); color: var(--text-primary, #333);
}
.new-tag-name-input:focus { outline: none; border-color: var(--primary-color, #c9a9e8); }
.new-tag-color-picker { display: flex; align-items: center; gap: 6px; }
.color-picker-input { width: 36px; height: 36px; padding: 2px; border: 1.5px solid var(--border-color, #e0e0e0); border-radius: 8px; cursor: pointer; background: var(--bg-primary, white); }
.color-presets-mini { display: flex; gap: 3px; }
.color-dot { width: 20px; height: 20px; border-radius: 50%; border: 2px solid var(--bg-primary, white); cursor: pointer; transition: transform 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.color-dot:hover { transform: scale(1.15); }
.create-tag-inline-btn { padding: 8px 16px; background: var(--primary-color, #c9a9e8); color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.create-tag-inline-btn:hover:not(:disabled) { background: var(--primary-hover, #b794d4); }
.create-tag-inline-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.tags-selector { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.tag-option { background: var(--bg-primary, white); border: 2px solid; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
.tag-option:hover { transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.tag-option.selected { color: white !important; }
.no-tags-hint { color: var(--text-tertiary, #999); font-size: 14px; font-style: italic; padding: 8px 0; }
.idea-candidate-section { padding: 16px 24px; border-bottom: 1px solid var(--border-color, #e0e0e0); background: var(--bg-tertiary, #fafafa); }
.checkbox-label { display: flex; align-items: center; gap: 12px; cursor: pointer; padding: 12px 16px; border: 2px solid var(--border-color, #e0e0e0); border-radius: 12px; transition: all 0.2s; background: var(--bg-primary, white); }
.checkbox-label:hover { border-color: var(--primary-color, #c9a9e8); background: var(--primary-light, #f8f4ff); }
.idea-checkbox { width: 20px; height: 20px; cursor: pointer; accent-color: var(--primary-color, #c9a9e8); margin: 0; flex-shrink: 0; }
.checkbox-icon { font-size: 20px; line-height: 1; flex-shrink: 0; }
.checkbox-text { font-weight: 500; color: var(--text-primary, #333); }
.content-wrapper { padding: 24px; min-height: 300px; }
.content-view { padding: 20px; border-radius: 12px; background: var(--bg-primary, white); }
.content-text { font-size: 16px; line-height: 1.6; color: var(--text-primary, #333); white-space: pre-wrap; word-break: break-word; margin: 0; }
.content-edit { display: flex; flex-direction: column; gap: 16px; }
.content-textarea { width: 100%; padding: 16px; border: 2px solid var(--primary-color, #c9a9e8); border-radius: 12px; font-size: 16px; line-height: 1.6; font-family: inherit; resize: vertical; background: var(--bg-primary, white); color: var(--text-primary, #333); }
.content-textarea:focus { outline: none; border-color: var(--primary-hover, #b794d4); }
.edit-actions { display: flex; justify-content: flex-end; gap: 12px; }
.cancel-edit-btn,.save-edit-btn { padding: 8px 20px; border-radius: 8px; border: none; cursor: pointer; font-size: 14px; transition: all 0.2s; }
.cancel-edit-btn { background: var(--bg-tertiary, #f5f5f5); color: var(--text-secondary, #666); }
.cancel-edit-btn:hover { background: var(--border-color, #e0e0e0); }
.save-edit-btn { background: var(--primary-color, #c9a9e8); color: white; }
.save-edit-btn:hover { background: var(--primary-hover, #b794d4); }
.files-section { padding: 20px 24px 24px; border-top: 1px solid var(--border-color, #e0e0e0); }
.files-header { margin-bottom: 16px; }
.files-title { margin: 0; font-size: 16px; font-weight: 500; color: var(--text-primary, #333); }
.note-footer { padding: 16px 24px; border-top: 1px solid var(--border-color, #e0e0e0); background: var(--bg-tertiary, #fafafa); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.date { font-size: 12px; color: var(--text-tertiary, #999); }

@media (max-width: 640px) {
  .note-display { padding: 10px; }
  .note-header { padding: 16px; }
  .note-title { font-size: 22px; }
  .title-input { font-size: 18px; }
  .content-wrapper { padding: 16px; }
}
</style>