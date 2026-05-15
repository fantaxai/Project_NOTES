import { defineStore } from 'pinia'
import api from '../api'

export const useFileStore = defineStore('files', {
  state: () => ({
    currentNoteFiles: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchNoteFiles(noteId) {
      this.loading = true
      this.error = null
      try {
        const response = await api.get(`/files/by_note/?note_id=${noteId}`)
        this.currentNoteFiles = response.data.files || []
        return this.currentNoteFiles
      } catch (error) {
        this.error = 'Ошибка загрузки файлов'
        console.error('Ошибка загрузки файлов:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async uploadFile(fileData) {
      try {
        // Если есть файл для загрузки (не только метаданные)
        if (fileData.file && fileData.file instanceof File) {
          const reader = new FileReader()
          const fileContent = await new Promise((resolve) => {
            reader.onload = (e) => resolve(e.target.result)
            reader.readAsDataURL(fileData.file)
          })
          
          const uploadData = {
            name: fileData.name,
            size: fileData.size,
            format: fileData.format,
            note: fileData.note,
            thumbnail: fileData.thumbnail,
            file_data: fileContent,
          }
          
          const response = await api.post('/files/', uploadData)
          return response.data
        } else {
          // Только метаданные
          const response = await api.post('/files/', fileData)
          return response.data
        }
      } catch (error) {
        console.error('Ошибка загрузки файла:', error)
        throw error
      }
    },

    async deleteFile(fileId) {
      try {
        await api.delete(`/files/${fileId}/`)
        this.currentNoteFiles = this.currentNoteFiles.filter(f => f.id !== fileId)
      } catch (error) {
        console.error('Ошибка удаления файла:', error)
        throw error
      }
    },

    getFileUrl(fileId) {
      return `/api/files/${fileId}/serve/`
    },

    async checkNoteHasFiles(noteId) {
      try {
        const response = await api.get(`/files/by_note/?note_id=${noteId}`)
        return response.data.count > 0
      } catch (error) {
        return false
      }
    },

    clearCurrentFiles() {
      this.currentNoteFiles = []
    },
  },
})