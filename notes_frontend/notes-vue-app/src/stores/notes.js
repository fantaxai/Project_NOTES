import { defineStore } from 'pinia'
import { ref } from 'vue'
import { notesApi } from '../api/index' // Импортируем из index.ts

export const useNoteStore = defineStore('note', () => {
  const notes = ref([])
  const currentNote = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchNotes = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await notesApi.getAll()
      notes.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки заметок'
      console.error('Ошибка загрузки:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // ... остальные методы используют notesApi ...
  const createNote = async (noteData) => {
    loading.value = true
    error.value = null
    try {
      const response = await notesApi.create(noteData)
      currentNote.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка создания заметки'
      console.error('Ошибка создания:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchNoteById = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await notesApi.getById(id)
      currentNote.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки заметки'
      console.error('Ошибка загрузки:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateNote = async (id, noteData) => {
    loading.value = true
    error.value = null
    try {
      const response = await notesApi.update(id, noteData)
      const updatedNote = response.data
      const index = notes.value.findIndex((n) => n.id === id)
      if (index !== -1) {
        notes.value[index] = updatedNote
      }
      currentNote.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка обновления заметки'
      console.error('Ошибка обновления:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteNote = async (id) => {
    loading.value = true
    error.value = null
    try {
      await notesApi.delete(id)
      notes.value = notes.value.filter((n) => n.id !== id)
      currentNote.value = null
    } catch (err) {
      error.value = err.message || 'Ошибка удаления заметки'
      console.error('Ошибка удаления:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearCurrentNote = () => {
    currentNote.value = null
    error.value = null
  }

  const hasFiles = async (noteId) => {
    try {
      await notesApi.getById(noteId)
      return false
    } catch (err) {
      console.error('Ошибка проверки файлов:', err)
      return false
    }
  }

  return {
    notes,
    currentNote,
    loading,
    error,
    fetchNotes,
    createNote,
    fetchNoteById,
    updateNote,
    deleteNote,
    clearCurrentNote,
    hasFiles,
  }
})
