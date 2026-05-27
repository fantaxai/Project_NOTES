import axios, { AxiosInstance } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: '/api/',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем перехватчик для токена
api.interceptors.request.use((config: any) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Обрабатываем 401 ошибки
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post('/api/auth/token/refresh/', {
            refresh: refreshToken,
          })

          const newAccess = response.data.access
          localStorage.setItem('access_token', newAccess)

          // Обновляем токен в заголовке
          originalRequest.headers = originalRequest.headers || {}
          originalRequest.headers.Authorization = `Bearer ${newAccess}`

          // Обновляем также в глобальных настройках экземпляра
          api.defaults.headers.common.Authorization = `Bearer ${newAccess}`

          return api(originalRequest)
        }
      } catch (refreshError) {
        // Если рефреш не удался - очищаем всё
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/auth'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export interface Tag {
  id?: number
  name: string
  color?: string
}

export interface Note {
  id?: number
  title: string
  content: string
  tags?: any[]
  created_at?: string
  updated_at?: string
  creation_date?: string
  last_change_date?: string
}

export const notesApi = {
  getAll: (): Promise<any> => api.get('/notes/'),
  getById: (id: number): Promise<any> => api.get(`/notes/${id}/`),
  create: (noteData: Omit<Note, 'id'>): Promise<any> => api.post('/notes/', noteData),
  update: (id: number, noteData: Partial<Note>): Promise<any> =>
    api.patch(`/notes/${id}/`, noteData),
  delete: (id: number): Promise<any> => api.delete(`/notes/${id}/`),
}

export const tagsApi = {
  getAll: (): Promise<any> => api.get('/tags/'),
  getById: (id: number): Promise<any> => api.get(`/tags/${id}/`),
  create: (tagData: Tag): Promise<any> => api.post('/tags/', tagData),
  update: (id: number, tagData: Partial<Tag>): Promise<any> => api.patch(`/tags/${id}/`, tagData),
  delete: (id: number): Promise<any> => api.delete(`/tags/${id}/`),
  getNotesByTag: (tagId: number): Promise<any> => api.get(`/tags/${tagId}/notes/`),
}

export const ideaApi = {
  getIdeaOfDay: (): Promise<any> => api.get('/ideas/today/'),
  markAsShown: (noteId: number): Promise<any> =>
    api.post('/ideas/today/mark_shown/', { note_id: noteId }),
  resetShownStatus: (): Promise<any> => api.post('/ideas/today/reset_shown/'),
  getStatistics: (): Promise<any> => api.get('/ideas/today/statistics/'),
}

export const checklistApi = {
  generate: (config: any): Promise<any> => api.post('/checklists/generate/', config),
  getAll: (): Promise<any> => api.get('/checklists/'),
  getById: (id: number): Promise<any> => api.get(`/checklists/${id}/`),
  delete: (id: number): Promise<any> => api.delete(`/checklists/${id}/`),
  toggleItem: (checklistId: number, itemId: number): Promise<any> =>
    api.post(`/checklists/${checklistId}/toggle_completed/`, { item_id: itemId }),
  saveAsNote: (checklistId: number): Promise<any> =>
    api.post(`/checklists/${checklistId}/save_as_note/`),
  regenerate: (checklistId: number): Promise<any> =>
    api.post(`/checklists/${checklistId}/regenerate/`),
}

export default api
