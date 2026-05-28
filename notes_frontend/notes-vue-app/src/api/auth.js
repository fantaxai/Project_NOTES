// api/auth.js
import api from './index'

export const authAPI = {
  register(userData) {
    return api.post('/auth/register/', userData)
  },

  login(credentials) {
    return api.post('/auth/login/', credentials)
  },

  logout(refreshToken) {
    return api.post('/auth/logout/', { refresh: refreshToken })
  },

  getProfile() {
    return api.get('/auth/me/')
  },
}
