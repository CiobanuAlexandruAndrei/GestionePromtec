import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      meta: { requiresAuth: true },
      component: () => import('../views/HomeView.vue'),
      beforeEnter: (to, from, next) => {
        const authStore = useAuthStore()
        // Instead of redirecting, we'll modify the component to be rendered
        if (to.matched[0] && to.matched[0].components) {
          to.matched[0].components.default = authStore.isAdmin 
            ? () => import('../views/admin/SlotsView.vue')
            : () => import('../views/user/UserHomeView.vue')
        }
        next()
      }
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/admin/UsersView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/logout',
      name: 'logout',
      component: () => import('../views/LogoutView.vue'),
      meta: { public: true }
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/SignupView.vue'),
      meta: { public: true }
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('@/views/ForgotPasswordView.vue'),
      meta: { public: true }
    },
    {
      path: '/reset-password/:token',
      name: 'reset-password',
      component: () => import('@/views/ResetPasswordView.vue'),
      meta: { public: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
      meta: { public: true }
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('../views/user/ContactView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/slot/:id',
      name: 'slot-details',
      component: () => import('../views/NotFoundView.vue'), // fallback component
      beforeEnter: (to, _from, next) => {
        const authStore = useAuthStore()
        // Instead of redirecting, we'll modify the component to be rendered
        if (to.matched[0]?.components) {
          to.matched[0].components.default = authStore.isAdmin 
            ? () => import('../views/admin/SlotDetails.vue')
            : () => import('../views/user/SlotUserView.vue')
        }
        next()
      },
      meta: { requiresAuth: true }
    },/*
    {
      path: '/slot/:id/registrations',
      name: 'slot-registrations',
      component: () => import('../views/user/SlotUserView.vue'),
      meta: { requiresAuth: true }
    }*/
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }

  // Check if route requires admin role
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    console.log('Access denied: Admin privileges required')
    next('/')
    return
  }

  // Redirect authenticated users away from login
  if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
    return
  }

  next()
})

export default router
