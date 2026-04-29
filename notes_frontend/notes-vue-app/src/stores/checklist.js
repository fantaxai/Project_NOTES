import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/',
  headers: { 'Content-Type': 'application/json' },
})

export const useChecklistStore = defineStore('checklist', () => {
  const savedChecklist = localStorage.getItem('currentChecklist')
  const currentChecklist = ref(savedChecklist ? JSON.parse(savedChecklist) : null)
  const checklists = ref([]) // все чеклисты
  const loading = ref(false)
  const error = ref(null)

  // Загрузить все чеклисты
  const fetchChecklists = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/checklists/')
      checklists.value = response.data

      // Если есть текущий чеклист, обновить его данные
      if (currentChecklist.value) {
        const updated = response.data.find((c) => c.id === currentChecklist.value.id)
        if (updated) {
          currentChecklist.value = updated
          localStorage.setItem('currentChecklist', JSON.stringify(updated))
        } else {
          // Текущий чеклист был удалён
          clearChecklist()
        }
      }

      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки чеклистов'
      console.error('Ошибка загрузки чеклистов:', err)
    } finally {
      loading.value = false
    }
  }

  // Сгенерировать новый чеклист
  const generateChecklist = async (config) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post('/checklists/generate/', {
        amount_of_ideas: config.amount_of_ideas,
        categories: config.categories,
      })

      currentChecklist.value = response.data
      localStorage.setItem('currentChecklist', JSON.stringify(response.data))

      // Обновить список чеклистов
      await fetchChecklists()

      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка генерации чеклиста'
      console.error('Ошибка:', err.response?.data || err.message)
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
      await api.delete(`/checklists/${checklistId}/`)

      // Если удалили текущий, сбросить
      if (currentChecklist.value?.id === checklistId) {
        clearChecklist()
      }

      // Обновить список
      await fetchChecklists()
    } catch (err) {
      console.error('Ошибка удаления чеклиста:', err)
      throw err
    }
  }

  // Переключить пункт чеклиста
  const toggleItem = async (checklistId, itemId) => {
    try {
      const response = await api.post(`/checklists/${checklistId}/toggle_completed/`, {
        item_id: itemId,
      })

      if (currentChecklist.value?.id === checklistId) {
        const item = currentChecklist.value.items.find((i) => i.id === itemId)
        if (item) {
          item.completed = response.data.completed
        }
        localStorage.setItem('currentChecklist', JSON.stringify(currentChecklist.value))
      }

      return response.data
    } catch (err) {
      console.error('Ошибка обновления пункта:', err)
    }
  }

  const clearChecklist = () => {
    currentChecklist.value = null
    error.value = null
    localStorage.removeItem('currentChecklist')
  }

  return {
    currentChecklist,
    checklists,
    loading,
    error,
    fetchChecklists,
    generateChecklist,
    selectChecklist,
    deleteChecklist,
    toggleItem,
    clearChecklist,
  }
})
