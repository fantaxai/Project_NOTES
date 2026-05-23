// stores/checklist.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { checklistApi } from '../api/index.ts'

export const useChecklistStore = defineStore('checklist', () => {
  const savedChecklist = localStorage.getItem('currentChecklist')
  const currentChecklist = ref(savedChecklist ? JSON.parse(savedChecklist) : null)
  const checklists = ref([])
  const loading = ref(false)
  const error = ref(null)
  const isLoaded = ref(false)

  // Загрузить все чеклисты
  const fetchChecklists = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await checklistApi.getAll()
      checklists.value = response.data
      isLoaded.value = true

      if (currentChecklist.value) {
        const updated = response.data.find((c) => c.id === currentChecklist.value.id)
        if (updated) {
          currentChecklist.value = updated
          localStorage.setItem('currentChecklist', JSON.stringify(updated))
        } else {
          clearChecklist()
        }
      }
      return response.data
    } catch (err) {
      if (err.response?.status === 401) {
        console.warn('Checklist: не авторизован, пропускаем загрузку')
        error.value = null
        return []
      }
      error.value = err.response?.data?.detail || err.message || 'Ошибка загрузки чеклистов'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Сгенерировать новый чеклист
  const generateChecklist = async (config) => {
    loading.value = true
    error.value = null
    try {
      const response = await checklistApi.generate({
        amount_of_ideas: config.amount_of_ideas,
        categories: config.categories,
      })
      currentChecklist.value = response.data
      localStorage.setItem('currentChecklist', JSON.stringify(response.data))
      await fetchChecklists()
      return response.data
    } catch (err) {
      if (err.response?.status === 401) {
        error.value = 'Необходимо войти в аккаунт'
        throw err
      }
      error.value = err.response?.data?.detail || err.message || 'Ошибка генерации чеклиста'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Выбрать чеклист
  const selectChecklist = (checklist) => {
    currentChecklist.value = checklist
    localStorage.setItem('currentChecklist', JSON.stringify(checklist))
  }

  // Удалить чеклист
  const deleteChecklist = async (checklistId) => {
    try {
      await checklistApi.delete(checklistId)
      if (currentChecklist.value?.id === checklistId) {
        clearChecklist()
      }
      await fetchChecklists()
    } catch (err) {
      console.error('Ошибка удаления чеклиста:', err.response?.data || err.message)
      throw err
    }
  }

  // Переключить пункт чеклиста
  const toggleItem = async (checklistId, itemId) => {
    try {
      const response = await checklistApi.toggleItem(checklistId, itemId)
      if (currentChecklist.value?.id === checklistId) {
        const item = currentChecklist.value.items.find((i) => i.id === itemId)
        if (item) {
          item.completed = response.data.completed
          localStorage.setItem('currentChecklist', JSON.stringify(currentChecklist.value))
        }
      }
      return response.data
    } catch (err) {
      console.error('Ошибка обновления пункта:', err.response?.data || err.message)
      throw err
    }
  }

  // Регенерировать чеклист
  const regenerateChecklist = async (checklistId) => {
    loading.value = true
    error.value = null
    try {
      const response = await checklistApi.regenerate(checklistId)
      if (currentChecklist.value?.id === checklistId) {
        currentChecklist.value = response.data
        localStorage.setItem('currentChecklist', JSON.stringify(response.data))
      }
      await fetchChecklists()
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Ошибка регенерации чеклиста'
      console.error('Ошибка регенерации:', err.response?.data || err.message)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Сохранить чеклист как заметку
  const saveAsNote = async (checklistId) => {
    loading.value = true
    error.value = null
    try {
      const response = await checklistApi.saveAsNote(checklistId)
      if (currentChecklist.value?.id === checklistId) {
        currentChecklist.value = {
          ...currentChecklist.value,
          saved_as_note: response.data.note_id
        }
        localStorage.setItem('currentChecklist', JSON.stringify(currentChecklist.value))
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || err.message || 'Ошибка сохранения в заметку'
      console.error('Ошибка сохранения в заметку:', err.response?.data || err.message)
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearChecklist = () => {
    currentChecklist.value = null
    error.value = null
    localStorage.removeItem('currentChecklist')
  }

  const reset = () => {
    currentChecklist.value = null
    checklists.value = []
    loading.value = false
    error.value = null
    isLoaded.value = false
    localStorage.removeItem('currentChecklist')
  }

  // Инициализация - загрузка чеклистов при первом обращении
  const init = async () => {
    if (!isLoaded.value) {
      await fetchChecklists()
    }
  }

  return {
    currentChecklist,
    checklists,
    loading,
    error,
    isLoaded,
    fetchChecklists,
    generateChecklist,
    selectChecklist,
    deleteChecklist,
    toggleItem,
    regenerateChecklist,
    reset,
    saveAsNote,
    clearChecklist,
    init,
  }
})