import { createRouter, createWebHistory } from 'vue-router'
import TasksView from '../views/TasksView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'tasks',
      component: TasksView
    }
  ]
})

export default router 