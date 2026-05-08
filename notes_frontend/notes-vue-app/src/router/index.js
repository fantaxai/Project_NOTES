import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('../views/AuthPage.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    redirect: '/notes',
  },
  {
    path: '/notes',
    name: 'notes',
    component: () => import('../views/NotelistView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/create',
    name: 'create',
    component: () => import('../views/CreateNoteView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/note/:id',
    name: 'note',
    component: () => import('../views/NoteView.vue'),
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Защита маршрутов
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Ждём проверки авторизации если ещё не проверена
  if (!authStore.isAuthChecked) {
    await authStore.checkAuth()
  }
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/auth')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/notes')
  } else {
    next()
  }
})

export default router