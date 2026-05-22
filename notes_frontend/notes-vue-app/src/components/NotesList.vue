<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useNoteListStore } from '../stores/notelist'
import { useFileStore } from '../stores/files'
import IdeaOfDay from '../components/IdeaOfDay.vue'

const noteListStore = useNoteListStore()
const fileStore = useFileStore()

// Локальное состояние
const isDeleting = ref(false)
const deleteError = ref(null)
const notesWithFiles = ref(new Set())

// Получение данных из стора
const notes = computed(() => noteListStore.sortedNotes)
const loading = computed(() => noteListStore.loading)
const error = computed(() => noteListStore.error)
const searchQuery = computed(() => noteListStore.searchQuery)
const sortOrder = computed(() => noteListStore.sortOrder)
const totalCount = computed(() => noteListStore.totalCount)

// Проверка наличия файлов для всех заметок
const checkFilesForNotes = async () => {
  const uncheckedNotes = notes.value.filter((note) => !notesWithFiles.value.has(note.id))
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

// Загрузка заметок при монтировании
onMounted(async () => {
  await noteListStore.fetchNotes()
  await checkFilesForNotes()
})

watch(
  () => notes.value,
  async () => {
    await checkFilesForNotes()
  }
)

// Вспомогательная функция для склонения слов
const getPluralForm = (number, forms) => {
  const n = Math.abs(number) % 100
  const n1 = n % 10

  if (n > 10 && n < 20) return forms[2]
  if (n1 > 1 && n1 < 5) return forms[1]
  if (n1 === 1) return forms[0]
  return forms[2]
}

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Сегодня'
  if (diffDays === 1) return 'Вчера'
  if (diffDays < 7) return `${diffDays} дн. назад`

  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
  })
}

// Превью текста - ограничиваем до 90 символов (3 строки по 30)
const getPreview = (content) => {
  if (!content) return 'Нет содержания'
  
  // Удаляем HTML теги
  const plainText = content.replace(/<[^>]*>/g, '')
  
  // Удаляем множественные пробелы и переносы строк
  const cleanText = plainText.replace(/\s+/g, ' ').trim()
  
  // Обрезаем до 90 символов
  if (cleanText.length > 90) {
    return cleanText.substring(0, 90) + '...'
  }
  
  return cleanText
}

// Обрезаем заголовок до 25 символов
const getTruncatedTitle = (title) => {
  if (!title) return 'Без названия'
  if (title.length > 25) {
    return title.substring(0, 25) + '...'
  }
  return title
}
</script>

<template>
  <div class="notes-list-page">
    <!-- Идея дня -->
    <IdeaOfDay />

    <!-- Шапка -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Мои идеи</h1>
        <span v-if="totalCount > 0" class="notes-count">
          {{ totalCount }} {{ getPluralForm(totalCount, ['идея', 'идеи', 'идей']) }}
        </span>
        <span v-if="selectedTagIds.length > 0" class="filter-badge">
          • Фильтр: {{ selectedTagIds.length }}
          {{ getPluralForm(selectedTagIds.length, ['тег', 'тега', 'тегов']) }} ({{
            filterMode === 'and' ? 'И' : 'ИЛИ'
          }})
        </span>
      </div>

      <div class="header-right">
        <button class="new-tag-btn" @click="openTagModal">
          <span class="plus-icon">+</span>
          Новый тег
        </button>
        <router-link to="/create" class="create-btn">
          <span class="plus-icon">+</span>
          Новая идея
        </router-link>
      </div>
    </div>

    <!-- Частые теги -->
    <div v-if="popularTags.length > 0" class="popular-tags-section">
      <div class="popular-tags-header">
        <span class="section-label">🏷️ Частые теги</span>
        <div class="filter-mode">
          <button
            :class="['mode-btn', { active: filterMode === 'and' }]"
            title="Показать идеи со ВСЕМИ выбранными тегами"
            @click="filterMode = 'and'"
          >
            И
          </button>
          <button
            :class="['mode-btn', { active: filterMode === 'or' }]"
            title="Показать идеи с ЛЮБЫМ из выбранных тегов"
            @click="filterMode = 'or'"
          >
            ИЛИ
          </button>
        </div>
      </div>
      <div class="popular-tags-list">
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
    </div>

    <!-- Фильтр по тегам -->
    <div class="filter-tags-section">
      <div class="filter-tags-header">
        <span class="section-label">🔍 Фильтр по тегам</span>
        <div class="filter-header-actions">
          <button
            v-if="selectedTagIds.length > 0"
            class="clear-filters-btn"
            @click="clearTagFilters"
          >
            ✕ Сбросить
          </button>
          <button class="select-tags-btn" @click="showTagSelector = !showTagSelector">
            {{ showTagSelector ? 'Скрыть список' : '➕ Выбрать теги' }}
          </button>
        </div>
      </div>

      <div v-if="selectedTagIds.length > 0" class="selected-filter-tags">
        <div class="filter-tags-list">
          <button
            v-for="tagId in selectedTagIds"
            :key="tagId"
            class="filter-tag active"
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
        </div>
      </div>
      <div v-else class="empty-filter-hint">Нажмите "Выбрать теги" чтобы отфильтровать идеи</div>

      <div v-if="showTagSelector" class="tag-selector-dropdown">
        <div class="tag-selector-header">
          <input
            v-model="tagSearchQuery"
            type="text"
            placeholder="🔍 Поиск тега..."
            class="tag-search-input"
          />
        </div>
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
            <span v-if="selectedTagIds.includes(tag.id)" class="check-icon">✓</span>
          </button>
        </div>
        <div v-if="filteredAllTags.length === 0" class="no-tags-found">Теги не найдены</div>
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
              <h3 class="note-title">{{ getTruncatedTitle(note.title) }}</h3>
              <span
                v-if="notesWithFiles.has(note.id)"
                class="attachment-icon"
                title="Есть прикрепленные файлы"
              >
                📎
              </span>
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

          <p class="note-preview">{{ getPreview(note.content) }}</p>

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
              #{{ tag.name }}
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

    <!-- Модальное окно создания тега -->
    <div v-if="showTagModal" class="modal-overlay" @click="closeTagModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Новый тег</h3>
          <button class="close-btn" @click="closeTagModal">×</button>
        </div>

        <form @submit.prevent="createNewTag">
          <div class="form-group">
            <label for="newTagName">Название тега</label>
            <input
              id="newTagName"
              v-model="newTagName"
              type="text"
              placeholder="Введите название тега"
              class="tag-input"
              autofocus
              required
            />
          </div>

          <div class="form-group">
            <label for="newTagColor">Цвет тега</label>
            <div class="color-picker-container">
              <input id="newTagColor" v-model="newTagColor" type="color" class="color-input" />
              <input
                v-model="newTagColor"
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
                @click="newTagColor = color"
              ></button>
            </div>
          </div>

          <div v-if="tagError" class="error-message">
            {{ tagError }}
          </div>

          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click="closeTagModal">Отмена</button>
            <button type="submit" :disabled="!newTagName.trim() || creatingTag" class="save-btn">
              {{ creatingTag ? 'Создание...' : 'Создать' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notes-list-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  color: #1a1a1a;
}

.notes-count {
  font-size: 14px;
  color: #666;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-input {
  width: 250px;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.create-btn:hover {
  background: #0056b3;
}

.plus-icon {
  font-size: 20px;
}

/* Панель сортировки */
.sort-panel {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-label {
  font-size: 14px;
  color: #666;
}

.sort-btn {
  padding: 6px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.sort-btn:hover {
  background: #f5f5f5;
}

.sort-btn.active {
  background: #007bff;
  border-color: #007bff;
  color: white;
}

/* Состояния */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  color: #dc3545;
}

.retry-btn {
  margin-top: 16px;
  padding: 8px 16px;
  background: #007bff;
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
  color: #333;
}

.empty-text {
  margin: 0 0 24px 0;
  color: #666;
}

.create-first-btn {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
}

.create-first-btn:hover {
  background: #0056b3;
}

/* Сетка заметок */
.notes-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 24px;
}

.delete-error {
  background: #fee;
  color: #dc3545;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  text-align: center;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

/* Карточка заметки */
.note-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  min-height: 180px;
  max-height: 280px;
  overflow: hidden;
}

.note-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  border-color: #007bff;
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
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.note-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #1a1a1a;
  line-height: 1.4;
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.attachment-icon {
  font-size: 16px;
  opacity: 0.6;
  flex-shrink: 0;
}

.note-preview {
  margin: 0 0 16px 0;
  color: #666;
  line-height: 1.5;
  font-size: 14px;
  flex: 1;
  overflow: hidden;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-height: 72px;
}

.delete-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  opacity: 0.6;
  transition: all 0.2s;
  flex-shrink: 0;
}

.delete-btn:hover:not(:disabled) {
  opacity: 1;
  background: #fee;
}

.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 12px 0;
  max-height: 32px;
  overflow: hidden;
}

.note-tag {
  background: white;
  border: 1.5px solid;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.note-tag:hover {
  transform: scale(1.05);
}

.tag-more {
  background: #e0e0e0;
  color: #666;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  white-space: nowrap;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.note-date {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

.read-more {
  font-size: 14px;
  color: #007bff;
  font-weight: 500;
  white-space: nowrap;
}

/* Адаптивность */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .header-right {
    flex-direction: column;
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .create-btn {
    width: 100%;
    justify-content: center;
  }

  .sort-panel {
    flex-direction: column;
    gap: 12px;
  }

  .notes-grid {
    grid-template-columns: 1fr;
  }
}
</style>