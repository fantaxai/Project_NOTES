import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
})

const notesApi = {
  getAll: () => api.get('/notes/'),
  getById: (id) => api.get(`/notes/${id}/`),
  create: (noteData) => api.post('/notes/', noteData),
  update: (id, noteData) => api.patch(`/notes/${id}/`, noteData),
  delete: (id) => api.delete(`/notes/${id}/`),
}

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
      const response = await api.get(`/files/by_note/?note_id=${noteId}`)
      return response.data.count > 0
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
