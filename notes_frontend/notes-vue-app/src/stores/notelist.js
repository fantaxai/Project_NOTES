import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notesApi } from '../api/index'

export const useNoteListStore = defineStore('notelist', () => {
  const notes = ref([])
  const loading = ref(false)
  const error = ref(null)
  const searchQuery = ref('')
  const sortOrder = ref('newest')

  const filteredNotes = computed(() => {
    if (!searchQuery.value.trim()) return notes.value

    const query = searchQuery.value.toLowerCase().trim()
    return notes.value.filter(
      (note) =>
        note.title?.toLowerCase().includes(query) || note.content?.toLowerCase().includes(query)
    )
  })

  // Отсортированные заметки
  const sortedNotes = computed(() => {
    const notesToSort = [...filteredNotes.value]

    return notesToSort.sort((a, b) => {
      const dateA = new Date(a.creation_date || a.last_change_date || 0)
      const dateB = new Date(b.creation_date || b.last_change_date || 0)

      return sortOrder.value === 'newest' ? dateB - dateA : dateA - dateB
    })
  })

  const totalCount = computed(() => notes.value.length)
  const filteredCount = computed(() => filteredNotes.value.length)
  const isEmpty = computed(() => notes.value.length === 0)

  const fetchNotes = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await notesApi.getAll()
      notes.value = response.data
      console.log('Загружено заметок:', notes.value.length)
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки списка заметок'
      console.error('Ошибка загрузки списка:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const addNoteToList = (newNote) => {
    if (!newNote || !newNote.id) {
      console.warn('Попытка добавить некорректную заметку в список')
      return
    }

    const exists = notes.value.some((note) => note.id === newNote.id)
    if (exists) {
      console.warn('Заметка с таким ID уже существует в списке')
      return
    }

    notes.value.unshift(newNote)
    console.log('Заметка добавлена в список локально:', newNote.id)
  }

  const updateNoteInList = (updatedNote) => {
    if (!updatedNote || !updatedNote.id) return

    const index = notes.value.findIndex((note) => note.id === updatedNote.id)
    if (index !== -1) {
      notes.value[index] = { ...notes.value[index], ...updatedNote }
      console.log('Заметка обновлена в списке:', updatedNote.id)
    }
  }

  const removeNoteFromList = (noteId) => {
    const initialLength = notes.value.length
    notes.value = notes.value.filter((note) => note.id !== noteId)

    if (initialLength !== notes.value.length) {
      console.log('Заметка удалена из списка:', noteId)
    }
  }

  const deleteNoteAndUpdateList = async (noteId) => {
    loading.value = true
    error.value = null

    try {
      await notesApi.delete(noteId)
      removeNoteFromList(noteId)
      console.log('Заметка удалена с сервера и из списка:', noteId)
    } catch (err) {
      error.value = err.message || 'Ошибка удаления заметки'
      console.error('Ошибка удаления:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const setSearchQuery = (query) => {
    searchQuery.value = query
  }

  const setSortOrder = (order) => {
    if (order === 'newest' || order === 'oldest') {
      sortOrder.value = order
    }
  }

  const clearList = () => {
    notes.value = []
    searchQuery.value = ''
    sortOrder.value = 'newest'
    error.value = null
  }

  const clearError = () => {
    error.value = null
  }

  // CreateNote
  const createNote = async (noteData) => {
    loading.value = true
    error.value = null

    try {
      console.log('📤 ОТПРАВКА ДАННЫХ:', JSON.stringify(noteData, null, 2))

      const response = await notesApi.create(noteData)
      const newNote = response.data

      console.log('📥 ОТВЕТ СЕРВЕРА:', newNote)

      // Проверяем наличие тегов в ответе
      if (newNote.tags && newNote.tags.length > 0) {
        console.log('✅ Теги успешно прикреплены:', newNote.tags)
      } else {
        console.warn('⚠️ Теги не были прикреплены!')
      }

      notes.value.unshift(newNote)
      return newNote
    } catch (err) {
      error.value = err.response?.data || 'Ошибка создания заметки'
      console.error('❌ Ошибка создания:', err.response?.data)
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    notes,
    loading,
    error,
    searchQuery,
    sortOrder,
    filteredNotes,
    sortedNotes,
    totalCount,
    filteredCount,
    isEmpty,
    fetchNotes,
    addNoteToList,
    updateNoteInList,
    removeNoteFromList,
    deleteNoteAndUpdateList,
    setSearchQuery,
    setSortOrder,
    clearList,
    clearError,
    createNote,
  }
})
