<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

      <div class="inline-block bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all w-full max-w-lg">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
          <div class="mb-6 flex items-center justify-between">
            <div class="flex items-center">
              <h3 class="text-xl font-semibold text-gray-900">Crea un nuovo utente</h3>
            </div>
            <button
              type="button"
              @click="$emit('close')"
              class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <span class="sr-only">Chiudi</span>
              <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            <!-- Error message -->
            <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
              {{ error }}
            </div>
            
            <!-- Success message -->
            <div v-if="success" class="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg text-sm">
              {{ success }}
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="first_name" class="block text-sm font-medium text-gray-700">Nome</label>
                <div class="relative mt-1">
                  <input
                    id="first_name"
                    v-model="formData.first_name"
                    type="text"
                    required
                    class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                  />
                </div>
              </div>

              <div>
                <label for="last_name" class="block text-sm font-medium text-gray-700">Cognome</label>
                <div class="relative mt-1">
                  <input
                    id="last_name"
                    v-model="formData.last_name"
                    type="text"
                    required
                    class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                  />
                </div>
              </div>
            </div>

            <div>
              <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
              <div class="relative mt-1">
                <input
                  id="email"
                  v-model="formData.email"
                  type="email"
                  required
                  class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                />
              </div>
            </div>

            <div>
              <label for="school_name" class="block text-sm font-medium text-gray-700">Scuola media</label>
              <div class="relative mt-1">
                <select
                  id="school_name"
                  v-model="formData.school_name"
                  required
                  class="block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                >
                  <option value="" disabled>Seleziona una scuola</option>
                  <option v-for="school in schools" :key="school" :value="school">
                    {{ school }}
                  </option>
                </select>
              </div>
            </div>

            <div>
              <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
              <div class="relative mt-1">
                <input
                  id="password"
                  v-model="formData.password"
                  type="password"
                  required
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
                    <span v-if="hasUppercase" class="text-green-500 mr-1">✓</span>
                    <span v-else class="text-red-500 mr-1">✗</span>
                    <span :class="hasUppercase ? 'text-green-600' : 'text-gray-600'">Almeno una lettera maiuscola</span>
                  </li>
                  <li class="flex items-center">
                    <span v-if="hasLowercase" class="text-green-500 mr-1">✓</span>
                    <span v-else class="text-red-500 mr-1">✗</span>
                    <span :class="hasLowercase ? 'text-green-600' : 'text-gray-600'">Almeno una lettera minuscola</span>
                  </li>
                  <li class="flex items-center">
                    <span v-if="hasNumbers" class="text-green-500 mr-1">✓</span>
                    <span v-else class="text-red-500 mr-1">✗</span>
                    <span :class="hasNumbers ? 'text-green-600' : 'text-gray-600'">Almeno un numero</span>
                  </li>
                  <li class="flex items-center">
                    <span v-if="hasSpecialChars" class="text-green-500 mr-1">✓</span>
                    <span v-else class="text-red-500 mr-1">✗</span>
                    <span :class="hasSpecialChars ? 'text-green-600' : 'text-gray-600'">Almeno un carattere speciale (!@#$%^&*(),.?":{}|<>)</span>
                  </li>
                </ul>
              </div>
            </div>

            <div class="pt-6 border-t border-gray-200 mt-6">
              <div class="flex justify-end space-x-3">
                <button
                  type="button"
                  @click="$emit('close')"
                  class="inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  :disabled="isLoading"
                  class="inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span v-if="isLoading">Creazione in corso...</span>
                  <span v-else>Crea utente</span>
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps, defineEmits, watch } from 'vue'
import { getSchools } from '@/services/api'
import axios from 'axios'
import { API_URL } from '@/services/api'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

// Define typed emits
type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'user-created', user: User): void;
}>()

const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  school_name: '',
  password: ''
})

const error = ref('')
const success = ref('')
const isLoading = ref(false)
const schools = ref<string[]>([])
const isLongEnough = ref(false)
const hasUppercase = ref(false)
const hasLowercase = ref(false)
const hasNumbers = ref(false)
const hasSpecialChars = ref(false)

onMounted(async () => {
  try {
    schools.value = await getSchools()
  } catch (err) {
    console.error('Failed to fetch schools:', err)
    error.value = 'Errore nel caricamento delle scuole. Riprova più tardi.'
  }
})

// Reset form when modal is closed
watch(() => props.show, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

const resetForm = () => {
  formData.value = {
    first_name: '',
    last_name: '',
    email: '',
    school_name: '',
    password: ''
  }
  error.value = ''
  success.value = ''
  isLongEnough.value = false
  hasUppercase.value = false
  hasLowercase.value = false
  hasNumbers.value = false
  hasSpecialChars.value = false
}

const validatePassword = () => {
  // Check length
  isLongEnough.value = formData.value.password.length >= 8
  
  // Check for uppercase, lowercase, numbers, special chars
  hasUppercase.value = /[A-Z]/.test(formData.value.password)
  hasLowercase.value = /[a-z]/.test(formData.value.password)
  hasNumbers.value = /\d/.test(formData.value.password)
  hasSpecialChars.value = /[!@#$%^&*(),.?":{}|<>]/.test(formData.value.password)
}

const handleSubmit = async () => {
  error.value = ''
  success.value = ''
  
  // Basic validation
  const passwordRequirements = [
    isLongEnough.value,
    hasUppercase.value,
    hasLowercase.value,
    hasNumbers.value,
    hasSpecialChars.value
  ]
  const satisfiedRequirements = passwordRequirements.filter(Boolean).length
  
  if (satisfiedRequirements < 3) {
    error.value = 'Per favore usa una password più sicura'
    return
  }
  
  isLoading.value = true
  
  try {
    // Get auth token from local storage
    const token = localStorage.getItem('token')
    
    if (!token) {
      error.value = 'Sessione scaduta. Per favore, effettua nuovamente il login.'
      isLoading.value = false
      return
    }
    
    // Make API request to create pre-approved user
    const response = await axios.post(
      `${API_URL}/security/create-pre-approved-user`,
      formData.value,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      }
    )
    
    success.value = 'Utente creato con successo. L\'utente riceverà una email di conferma.'
    
    // Emit event to parent
    setTimeout(() => {
      resetForm()
      isLoading.value = false
      // emit event to parent
      emit('user-created', response.data.user)
    }, 2000)
    
  } catch (err: any) {
    isLoading.value = false
    if (err.response && err.response.data && err.response.data.error) {
      error.value = err.response.data.error
    } else {
      error.value = 'Si è verificato un errore. Riprova più tardi.'
    }
  }
}
</script>
