// stores/ideas.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: { 'Content-Type': 'application/json' },
})

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
      console.log('📡 Запрос к API...')
      const response = await api.get('/ideas/today/today/')
      console.log('✅ Ответ:', response.data)

      // ВАЖНО! Данные приходят в response.data
      currentIdea.value = response.data
      totalCandidates.value = response.data.total_candidates || 0

      if (response.data.shown_ids) {
        shownNoteIds.value = new Set(response.data.shown_ids)
      }

      console.log('✅ currentIdea установлен:', currentIdea.value)
      console.log('✅ totalCandidates установлен:', totalCandidates.value)

      return response.data
    } catch (err) {
      console.error('❌ Ошибка:', err)
      error.value = err.message || 'Ошибка загрузки'
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

  const nextIdea = async () => {
    if (currentIdea.value?.note?.id) {
      await markAsShown(currentIdea.value.note.id)
      await fetchIdeaOfDay()
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
    nextIdea,
  }
})
