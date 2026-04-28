import { defineStore } from 'pinia'
import { ref } from 'vue'
import { tagsApi } from '../api/index.ts'

export const DEFAULT_TAGS = [
  { name: 'Работа', color: '#FFB3B3' },
  { name: 'Личное', color: '#A0C4FF' },
  { name: 'Идеи', color: '#CAFFBF' },
  { name: 'Важное', color: '#FFC6FF' },
  { name: 'Изучить', color: '#FDFFB6' },
  { name: 'Проекты', color: '#9BF6FF' },
  { name: 'Заметки', color: '#BDB2FF' },
  { name: 'Планы', color: '#FFD6A5' },
]

export const useTagStore = defineStore('tag', () => {
  const tags = ref([])
  const currentTag = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Получить все теги
  const fetchTags = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await tagsApi.getAll()
      tags.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки тегов'
      console.error('Ошибка загрузки тегов:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Получить тег по ID
  const fetchTagById = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await tagsApi.getById(id)
      currentTag.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки тега'
      console.error('Ошибка загрузки тега:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Создать новый тег
  const createTag = async (tagData) => {
    loading.value = true
    error.value = null
    try {
      const response = await tagsApi.create(tagData)
      tags.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка создания тега'
      console.error('Ошибка создания тега:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Обновить тег
  const updateTag = async (id, tagData) => {
    loading.value = true
    error.value = null
    try {
      const response = await tagsApi.update(id, tagData)
      const index = tags.value.findIndex((tag) => tag.id === id)
      if (index !== -1) {
        tags.value[index] = response.data
      }
      if (currentTag.value?.id === id) {
        currentTag.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка обновления тега'
      console.error('Ошибка обновления тега:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Удалить тег
  const deleteTag = async (id) => {
    loading.value = true
    error.value = null
    try {
      await tagsApi.delete(id)
      tags.value = tags.value.filter((tag) => tag.id !== id)
      if (currentTag.value?.id === id) {
        currentTag.value = null
      }
    } catch (err) {
      error.value = err.message || 'Ошибка удаления тега'
      console.error('Ошибка удаления тега:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Получить заметки по тегу
  const fetchNotesByTag = async (tagId) => {
    loading.value = true
    error.value = null
    try {
      const response = await tagsApi.getNotesByTag(tagId)
      return response.data
    } catch (err) {
      error.value = err.message || 'Ошибка загрузки заметок по тегу'
      console.error('Ошибка загрузки заметок по тегу:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearCurrentTag = () => {
    currentTag.value = null
    error.value = null
  }

  const initializeDefaultTags = async () => {
    const defaultTags = [
      { name: 'Работа', color: '#FFB3B3' },
      { name: 'Личное', color: '#A0C4FF' },
      { name: 'Проекты', color: '#CAFFBF' },
      { name: 'Изучить', color: '#FDFFB6' },
      { name: 'Важное', color: '#FFC6FF' },
    ]

    try {
      // Проверяем, есть ли уже теги
      const existingTags = await fetchTags()

      if (existingTags.length === 0) {
        // Создаем предустановленные теги
        for (const tag of defaultTags) {
          await createTag(tag)
        }
        console.log('✅ Предустановленные теги созданы')
      }
    } catch (err) {
      console.error('Ошибка создания предустановленных тегов:', err)
    }
  }

  return {
    tags,
    currentTag,
    loading,
    error,
    fetchTags,
    fetchTagById,
    createTag,
    updateTag,
    deleteTag,
    fetchNotesByTag,
    clearCurrentTag,
    initializeDefaultTags,
  }
})
