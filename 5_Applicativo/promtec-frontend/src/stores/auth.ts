import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  is_admin: boolean
}

interface AuthState {
  token: string | null
  user: User | null
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const state = ref<AuthState>({
    token: localStorage.getItem('token'),
    user: loadUserFromStorage()
  })

  // Getters
  const isAuthenticated = computed(() => !!state.value.token)
  const isAdmin = computed(() => state.value.user?.is_admin ?? false)
  const currentUser = computed(() => state.value.user)
  const userFullName = computed(() => {
    if (!state.value.user) return ''
    return `${state.value.user.first_name} ${state.value.user.last_name}`.trim()
  })

  // Actions
  function setAuth(token: string, user: User) {
    state.value.token = token
    state.value.user = user
    
    // Persist to localStorage
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
  }

  function clearAuth() {
    state.value.token = null
    state.value.user = null
    
    // Clear localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Helper function to load user from storage
  function loadUserFromStorage(): User | null {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null
    
    try {
      return JSON.parse(userStr)
    } catch (e) {
      console.error('Failed to parse user from localStorage:', e)
      return null
    }
  }

  return {
    // State
    token: computed(() => state.value.token),
    user: currentUser,
    
    // Getters
    isAuthenticated,
    isAdmin,
    userFullName,
    
    // Actions
    setAuth,
    clearAuth
  }
})