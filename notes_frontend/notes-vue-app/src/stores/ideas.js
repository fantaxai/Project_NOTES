import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index' // Импортируем общий api

export const useIdeaStore = defineStore('idea', () => {
  const currentIdea = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const shownNoteIds = ref(new Set())
  const totalCandidates = ref(0)

  const shownCount = computed(() => shownNoteIds.value.size)

  const fetchIdeaOfDay = async () => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/ideas/today/')
      console.log('✅ Ответ API:', response.data)

      totalCandidates.value = response.data.total_candidates || 0

      if (response.data.shown_ids) {
        shownNoteIds.value = new Set(response.data.shown_ids)
      }

      if (!response.data.note) {
        currentIdea.value = null
        error.value = response.data.message || 'Недостаточно кандидатов'
        return response.data
      }

      currentIdea.value = response.data
      error.value = null

      return response.data
    } catch (err) {
      console.error('❌ Ошибка:', err)
      error.value = err.response?.data?.error || err.message || 'Ошибка загрузки'
      currentIdea.value = null
    } finally {
      loading.value = false
    }
  }

  const markAsShown = async (noteId) => {
    try {
      await api.post('/ideas/today/mark_shown/', { note_id: noteId })
      shownNoteIds.value.add(noteId)
    } catch (err) {
      console.error('Ошибка отметки:', err)
    }
  }

  const resetShownStatus = async () => {
    try {
      await api.post('/ideas/today/reset_shown/')
      shownNoteIds.value.clear()
      await fetchIdeaOfDay()
    } catch (err) {
      console.error('Ошибка сброса:', err)
    }
  }

  return {
    currentIdea,
    loading,
    error,
    totalCandidates,
    shownCount,
    fetchIdeaOfDay,
    markAsShown,
    resetShownStatus,
  }
})
