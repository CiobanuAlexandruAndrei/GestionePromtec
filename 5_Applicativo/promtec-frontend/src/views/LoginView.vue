<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <div class="flex-grow flex items-center justify-center">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-sm">
      <div class="flex flex-col items-center">
        <div class="h-16 w-16 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold mb-6">
          <img
            src="@/assets/img/logo_cpt.jpg"
            alt="CPT Logo"
            class="w-full h-full object-contain rounded-lg"
          />
        </div>
        <h2 class="text-2xl font-semibold text-gray-800">Accedi a Gestione Promtec</h2>
        <p class="mt-2 text-sm text-gray-600">
          Oppure
          <router-link to="/signup" class="text-indigo-600 hover:text-indigo-700 font-medium">
            registrati
          </router-link>
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>

        <div class="space-y-4">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email
            </label>
            <div class="relative mt-1">
              <input
                id="email"
                v-model="email"
                name="email"
                type="text"
                required
                autocomplete="username"
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between">
              <label for="password" class="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div class="text-sm">
                <router-link to="/forgot-password" class="font-medium text-indigo-600 hover:text-indigo-500">
                  Password dimenticata?
                </router-link>
              </div>
            </div>
            <div class="relative mt-1">
              <input
                id="password"
                v-model="password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isLoading">Accedendo...</span>
          <span v-else>Accedi</span>
        </button>
      </form>
    </div>
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { login } from '@/services/api'
import FooterComponent from '@/components/FooterComponent.vue'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  try {
    error.value = ''
    isLoading.value = true

    if (!email.value || !password.value) {
      throw new Error('Per favore, compila tutti i campi')
    }

    // Call the login API
    const response = await login(email.value, password.value)

    // Extract token and user from the response
    const { token, user } = response

    if (!token) {
      throw new Error('Login fallito')
    }

    // Store the token and user info in the auth store
    authStore.setAuth(token, user)

    // Redirect to the home page
    router.push('/')
  } catch (err: any) {
    // First try to get the most specific error message from the response
    if (err.response?.data) {
      // Check for detailed error message in various formats
      if (typeof err.response.data === 'string') {
        error.value = err.response.data
      } else if (err.response.data.detail) {
        error.value = err.response.data.detail
      } else if (err.response.data.message) {
        error.value = err.response.data.message
      } else if (err.response.data.error) {
        error.value = err.response.data.error
      } else if (err.response.data.errors) {
        // Handle validation errors from the backend
        const errors = err.response.data.errors
        error.value = Object.values(errors).flat().join(', ')
      } else if (Object.keys(err.response.data).length > 0) {
        // Try to extract any message from the response data
        const firstKey = Object.keys(err.response.data)[0]
        const firstValue = err.response.data[firstKey]
        if (typeof firstValue === 'string') {
          error.value = firstValue
        } else {
          error.value = `Errore: ${JSON.stringify(err.response.data)}`
        }
      } else {
        error.value = `Errore dal server (${err.response.status})`
      }
    } else {
      error.value = err instanceof Error ? err.message : 'Si è verificato un errore durante il login'
    }
    console.error('Login fallito:', err)
  } finally {
    isLoading.value = false
  }
}
</script>
