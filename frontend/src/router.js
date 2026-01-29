import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
  },
  {
    path: '/',
    name: 'MainList',
    component: () => import('./views/MainList.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/recipes',
    name: 'Recipes',
    component: () => import('./views/Recipes.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('./views/History.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/items',
    name: 'Items',
    component: () => import('./views/Items.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/shopping',
    name: 'Shopping',
    component: () => import('./views/Shopping.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/Settings.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && authStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
