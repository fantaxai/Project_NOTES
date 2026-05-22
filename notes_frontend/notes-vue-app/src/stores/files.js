import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index'  // ← импортируем общий инстанс с JWT

const filesApi = {
  getAll: () => api.get('/files/'),
  getById: (id) => api.get(`/files/${id}/`),
  getByNote: (noteId) => api.get(`/files/by_note/?note_id=${noteId}`),
  create: (fileData) => {
    const formData = new FormData()
    formData.append('name', fileData.name)
    formData.append('size', fileData.size)
    formData.append('format', fileData.format)
    formData.append('note', fileData.note)
    if (fileData.thumbnail) {
      formData.append('thumbnail', fileData.thumbnail)
    }
    return api.post('/files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  delete: (id) => api.delete(`/files/${id}/`),
  updateThumbnail: (id, thumbnail) =>
    api.post(`/files/${id}/update_thumbnail/`, { thumbnail }),
}

export const useFileStore = defineStore('file', () => {
  const files = ref([])
  const currentNoteFiles = ref([])
  const loading = ref(false)
  const error = ref(null)

  const fetchNoteFiles = async (noteId) => {
    loading.value = true
    error.value = null
    try {
      const response = await filesApi.getByNote(noteId)
      currentNoteFiles.value = response.data.files || []
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки файлов'
      console.error('Ошибка загрузки файлов:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const uploadFile = async (fileData) => {
    loading.value = true
    error.value = null
    try {
      const response = await filesApi.create(fileData)
      currentNoteFiles.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки файла'
      console.error('Ошибка загрузки файла:', err.response?.data || err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteFile = async (fileId) => {
    loading.value = true
    error.value = null
    try {
      await filesApi.delete(fileId)
      currentNoteFiles.value = currentNoteFiles.value.filter((f) => f.id !== fileId)
    } catch (err) {
      error.value = err.message || 'Ошибка удаления файла'
      console.error('Ошибка удаления файла:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateFileThumbnail = async (fileId, thumbnail) => {
    try {
      const response = await filesApi.updateThumbnail(fileId, thumbnail)
      const index = currentNoteFiles.value.findIndex((f) => f.id === fileId)
      if (index !== -1) {
        currentNoteFiles.value[index] = response.data.data
      }
      return response.data
    } catch (err) {
      console.error('Ошибка обновления миниатюры:', err)
      throw err
    }
  }

  const checkNoteHasFiles = async (noteId) => {
    try {
      const response = await filesApi.getByNote(noteId)
      return response.data.count > 0
    } catch (err) {
      return false
    }
  }

  const clearCurrentFiles = () => {
    currentNoteFiles.value = []
    error.value = null
  }

  return {
    files,
    currentNoteFiles,
    loading,
    error,
    fetchNoteFiles,
    uploadFile,
    deleteFile,
    updateFileThumbnail,
    checkNoteHasFiles,
    clearCurrentFiles,
  }
})
