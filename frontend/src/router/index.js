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
    path: '/students/:id',
    name: 'student-detail',
    component: () => import('@/views/StudentDetailView.vue'),
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
    redirect: '/finances/accepted',
  },
  {
    path: '/finances',
    redirect: '/finances/accepted',
  },
  {
    path: '/finances/accepted',
    name: 'finances-accepted',
    component: () => import('@/views/finances/FinancesAcceptedView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/finances/payments',
    name: 'finances-payments',
    component: () => import('@/views/finances/FinancesPaidView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/finances/returned',
    name: 'finances-returned',
    component: () => import('@/views/finances/FinancesReturnedView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/finances/bonus',
    name: 'finances-bonus',
    component: () => import('@/views/finances/FinancesBonusView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/finances/bank',
    name: 'finances-bank',
    component: () => import('@/views/finances/FinancesBankView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/finances/teachers',
    name: 'finances-teachers',
    component: () => import('@/views/finances/FinancesTeachersView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/finances/debts',
    name: 'finances-debts',
    component: () => import('@/views/finances/FinancesDebtsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('@/views/UsersView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/users/:id',
    name: 'user-detail',
    component: () => import('@/views/UserDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/learning-places',
    name: 'learning-places',
    component: () => import('@/views/LearningPlacesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/agents',
    name: 'agents',
    component: () => import('@/views/AgentsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/agents/:id',
    name: 'agent-detail',
    component: () => import('@/views/AgentDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/holidays',
    name: 'holidays',
    component: () => import('@/views/HolidaysView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/vehicles',
    name: 'vehicles',
    component: () => import('@/views/CarsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/cars',
    redirect: '/vehicles',
  },
  {
    path: '/lessons',
    name: 'lessons',
    component: () => import('@/views/LessonsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: () => import('@/views/NotificationsView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
    return
  }

  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchCurrentUser()
  }

  if (authStore.isStudent && authStore.user) {
    const studentDetailPath = `/students/${authStore.user.id}`
    if (to.path !== studentDetailPath && to.name !== 'login') {
      next({ name: 'student-detail', params: { id: authStore.user.id } })
      return
    }
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    if (authStore.isStudent && authStore.user) {
      next({ name: 'student-detail', params: { id: authStore.user.id } })
    } else {
      next({ name: 'home' })
    }
  } else {
    next()
  }
})

export default router
