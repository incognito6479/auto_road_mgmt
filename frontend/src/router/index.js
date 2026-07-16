import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import CategoriesView from '@/views/CategoriesView.vue'
import CategoryDetailView from '@/views/CategoryDetailView.vue'
import StudentsView from '@/views/StudentsView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresGuest: true }, // redirect to home if already logged in
  },
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
    path: '/categories',
    name: 'categories',
    component: CategoriesView,
    meta: { requiresAuth: true },
  },
  {
    path: '/categories/:id',
    name: 'category-detail',
    component: CategoryDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/students',
    name: 'students',
    component: StudentsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/groups',
    name: 'groups',
    component: () => import('@/views/GroupsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/groups/:id',
    name: 'group-detail',
    component: () => import('@/views/GroupDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/billing',
    name: 'billing',
    component: () => import('@/views/PaymentsView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Not logged in → redirect to login
    next({ name: 'login' })
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // Already logged in → redirect to home
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
