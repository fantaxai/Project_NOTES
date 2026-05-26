<template>
  <div class="notes-list-page">
    <!-- Верхняя секция: Идея дня слева + Чеклист справа -->
    <div class="top-section">
      <!-- Левая колонка -->
      <div ref="leftColumnRef" class="left-column">
        <div class="idea-section">
          <IdeaOfDay />
        </div>
        <div class="tags-section-inline">
          <div class="tags-section-header">
            <span class="section-icon">🏷️</span>
            <h3 class="section-title">Теги</h3>
            <div class="section-actions">
              <button
                class="mini-action-btn"
                title="Управление тегами"
                @click="openManageTagsModal"
              >
                ✏️
              </button>
              <button
                class="mini-action-btn"
                :class="{ active: showTagSelector }"
                title="Выбрать теги"
                @click="showTagSelector = !showTagSelector"
              >
                {{ showTagSelector ? '✓' : '➕' }}
              </button>
            </div>
          </div>

          <!-- Частые теги -->
          <div v-if="popularTags.length > 0" class="popular-tags-inline">
            <button
              v-for="tag in popularTags"
              :key="tag.id"
              :class="['popular-tag', { active: selectedTagIds.includes(tag.id) }]"
              :style="
                selectedTagIds.includes(tag.id)
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
              @click="toggleTagFilter(tag.id)"
            >
              #{{ tag.name }}
              <span class="tag-count">{{ tag.note_count }}</span>
            </button>
          </div>

          <!-- Выбранные теги -->
          <div v-if="selectedTagIds.length > 0" class="selected-tags-inline">
            <button
              v-for="tagId in selectedTagIds"
              :key="tagId"
              class="selected-tag"
              :style="{
                backgroundColor: getTagById(tagId)?.color,
                borderColor: getTagById(tagId)?.color,
                color: 'white',
              }"
              @click="toggleTagFilter(tagId)"
            >
              #{{ getTagById(tagId)?.name }}
              <span class="remove-icon">×</span>
            </button>
            <button class="clear-tags-btn" title="Сбросить фильтр" @click="clearTagFilters">
              ✕ Сбросить
            </button>
          </div>

          <!-- Режим фильтрации -->
          <div class="filter-mode-inline">
            <span class="mode-label">Режим:</span>
            <button
              :class="['mode-btn', { active: filterMode === 'and' }]"
              @click="filterMode = 'and'"
            >
              И
            </button>
            <button
              :class="['mode-btn', { active: filterMode === 'or' }]"
              @click="filterMode = 'or'"
            >
              ИЛИ
            </button>
          </div>

          <!-- Выпадающий список тегов -->
          <div v-if="showTagSelector" class="tag-selector-inline">
            <input
              v-model="tagSearchQuery"
              type="text"
              placeholder="🔍 Поиск тега..."
              class="tag-search-input"
            />
            <div class="all-tags-grid">
              <button
                v-for="tag in filteredAllTags"
                :key="tag.id"
                :class="['tag-selector-item', { active: selectedTagIds.includes(tag.id) }]"
                :style="
                  selectedTagIds.includes(tag.id)
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
                @click="toggleTagFilter(tag.id)"
              >
                #{{ tag.name }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Правая колонка - Чеклист -->
      <div
        class="right-column"
        :style="{
          maxHeight: leftColumnHeight ? leftColumnHeight + 'px' : 'none',
          height: leftColumnHeight ? leftColumnHeight + 'px' : 'auto',
        }"
      >
        <div class="checklist-preview">
          <ChecklistDisplay />
        </div>
      </div>
    </div>

    <!-- Панель сортировки и поиска -->
    <div class="controls-panel">
      <div class="search-wrapper">
        <input
          :value="searchQuery"
          type="text"
          placeholder="🔍 Поиск по идеям и тегам..."
          class="search-input"
          @input="handleSearch"
        />
        <div v-if="searchQuery" class="search-info">Найдено идей: {{ filteredNotes.length }}</div>
      </div>

      <div class="sort-controls">
        <span class="sort-label">Сортировка:</span>
        <button
          class="sort-btn"
          :class="{ active: sortOrder === 'newest' }"
          @click="setSortOrder('newest')"
        >
          📅 Новые
        </button>
        <button
          class="sort-btn"
          :class="{ active: sortOrder === 'oldest' }"
          @click="setSortOrder('oldest')"
        >
          📅 Старые
        </button>
      </div>
    </div>

    <!-- Состояния загрузки/ошибки/пустоты -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка идей...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>😕 {{ error }}</p>
      <button class="retry-btn" @click="fetchNotes">Попробовать снова</button>
    </div>

    <div v-else-if="filteredNotes.length === 0" class="empty-state">
      <div class="empty-icon">{{ searchQuery ? '🔍' : '💭' }}</div>
      <h2 class="empty-title">
        {{
          selectedTagIds.length > 0
            ? 'Нет идей с выбранными тегами'
            : searchQuery
              ? 'Ничего не найдено'
              : 'Нет идей'
        }}
      </h2>
      <p class="empty-text">
        {{
          selectedTagIds.length > 0
            ? 'Попробуйте выбрать другие теги'
            : searchQuery
              ? 'Попробуйте изменить поисковый запрос'
              : 'Создайте свою первую идею'
        }}
      </p>
      <router-link
        v-if="!searchQuery && selectedTagIds.length === 0"
        to="/create"
        class="create-first-btn"
      >
        Создать идею
      </router-link>
    </div>

    <!-- Сетка заметок -->
    <div v-else class="notes-container">
      <div v-if="deleteError" class="delete-error">
        {{ deleteError }}
      </div>

      <div class="notes-grid">
        <div
          v-for="note in filteredNotes"
          :key="note.id"
          class="note-card"
          @click="goToNote(note.id)"
        >
          <div class="note-header">
            <div class="card-title-wrapper">
              <h3 class="note-title" v-html="highlightText(truncateTitle(note.title))"></h3>
              <div class="card-icons">
                <span
                  v-if="note.is_idea_candidate"
                  class="candidate-icon"
                  title="Кандидат для идеи дня"
                >
                  💡
                </span>
                <span
                  v-if="notesWithFiles.has(note.id)"
                  class="attachment-icon"
                  title="Есть прикрепленные файлы"
                >
                  📎
                </span>
              </div>
            </div>
            <button
              class="delete-btn"
              title="Удалить идею"
              :disabled="isDeleting"
              @click.stop="handleDelete(note.id)"
            >
              {{ isDeleting ? '...' : '✕' }}
            </button>
          </div>

          <p class="note-preview" v-html="highlightText(getFormattedPreview(note.content))"></p>

          <div v-if="note.tags && note.tags.length" class="note-tags">
            <button
              v-for="tag in note.tags.slice(0, 3)"
              :key="tag.id"
              class="note-tag"
              :style="{
                backgroundColor: tag.color + '20',
                color: tag.color,
                borderColor: tag.color,
              }"
              @click.stop="selectSingleTag(tag.id)"
            >
              <span v-html="highlightText('#' + tag.name)"></span>
            </button>
            <span v-if="note.tags.length > 3" class="tag-more"> +{{ note.tags.length - 3 }} </span>
          </div>

          <div class="note-footer">
            <span class="note-date">{{
              formatDate(note.creation_date || note.last_change_date)
            }}</span>
            <span class="read-more">Читать →</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно управления тегами -->
    <div v-if="showManageTagsModal" class="modal-overlay" @click="closeManageTagsModal">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header">
          <h3>Управление тегами</h3>
          <button class="close-btn" @click="closeManageTagsModal">×</button>
        </div>

        <div class="manage-tags-content">
          <div class="manage-tags-header">
            <input
              v-model="manageTagSearchQuery"
              type="text"
              placeholder="🔍 Поиск тега..."
              class="tag-search-input"
            />
            <button class="add-tag-manage-btn" @click="openCreateTagModal">+ Новый тег</button>
          </div>

          <div class="manage-tags-list">
            <div v-if="filteredManageTags.length === 0" class="no-tags-found">Теги не найдены</div>

            <div v-for="tag in filteredManageTags" :key="tag.id" class="manage-tag-item">
              <div class="manage-tag-info">
                <span class="tag-color-dot" :style="{ backgroundColor: tag.color }"></span>
                <span class="tag-name">{{ tag.name }}</span>
                <span class="tag-notes-count">{{ getTagNotesCount(tag.id) }} идей</span>
              </div>
              <div class="manage-tag-actions">
                <button class="edit-tag-manage-btn" title="Редактировать" @click="editTag(tag)">
                  ✏️
                </button>
                <button
                  class="delete-tag-manage-btn"
                  title="Удалить"
                  :disabled="deletingTagId === tag.id"
                  @click="deleteTag(tag)"
                >
                  {{ deletingTagId === tag.id ? '...' : '🗑️' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования/создания тега -->
    <div v-if="showEditTagModal" class="modal-overlay" @click="closeEditTagModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingTag ? 'Редактировать тег' : 'Новый тег' }}</h3>
          <button class="close-btn" @click="closeEditTagModal">×</button>
        </div>

        <div class="form-body">
          <div class="form-group">
            <label for="editTagName">Название тега</label>
            <input
              id="editTagName"
              v-model="editTagName"
              type="text"
              placeholder="Введите название тега"
              class="tag-input"
              autofocus
              required
            />
          </div>

          <div class="form-group">
            <label for="editTagColor">Цвет тега</label>
            <div class="color-picker-container">
              <input id="editTagColor" v-model="editTagColor" type="color" class="color-input" />
              <input
                v-model="editTagColor"
                type="text"
                placeholder="#RRGGBB"
                class="color-text"
                pattern="^#[0-9A-Fa-f]{6}$"
              />
            </div>
            <div class="color-presets">
              <button
                v-for="color in quickColors"
                :key="color"
                type="button"
                class="color-preset"
                :style="{ backgroundColor: color }"
                @click="editTagColor = color"
              ></button>
            </div>
          </div>

          <div v-if="editTagError" class="error-message">
            {{ editTagError }}
          </div>

          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeEditTagModal">Отмена</button>
            <button type="button" :disabled="!editTagName.trim() || savingTag" class="save-btn" @click="saveTag">
              {{ savingTag ? 'Сохранение...' : editingTag ? 'Сохранить' : 'Создать' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useNoteListStore } from '../stores/notelist'
import { useTagStore } from '../stores/tags'
import { useFileStore } from '../stores/files'
import IdeaOfDay from '../components/IdeaOfDay.vue'
import ChecklistDisplay from '../components/ChecklistDisplay.vue'
import { useChecklistStore } from '../stores/checklist'

const router = useRouter()
const route = useRoute()
const noteListStore = useNoteListStore()
const tagStore = useTagStore()
const fileStore = useFileStore()
const checklistStore = useChecklistStore()

// Состояние для файлов
const notesWithFiles = ref(new Set())
const isDeleting = ref(false)
const deleteError = ref(null)

// Состояние фильтрации
const selectedTagIds = ref([])
const filterMode = ref('or')
const showTagSelector = ref(false)
const tagSearchQuery = ref('')

// Состояния для управления тегами
const showManageTagsModal = ref(false)
const showEditTagModal = ref(false)
const manageTagSearchQuery = ref('')
const editingTag = ref(null)
const editTagName = ref('')
const editTagColor = ref('#C9A9E8')
const savingTag = ref(false)
const editTagError = ref(null)
const deletingTagId = ref(null)
const leftColumnRef = ref(null)
const leftColumnHeight = ref(0)
let resizeObserver = null

const updateLeftColumnHeight = () => {
  if (leftColumnRef.value) {
    leftColumnHeight.value = leftColumnRef.value.offsetHeight
  }
}

const setupResizeObserver = () => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }

  if (leftColumnRef.value) {
    // Оборачиваем в requestAnimationFrame для предотвращения ошибки
    resizeObserver = new ResizeObserver((entries) => {
      // Используем debounce через requestAnimationFrame
      window.requestAnimationFrame(() => {
        if (!Array.isArray(entries) || !entries.length) {
          return
        }
        updateLeftColumnHeight()
      })
    })
    resizeObserver.observe(leftColumnRef.value)
  }
}

const quickColors = [
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

// Ключ для localStorage
const STORAGE_KEY = 'notelist_filters'

// Проверка наличия файлов для всех заметок
const checkFilesForNotes = async () => {
  const uncheckedNotes = allNotes.value.filter((note) => !notesWithFiles.value.has(note.id))

  for (const note of uncheckedNotes) {
    try {
      const hasFiles = await fileStore.checkNoteHasFiles(note.id)
      if (hasFiles) {
        notesWithFiles.value.add(note.id)
      }
    } catch (err) {
      console.error(`Ошибка проверки файлов для заметки ${note.id}:`, err)
    }
  }
}

// Сохранение фильтров в localStorage
const saveFiltersToStorage = () => {
  const filters = {
    selectedTagIds: selectedTagIds.value,
    filterMode: filterMode.value,
    searchQuery: searchQuery.value,
    sortOrder: sortOrder.value,
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(filters))
}

// Загрузка фильтров из localStorage
const loadFiltersFromStorage = () => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    try {
      const filters = JSON.parse(saved)
      selectedTagIds.value = filters.selectedTagIds || []
      filterMode.value = filters.filterMode || 'or'
      if (filters.searchQuery) {
        noteListStore.setSearchQuery(filters.searchQuery)
      }
      if (filters.sortOrder) {
        noteListStore.setSortOrder(filters.sortOrder)
      }
    } catch (e) {
      console.error('Ошибка загрузки фильтров:', e)
    }
  }
}

// Инициализация из URL
const initFromUrl = () => {
  const tagsParam = route.query.tags
  const modeParam = route.query.mode

  if (tagsParam) {
    selectedTagIds.value = tagsParam.split(',').map(Number)
  } else {
    loadFiltersFromStorage()
  }

  if (modeParam && (modeParam === 'and' || modeParam === 'or')) {
    filterMode.value = modeParam
  }
}

// Синхронизация фильтров с URL
watch(
  () => route.query,
  (newQuery) => {
    const tagsParam = newQuery.tags
    const modeParam = newQuery.mode

    if (tagsParam) {
      const tagIds = tagsParam.split(',').map(Number)
      if (JSON.stringify(tagIds) !== JSON.stringify(selectedTagIds.value)) {
        selectedTagIds.value = tagIds
      }
    } else if (selectedTagIds.value.length > 0) {
      selectedTagIds.value = []
    }

    if (modeParam && (modeParam === 'and' || modeParam === 'or')) {
      if (filterMode.value !== modeParam) {
        filterMode.value = modeParam
      }
    } else if (filterMode.value !== 'or') {
      filterMode.value = 'or'
    }
  },
  { immediate: true }
)

// При изменении фильтров обновляем URL и localStorage
watch([selectedTagIds, filterMode], () => {
  const query = { ...route.query }

  if (selectedTagIds.value.length > 0) {
    query.tags = selectedTagIds.value.join(',')
  } else {
    delete query.tags
  }

  if (filterMode.value !== 'or') {
    query.mode = filterMode.value
  } else {
    delete query.mode
  }

  saveFiltersToStorage()

  const currentTags = route.query.tags
  const currentMode = route.query.mode
  const newTags = query.tags
  const newMode = query.mode

  if (currentTags !== newTags || currentMode !== newMode) {
    router.replace({ query })
  }
})

// Получаем данные из сторов
const allNotes = computed(() => noteListStore.notes)
const loading = computed(() => noteListStore.loading || tagStore.loading)
const error = computed(() => noteListStore.error || tagStore.error)
const searchQuery = computed(() => noteListStore.searchQuery)
const sortOrder = computed(() => noteListStore.sortOrder)
//const totalCount = computed(() => noteListStore.totalCount)

// Все теги из стора
const allTags = computed(() => tagStore.tags)

watch(
  () => [allNotes.value, allTags.value],
  () => {
    nextTick(() => {
      updateLeftColumnHeight()
      setupResizeObserver()
    })
  },
  { deep: true }
)

// Отфильтрованные теги для селектора
const filteredAllTags = computed(() => {
  if (!tagSearchQuery.value.trim()) return allTags.value

  const query = tagSearchQuery.value.toLowerCase().trim()
  return allTags.value.filter((tag) => tag.name.toLowerCase().includes(query))
})

// Получить тег по ID
const getTagById = (id) => {
  return allTags.value.find((t) => t.id === id)
}

// Теги, соответствующие поисковому запросу
const matchingTags = computed(() => {
  if (!searchQuery.value.trim()) return []

  const query = searchQuery.value.toLowerCase().trim()
  return allTags.value.filter((tag) => tag.name.toLowerCase().includes(query))
})

// Популярные теги
const popularTags = computed(() => {
  const tagCounts = {}

  allNotes.value.forEach((note) => {
    if (note.tags) {
      note.tags.forEach((tag) => {
        if (!tagCounts[tag.id]) {
          tagCounts[tag.id] = { ...tag, note_count: 0 }
        }
        tagCounts[tag.id].note_count++
      })
    }
  })

  return Object.values(tagCounts)
    .sort((a, b) => b.note_count - a.note_count)
    .slice(0, 8)
})

// Сортированные заметки
const sortedAllNotes = computed(() => {
  const notesToSort = [...allNotes.value]

  return notesToSort.sort((a, b) => {
    const dateA = new Date(a.creation_date || a.last_change_date || 0)
    const dateB = new Date(b.creation_date || b.last_change_date || 0)

    return sortOrder.value === 'newest' ? dateB - dateA : dateA - dateB
  })
})

// Фильтрованные заметки
const filteredNotes = computed(() => {
  let result = sortedAllNotes.value

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    const matchingTagIds = matchingTags.value.map((t) => t.id)

    result = result.filter((note) => {
      const textMatch =
        note.title?.toLowerCase().includes(query) || note.content?.toLowerCase().includes(query)

      const noteTagIds = note.tags?.map((t) => t.id) || []
      const tagMatch = matchingTagIds.some((id) => noteTagIds.includes(id))

      return textMatch || tagMatch
    })
  }

  if (selectedTagIds.value.length > 0) {
    if (filterMode.value === 'and') {
      result = result.filter((note) => {
        const noteTagIds = note.tags?.map((t) => t.id) || []
        return selectedTagIds.value.every((id) => noteTagIds.includes(id))
      })
    } else {
      result = result.filter((note) => {
        const noteTagIds = note.tags?.map((t) => t.id) || []
        return selectedTagIds.value.some((id) => noteTagIds.includes(id))
      })
    }
  }

  return result
})

// Отслеживание изменений заметок для проверки файлов
watch(
  () => allNotes.value,
  async () => {
    await checkFilesForNotes()
  }
)

const highlightText = (text) => {
  if (!searchQuery.value.trim() || !text) return text

  const query = searchQuery.value.trim()
  const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi')

  return text.replace(regex, '<mark class="search-highlight">$1</mark>')
}

const escapeRegExp = (string) => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

const toggleTagFilter = (tagId) => {
  const index = selectedTagIds.value.indexOf(tagId)
  if (index === -1) {
    selectedTagIds.value.push(tagId)
  } else {
    selectedTagIds.value.splice(index, 1)
  }
}

// Обрезка заголовка до 25 символов
const truncateTitle = (title) => {
  if (!title) return 'Без названия'
  return title.length > 25 ? title.substring(0, 25) + '...' : title
}

// Обрезка содержания: первые 3 строки, в каждой строке до 30 символов
const truncateContent = (content) => {
  if (!content) return 'Нет содержания'
  
  let text = content.replace(/<[^>]*>/g, '')
  
  const lines = text.split('\n')
  
  const truncatedLines = lines.slice(0, 3).map(line => {
    if (line.length > 30) {
      return line.substring(0, 30) + '...'
    }
    return line
  })

  return truncatedLines.join('\n')
}

const getFormattedPreview = (content) => {
  const truncated = truncateContent(content)
  return truncated.replace(/\n/g, '<br>')
}

const selectSingleTag = (tagId) => {
  selectedTagIds.value = [tagId]
  filterMode.value = 'or'
  showTagSelector.value = false
}

const clearTagFilters = () => {
  selectedTagIds.value = []
}

const setSortOrder = (order) => {
  noteListStore.setSortOrder(order)
}

const handleSearch = (event) => {
  noteListStore.setSearchQuery(event.target.value)
}

const handleDelete = async (id) => {
  if (!confirm('Вы уверены, что хотите удалить эту идею?')) return

  isDeleting.value = true
  deleteError.value = null

  try {
    await noteListStore.deleteNoteAndUpdateList(id)
    notesWithFiles.value.delete(id)
  } catch (err) {
    deleteError.value = 'Не удалось удалить заметку'
    console.error('Ошибка удаления:', err)
  } finally {
    isDeleting.value = false
  }
}

const goToNote = (id) => {
  saveFiltersToStorage()
  router.push(`/note/${id}`)
}

const fetchNotes = async () => {
  try {
    await Promise.all([noteListStore.fetchNotes(), tagStore.fetchTags()])
    await checkFilesForNotes()
    nextTick(() => {
      updateLeftColumnHeight()
    })
  } catch (err) {
    console.error('Ошибка загрузки:', err)
  }
}

// Отфильтрованные теги для управления
const filteredManageTags = computed(() => {
  if (!manageTagSearchQuery.value.trim()) return allTags.value

  const query = manageTagSearchQuery.value.toLowerCase().trim()
  return allTags.value.filter((tag) => tag.name.toLowerCase().includes(query))
})

// Получить количество заметок для тега
const getTagNotesCount = (tagId) => {
  return allNotes.value.filter((note) => note.tags?.some((t) => t.id === tagId)).length
}

// Открыть модальное окно управления тегами
const openManageTagsModal = () => {
  showManageTagsModal.value = true
  manageTagSearchQuery.value = ''
}

// Закрыть модальное окно управления тегами
const closeManageTagsModal = () => {
  showManageTagsModal.value = false
  manageTagSearchQuery.value = ''
}

// Открыть модальное окно создания тега
const openCreateTagModal = () => {
  editingTag.value = null
  editTagName.value = ''
  editTagColor.value = '#C9A9E8'
  editTagError.value = null
  showEditTagModal.value = true
}

// Редактировать тег
const editTag = (tag) => {
  editingTag.value = tag
  editTagName.value = tag.name
  editTagColor.value = tag.color
  editTagError.value = null
  showEditTagModal.value = true
}

// Закрыть модальное окно редактирования
const closeEditTagModal = () => {
  showEditTagModal.value = false
  editingTag.value = null
  editTagName.value = ''
  editTagColor.value = '#C9A9E8'
  editTagError.value = null
  showManageTagsModal.value = true
}

// Сохранить тег
const saveTag = async () => {
  if (!editTagName.value.trim()) return

  savingTag.value = true
  editTagError.value = null

  try {
    if (editingTag.value) {
      await tagStore.updateTag(editingTag.value.id, {
        name: editTagName.value.trim(),
        color: editTagColor.value,
      })
    } else {
      await tagStore.createTag({
        name: editTagName.value.trim(),
        color: editTagColor.value,
      })
    }

    await tagStore.fetchTags()
    await noteListStore.fetchNotes()  
    closeEditTagModal()
  } catch (err) {
    editTagError.value = err.response?.data?.detail || 'Ошибка сохранения тега'
  } finally {
    savingTag.value = false
  }
}

// Удалить тег
const deleteTag = async (tag) => {
  const notesCount = getTagNotesCount(tag.id)
  let confirmMessage = `Удалить тег "${tag.name}"?`

  if (notesCount > 0) {
    confirmMessage += `\n\nВнимание! Этот тег используется в ${notesCount} ${getPluralForm(notesCount, ['идее', 'идеях', 'идеях'])}.`
  }

  if (!confirm(confirmMessage)) return

  deletingTagId.value = tag.id

  try {
    await tagStore.deleteTag(tag.id)

    const index = selectedTagIds.value.indexOf(tag.id)
    if (index !== -1) {
      selectedTagIds.value.splice(index, 1)
    }

    await tagStore.fetchTags()
  } catch (err) {
    alert('Ошибка удаления тега: ' + (err.response?.data?.detail || err.message))
  } finally {
    deletingTagId.value = null
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''

  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const noteDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffTime = today - noteDate
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

  const timeStr = date.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })

  if (diffDays === 0) return `Сегодня в ${timeStr}`
  if (diffDays === 1) return `Вчера в ${timeStr}`
  if (diffDays < 7) return `${diffDays} дн. назад в ${timeStr}`

  return (
    date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
    }) + ` в ${timeStr}`
  )
}

const getPluralForm = (number, forms) => {
  const n = Math.abs(number) % 100
  const n1 = n % 10

  if (n > 10 && n < 20) return forms[2]
  if (n1 > 1 && n1 < 5) return forms[1]
  if (n1 === 1) return forms[0]
  return forms[2]
}

onMounted(() => {
  initFromUrl()
  fetchNotes()
  checklistStore.fetchChecklists()
  nextTick(() => {
    updateLeftColumnHeight()
    setupResizeObserver()
  })
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
})
</script>

<style scoped>
.notes-list-page {
  min-height: 100vh;
  background: var(--bg-secondary, #f5f5f5);
  padding-bottom: 40px;
}

/* Верхняя секция - две колонки одинаковой высоты */
.top-section {
  display: flex;
  gap: 16px;
  margin: 16px 24px;
  align-items: flex-start;
} 

@media (max-width: 768px) {
  .top-section {
    flex-direction: column;
    margin: 16px;
  }
  
  .right-column {
    min-width: auto;
  }
}

.left-column {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.right-column {
  flex: 1;
  display: flex;
  min-width: 280px;
  overflow: hidden;
  align-self: flex-start;
}

/* Идея дня */
.idea-section {
  background: transparent;
}

/* Теги внутри левой колонки */
.tags-section-inline {
  background: var(--bg-primary, white);
  border-radius: 16px;
  padding: 16px;
  box-shadow: var(--card-shadow, 0 2px 8px rgba(0, 0, 0, 0.05));
  border: 1px solid var(--border-color, #e0e0e0);
  flex: 1;
}

/* Мобильная версия */
@media (max-width: 768px) {
  .tags-section-inline {
    padding: 10px 12px;
  }
}


.tags-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.section-icon {
  font-size: 18px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
}

.section-actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.mini-action-btn {
  background: none;
  border: 1px solid var(--border-color, #e0e0e0);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary, #666);
}

.mini-action-btn:hover {
  background: var(--hover-bg, #f5f5f5);
  border-color: var(--primary-color, #c9a9e8);
}

.mini-action-btn.active {
  background: var(--primary-color, #c9a9e8);
  border-color: var(--primary-color, #c9a9e8);
  color: white;
}

/* Частые теги */
.popular-tags-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.popular-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-primary, white);
  border: 2px solid;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.popular-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.popular-tag.active {
  color: white !important;
}

.tag-count {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
}

/* Выбранные теги */
.selected-tags-inline {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.selected-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-primary, white);
  border: 2px solid;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  color: white !important;
}

.selected-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.remove-icon {
  font-size: 16px;
  line-height: 1;
  opacity: 0.8;
  margin-left: 4px;
}

.clear-tags-btn {
  background: none;
  border: 1px solid var(--danger-color, #dc3545);
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 12px;
  color: var(--danger-color, #dc3545);
  cursor: pointer;
  transition: all 0.2s;
  margin-left: auto;
}

.clear-tags-btn:hover {
  background: var(--danger-bg, #fee);
}

/* Режим фильтрации */
.filter-mode-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.mode-label {
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.mode-btn {
  padding: 4px 10px;
  background: var(--bg-tertiary, #f5f5f5);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary, #666);
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn.active {
  background: var(--primary-color, #c9a9e8);
  border-color: var(--primary-color, #c9a9e8);
  color: white;
}

/* Выпадающий список тегов */
.tag-selector-inline {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #e0e0e0);
  max-height: 200px;
  overflow-y: auto;
}

.tag-search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 10px;
  background: var(--bg-primary, white);
  color: var(--text-primary, #333);
}

.tag-search-input:focus {
  outline: none;
  border-color: var(--primary-color, #c9a9e8);
}

.all-tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 6px;
}

.tag-selector-item {
  background: var(--bg-primary, white);
  border: 1.5px solid;
  padding: 6px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.tag-selector-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.tag-selector-item.active {
  color: white !important;
}

.no-tags-found {
  text-align: center;
  padding: 20px;
  color: var(--text-tertiary, #999);
}

/* Чеклист */
.checklist-preview {
  background: var(--bg-primary, white);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--card-shadow, 0 2px 8px rgba(0, 0, 0, 0.05));
  border: 1px solid var(--border-color, #e0e0e0);
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.2s ease;
}
/* Мобильная адаптация */
@media (max-width: 768px) {
  .top-section {
    flex-direction: column;
    margin: 12px 16px;
    gap: 12px;
  }
  
  .left-column {
    gap: 10px;
  }
  
  .right-column {
    min-width: auto;
    align-self: stretch;
  }
  
  .controls-panel {
    flex-direction: column;
    margin: 4px auto 16px auto;
    padding: 0 20px;
  }
  
  .notes-container {
    padding: 0 20px 20px 20px;
  }
  
  .search-wrapper {
    max-width: 100%;
  }
}

/* Панель управления (поиск и сортировка) */
.controls-panel {
  max-width: 1400px;
  margin: 8px auto 20px auto;
  padding: 0 32px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.search-wrapper {
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s;
  background: var(--bg-primary, white);
  color: var(--text-primary, #333);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color, #c9a9e8);
  box-shadow: 0 0 0 3px rgba(201, 169, 232, 0.1);
}

.search-input::placeholder {
  color: var(--text-tertiary, #999);
}

.search-info {
  font-size: 12px;
  color: var(--primary-color, #c9a9e8);
  margin-top: 6px;
  padding-left: 4px;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-label {
  font-size: 14px;
  color: var(--text-secondary, #666);
}

.sort-btn {
  padding: 8px 16px;
  background: var(--bg-primary, white);
  border: 1px solid var(--border-color, #ddd);
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-secondary, #666);
  cursor: pointer;
  transition: all 0.2s;
}

.sort-btn:hover {
  background: var(--hover-bg, #f5f5f5);
}

.sort-btn.active {
  background: var(--primary-color, #c9a9e8);
  border-color: var(--primary-color, #c9a9e8);
  color: white;
}

/* Состояния загрузки/ошибки/пустоты */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  padding: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-light, #f3f3f3);
  border-top: 3px solid var(--primary-color, #c9a9e8);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-state {
  color: var(--danger-color, #dc3545);
}

.retry-btn {
  margin-top: 16px;
  padding: 8px 16px;
  background: var(--primary-color, #c9a9e8);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-title {
  margin: 0 0 8px 0;
  color: var(--text-primary, #333);
}

.empty-text {
  margin: 0 0 24px 0;
  color: var(--text-secondary, #666);
}

.create-first-btn {
  padding: 12px 24px;
  background: var(--primary-color, #c9a9e8);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  text-decoration: none;
}

/* Сетка заметок */
.notes-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px 24px 32px;
}

.delete-error {
  background: var(--danger-bg, #fee);
  color: var(--danger-color, #dc3545);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  text-align: center;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  max-width: 100%;
}

.note-card {
  background: var(--bg-primary, white);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--card-shadow, 0 2px 8px rgba(0, 0, 0, 0.05));
  transition: all 0.3s;
  cursor: pointer;
  border: 1px solid var(--border-color, #e0e0e0);
  display: flex;
  flex-direction: column;
  aspect-ratio: 1; /* Делает карточку квадратной */
  min-height: 300px; /* Минимальная высота для маленьких экранов */
}

.note-card:hover {
  box-shadow: var(--card-shadow-hover, 0 8px 24px rgba(0, 0, 0, 0.1));
  transform: translateY(-4px);
  border-color: var(--primary-color, #c9a9e8);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 8px;
}

.card-title-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.note-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #1a1a1a);
  line-height: 1.4;
  flex: 1;
  min-width: 0;
  word-break: break-word;
  overflow-wrap: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.candidate-icon {
  font-size: 16px;
  opacity: 0.8;
  flex-shrink: 0;
  margin-top: 2px;
}

.attachment-icon {
  font-size: 18px;
  opacity: 0.6;
  flex-shrink: 0;
  margin-top: 1px;
}

.delete-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  opacity: 0.5;
  transition: all 0.2s;
  color: var(--text-tertiary, #999);
  flex-shrink: 0;
}

.delete-btn:hover {
  opacity: 1;
  background: var(--danger-bg, #fee);
  color: var(--danger-color, #dc3545);
}

.note-preview {
  margin: 0 0 16px 0;
  color: var(--text-secondary, #666);
  line-height: 1.6;
  font-size: 14px;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: normal;
}

.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 12px 0;
}

.note-tag {
  background: var(--bg-primary, white);
  border: 1.5px solid;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.note-tag:hover {
  transform: scale(1.05);
}

.tag-more {
  background: var(--border-color, #e0e0e0);
  color: var(--text-secondary, #666);
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--border-light, #f0f0f0);
}

.note-date {
  font-size: 13px;
  color: var(--text-tertiary, #999);
}

.read-more {
  font-size: 14px;
  color: var(--primary-color, #c9a9e8);
  font-weight: 500;
}

:deep(.search-highlight) {
  background: var(--primary-light, #f0e6ff);
  color: #5700b3;
  padding: 0 2px;
  border-radius: 3px;
  font-weight: 500;
}

/* Модальные окна */
/* Модальные окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay, rgba(0, 0, 0, 0.5));
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  padding: 16px; /* Добавляем отступы для мобильных */
}

.modal-content {
  background: var(--bg-primary, white);
  border-radius: 16px;
  padding: 24px;
  width: 100%; /* По умолчанию на всю ширину */
  max-width: 500px; /* Максимальная ширина */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.2s ease-out;
  border: 1px solid var(--border-color, transparent);
  max-height: 90vh; /* Ограничение по высоте */
  overflow-y: auto; /* Скролл если не помещается */
}

.modal-large {
  max-width: 600px; /* Чуть шире для больших экранов */
}

/* Адаптивность для мобильных */
@media (max-width: 600px) {
  .modal-overlay {
    padding: 12px;
    align-items: flex-start; /* Прижимаем к верху на маленьких экранах */
    padding-top: 20px;
  }

  .modal-content {
    width: 100%;
    max-width: 100%;
    max-height: 85vh;
    padding: 16px;
    border-radius: 12px;
  }

  .modal-large {
    max-width: 100%;
  }

  .modal-header h3 {
    font-size: 16px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .cancel-btn,
  .save-btn {
    width: 100%;
    text-align: center;
    justify-content: center;
  }

  .color-presets {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .color-picker-container {
    flex-wrap: wrap;
  }

  .color-input {
    width: 48px;
    height: 36px;
  }

  .manage-tags-content {
    max-height: 50vh; /* Уменьшаем высоту для мобильных */
  }

  .manage-tags-header {
    flex-direction: column;
    gap: 8px;
  }

  .add-tag-manage-btn {
    width: 100%;
  }

  .manage-tag-item {
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px 12px;
  }

  .manage-tag-info {
    width: 100%;
  }

  .tag-notes-count {
    margin-right: 0;
    margin-left: auto;
  }

  .manage-tag-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .tag-search-input {
    font-size: 16px; /* Предотвращает зум на iOS */
  }
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
  color: var(--text-primary, #333);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary, #666);
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
  background: var(--hover-bg, #f0f0f0);
  color: var(--text-primary, #333);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary, #333);
}

.tag-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  background: var(--bg-primary, white);
  color: var(--text-primary, #333);
}

.tag-input:focus {
  outline: none;
  border-color: var(--primary-color, #c9a9e8);
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
  border: 1px solid var(--border-color, #ddd);
  border-radius: 8px;
  cursor: pointer;
  background: var(--bg-primary, white);
}

.color-text {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 8px;
  font-size: 14px;
  font-family: monospace;
  text-transform: uppercase;
  background: var(--bg-primary, white);
  color: var(--text-primary, #333);
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
  color: var(--danger-color, #dc3545);
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
  background: var(--bg-tertiary, #f5f5f5);
  color: var(--text-secondary, #666);
}

.cancel-btn:hover {
  background: var(--border-color, #e0e0e0);
}

.save-btn {
  background: var(--primary-color, #c9a9e8);
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: var(--primary-hover, #b794d4);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Управление тегами */
.manage-tags-content {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 4px;

  scrollbar-width: thin;
  scrollbar-color: var(--primary-color, #c9a9e8) transparent;
}

.manage-tags-content::-webkit-scrollbar {
  width: 4px;
}

.manage-tags-content::-webkit-scrollbar-track {
  background: transparent;
}

.manage-tags-content::-webkit-scrollbar-thumb {
  background: var(--primary-color, #c9a9e8);
  border-radius: 4px;
}

.manage-tags-content::-webkit-scrollbar-thumb:hover {
  background: var(--primary-hover, #b794d4);
}

.manage-tags-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  position: sticky;
  top: 0;
  background: var(--bg-primary, white);
  padding-bottom: 12px;
  z-index: 1;
}

.add-tag-manage-btn {
  padding: 10px 16px;
  background: var(--primary-color, #c9a9e8);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.add-tag-manage-btn:hover {
  background: var(--primary-hover, #b794d4);
}

.manage-tags-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.manage-tag-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-tertiary, #f8f9fa);
  border-radius: 10px;
  transition: all 0.2s;
}

.manage-tag-item:hover {
  background: var(--hover-bg, #e9ecef);
}

.manage-tag-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.tag-color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 0.1);
}

.tag-name {
  font-weight: 500;
  color: var(--text-primary, #333);
}

.tag-notes-count {
  font-size: 12px;
  color: var(--text-tertiary, #999);
  margin-left: auto;
  margin-right: 16px;
}

.manage-tag-actions {
  display: flex;
  gap: 4px;
}

.edit-tag-manage-btn,
.delete-tag-manage-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 6px;
  transition: all 0.2s;
  opacity: 0.7;
}

.edit-tag-manage-btn:hover {
  opacity: 1;
  background: var(--hover-bg, #e0e0e0);
}

.delete-tag-manage-btn:hover:not(:disabled) {
  opacity: 1;
  background: var(--danger-bg, #fee);
  color: var(--danger-color, #dc3545);
}

.delete-tag-manage-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.card-title-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.card-icons {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.candidate-icon {
  font-size: 16px;
  opacity: 0.8;
  flex-shrink: 0;
}

.attachment-icon {
  font-size: 18px;
  opacity: 0.6;
  flex-shrink: 0;
}

/* Адаптивность */
@media (max-width: 768px) {
  .top-section {
    flex-direction: column;
    margin: 8px 12px;
    gap: 10px;
  }
  
  .left-column {
    gap: 8px;
  }
  
  .right-column {
    min-width: auto;
    align-self: stretch;
  }
  
  .checklist-preview {
    padding: 12px;
    max-height: 280px;
  }
  
  .controls-panel {
    flex-direction: column;
    margin: 4px auto 12px auto;
    padding: 0 12px;
    gap: 12px;
  }
  
  .search-wrapper {
    max-width: 100%;
  }
  
  .notes-container {
    padding: 0 12px 16px 12px;
  }
  
  .notes-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .all-tags-grid {
    grid-template-columns: 1fr;
  }
  
  /* Уменьшаем отступы в блоке тегов */
  .tags-section-inline {
    padding: 10px 12px;
  }
  
  .popular-tag,
  .selected-tag {
    padding: 4px 10px;
    font-size: 12px;
  }
  
  .tag-selector-inline {
    margin-top: 8px;
    padding-top: 8px;
  }
}

/* Ограничиваем максимум 4 карточки в ряд */
@media (min-width: 1400px) {
  .notes-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Планшеты - 2 карточки */
@media (max-width: 900px) {
  .notes-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

/* Телефоны - 1 карточка */
@media (max-width: 600px) {
  .notes-container {
    padding: 0 16px;
  }

  .notes-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>
