import { createRouter, createWebHistory } from 'vue-router'
import CreateNoteView from '../views/CreateNoteView.vue'
import NoteView from '../views/NoteView.vue'
import NotelistView from '../views/NotelistView.vue'

const routes = [
  {
    path: '/',
    redirect: '/notes',
  },
  {
    path: '/create',
    name: 'create',
    component: CreateNoteView,
  },
  {
    path: '/notes',
    name: 'notes',
    component: NotelistView,
  },
  {
    path: '/note/:id',
    name: 'note',
    component: NoteView,
  },
]

const router = createRouter({
  history: createWebHistory('/'),
  routes,
})

export default router
