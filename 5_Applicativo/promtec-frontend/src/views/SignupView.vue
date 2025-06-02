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
        <h2 class="text-2xl font-semibold text-gray-800">Crea il tuo account</h2>
        <p class="mt-2 text-sm text-gray-600">
          Oppure
          <router-link to="/login" class="text-indigo-600 hover:text-indigo-700 font-medium">
            accedi al tuo account
          </router-link>
        </p>
      </div>

      <form v-if="!success" @submit.prevent="handleSubmit" class="mt-8 space-y-6">
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>

        <div class="space-y-4">
          <div>
            <label for="nome" class="block text-sm font-medium text-gray-700">
              Nome
            </label>
            <div class="relative mt-1">
              <input
                id="nome"
                v-model="nome"
                name="nome"
                type="text"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
          </div>
          <div>
            <label for="cognome" class="block text-sm font-medium text-gray-700">
              Cognome
            </label>
            <div class="relative mt-1">
              <input
                id="cognome"
                v-model="cognome"
                name="cognome"
                type="text"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
          </div>
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email
            </label>
            <div class="relative mt-1">
              <input
                id="email"
                v-model="email"
                name="email"
                type="email"
                required
                autocomplete="email"
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
          </div>
          <div>
            <label for="scuola" class="block text-sm font-medium text-gray-700">
              Scuola media
            </label>
            <div class="relative mt-1">
              <select
                id="scuola"
                v-model="scuola"
                name="scuola"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              >
                <option value="" disabled>Seleziona una scuola</option>
                <option v-for="school in schools" :key="school" :value="school">
                  {{ school }}
                </option>
              </select>
            </div>
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div class="relative mt-1">
              <input
                id="password"
                v-model="password"
                name="password"
                type="password"
                required
                autocomplete="new-password"
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                @input="validatePassword"
              />
            </div>
            <div class="mt-2 text-xs">
              <p class="font-medium mb-1">La password deve contenere:</p>
              <ul class="space-y-1 pl-1">
                <li class="flex items-center">
                  <span v-if="isLongEnough" class="text-green-500 mr-1">✓</span>
                  <span v-else class="text-red-500 mr-1">✗</span>
                  <span :class="isLongEnough ? 'text-green-600' : 'text-gray-600'">Almeno 8 caratteri</span>
                </li>
                <li class="flex items-center">
                  <span v-if="hasUpperCase" class="text-green-500 mr-1">✓</span>
                  <span v-else class="text-red-500 mr-1">✗</span>
                  <span :class="hasUpperCase ? 'text-green-600' : 'text-gray-600'">Almeno una lettera maiuscola</span>
                </li>
                <li class="flex items-center">
                  <span v-if="hasLowerCase" class="text-green-500 mr-1">✓</span>
                  <span v-else class="text-red-500 mr-1">✗</span>
                  <span :class="hasLowerCase ? 'text-green-600' : 'text-gray-600'">Almeno una lettera minuscola</span>
                </li>
                <li class="flex items-center">
                  <span v-if="hasNumber" class="text-green-500 mr-1">✓</span>
                  <span v-else class="text-red-500 mr-1">✗</span>
                  <span :class="hasNumber ? 'text-green-600' : 'text-gray-600'">Almeno un numero</span>
                </li>
                <li class="flex items-center">
                  <span v-if="hasSpecial" class="text-green-500 mr-1">✓</span>
                  <span v-else class="text-red-500 mr-1">✗</span>
                  <span :class="hasSpecial ? 'text-green-600' : 'text-gray-600'">Almeno un carattere speciale (!@#$%^&*(),.?":{}|<>)</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isLoading">Creazione account in corso...</span>
          <span v-else>Richiedi accesso</span>
        </button>
      </form>

      <div v-else class="mt-8 space-y-6">
        <div class="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg space-y-2">
          <p class="font-medium">Registrazione completata con successo!</p>
          <p>La tua richiesta è in attesa di approvazione da parte dell'amministratore. Riceverai una notifica via email quando il tuo account sarà attivato.</p>
          <p class="mt-4">Puoi tornare alla <router-link to="/login" class="text-indigo-600 hover:text-indigo-700 font-medium">pagina di login</router-link> quando vuoi.</p>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSchools } from '@/services/api'
import axios from 'axios'
import { API_URL } from '@/services/api'

const router = useRouter()

const nome = ref('')
const cognome = ref('')
const email = ref('')
const scuola = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const success = ref(false)
const schools = ref<string[]>([])

onMounted(async () => {
  try {
    schools.value = await getSchools()
  } catch (err) {
    console.error('Failed to fetch schools:', err)
    error.value = 'Errore nel caricamento delle scuole. Riprova più tardi.'
  }
})

const isLongEnough = ref(false)
const hasUpperCase = ref(false)
const hasLowerCase = ref(false)
const hasNumber = ref(false)
const hasSpecial = ref(false)

const validatePassword = () => {
  // Check length
  isLongEnough.value = password.value.length >= 8
  
  // Check for at least one number
  hasNumber.value = /\d/.test(password.value)
  
  // Check for at least one special character
  hasSpecial.value = /[!@#$%^&*(),.?":{}|<>]/.test(password.value)
  
  // Check for uppercase and lowercase letters
  hasUpperCase.value = /[A-Z]/.test(password.value)
  hasLowerCase.value = /[a-z]/.test(password.value)
}

const handleSubmit = async () => {
  try {
    error.value = ''
    success.value = false
    isLoading.value = true

    if (!nome.value || !cognome.value || !email.value || !scuola.value || !password.value) {
      throw new Error('Per favore, compila tutti i campi')
    }
    
    // Check password strength
    const passwordRequirements = [
      isLongEnough.value,
      hasUpperCase.value,
      hasLowerCase.value,
      hasNumber.value,
      hasSpecial.value
    ]
    const satisfiedRequirements = passwordRequirements.filter(Boolean).length
    
    if (satisfiedRequirements < 3) {
      throw new Error('La password non è abbastanza sicura. Deve contenere almeno 8 caratteri, numeri e lettere maiuscole/minuscole.')
    }

    // Register the user
    const response = await axios.post(`${API_URL}/security/create_user`, {
      email: email.value,
      password: password.value,
      first_name: nome.value,
      last_name: cognome.value,
      school_name: scuola.value
    })

    if (response.status === 201) {
      success.value = true
      // Clear form
      nome.value = ''
      cognome.value = ''
      email.value = ''
      scuola.value = ''
      password.value = ''
      
      // No redirect - user can decide when to go back to login
    }
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
      error.value = err instanceof Error ? err.message : 'Si è verificato un errore durante la registrazione'
    }
    console.error('Registrazione fallita:', err)
  } finally {
    isLoading.value = false
  }
}
</script>