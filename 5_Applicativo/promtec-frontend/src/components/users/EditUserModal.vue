<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { updateUser, getSchools } from '@/services/api'
import { HelpCircle } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  is_admin: boolean
  is_active: boolean
  school_name: string
}

interface Props {
  user: User
  isOpen: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update'): void
}>()

const firstName = ref(props.user.first_name)
const lastName = ref(props.user.last_name)
const email = ref(props.user.email)
const schoolName = ref(props.user.school_name)
const isAdmin = ref(props.user.is_admin)
const isActive = ref(props.user.is_active)
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const schools = ref<string[]>([])

// Get current logged in user for comparison
const authStore = useAuthStore()

// Directly check if user is editing their own account
const isSelfEdit = computed(() => {
  if (!authStore.user || !props.user) return false
  
  // Compare by email since id may not be present in localStorage
  return authStore.user.email === props.user.email
})

// Reset form when user changes
watch(() => props.user, (newUser) => {
  if (newUser) {
    firstName.value = props.user.first_name
    lastName.value = props.user.last_name
    email.value = props.user.email
    schoolName.value = props.user.school_name
    isAdmin.value = props.user.is_admin
    isActive.value = props.user.is_active
    password.value = ''
    error.value = ''
  }
})

onMounted(async () => {
  try {
    schools.value = await getSchools()
  } catch (err) {
    console.error('Failed to fetch schools:', err)
    error.value = 'Errore nel caricamento delle scuole. Riprova più tardi.'
  }
})

const handleSubmit = async () => {
  try {
    error.value = ''
    
    // If user is editing their own account and has entered a password,
    // check that the password is confirmed
    if (isSelfEdit.value && password.value) {
      if (password.value !== confirmPassword.value) {
        error.value = 'Le password non corrispondono'
        return
      }
    }
    
    await updateUser(props.user.id, {
      first_name: firstName.value,
      last_name: lastName.value,
      email: isSelfEdit.value ? props.user.email : email.value, // Don't allow email change for self
      school_name: schoolName.value,
      is_admin: isAdmin.value,
      is_active: isSelfEdit.value ? true : isActive.value, // Don't allow self-deactivation
      ...(password.value ? { password: password.value } : {})
    })
    emit('update')
    emit('close')
  } catch (err) {
    error.value = 'Errore durante l\'aggiornamento dell\'utente'
    console.error(err)
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

      <div class="inline-block bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all w-full max-w-lg">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6">
          <div class="mb-6 flex items-center justify-between">
            <div class="flex items-center">
              <h3 class="text-xl font-semibold text-gray-900">Modifica Utente</h3>
            </div>
          </div>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
              {{ error }}
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="firstName" class="block text-sm font-medium text-gray-700">Nome</label>
                <div class="relative mt-1">
                  <input
                    id="firstName"
                    v-model="firstName"
                    type="text"
                    required
                    class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                  />
                </div>
              </div>

              <div>
                <label for="lastName" class="block text-sm font-medium text-gray-700">Cognome</label>
                <div class="relative mt-1">
                  <input
                    id="lastName"
                    v-model="lastName"
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
                  v-model="email"
                  type="email"
                  required
                  :disabled="isSelfEdit"
                  :class="[
                    'block w-full px-3 py-2 border rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm',
                    isSelfEdit ? 'bg-gray-100 border-gray-200 cursor-not-allowed' : 'border-gray-300'
                  ]"
                />
                <p v-if="isSelfEdit" class="mt-1 text-xs text-gray-500 italic">Non è possibile modificare la propria email</p>
              </div>
            </div>

            <div>
              <label for="school" class="block text-sm font-medium text-gray-700">Scuola</label>
              <div class="relative mt-1">
                <select
                  id="school"
                  v-model="schoolName"
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
              <div class="flex items-center justify-between">
                <label for="password" class="block text-sm font-medium text-gray-700">
                  Password (lascia vuoto per non modificare)
                </label>
              </div>
              <div class="relative mt-1">
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                />
              </div>
            </div>
            
            <!-- Password confirmation field (shown only when editing own account) -->
            <div v-if="isSelfEdit" class="mt-4 border-t pt-4 border-gray-100">
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
                Conferma Password
              </label>
              <div class="relative mt-1">
                <input
                  id="confirmPassword"
                  v-model="confirmPassword"
                  type="password"
                  :class="[
                    'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm',
                    password && password !== confirmPassword ? 'border-red-300 ring-1 ring-red-500' : ''
                  ]"
                />
                <p v-if="password && password !== confirmPassword" class="mt-1 text-xs text-red-500">Le password non corrispondono</p>
              </div>
            </div>

            <div v-if="!isSelfEdit" class="bg-gray-50 px-4 py-3 rounded-lg space-x-6">
              <label class="inline-flex items-center">
                <input
                  v-model="isAdmin"
                  type="checkbox"
                  class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span class="ml-2 text-sm font-medium text-gray-700">Amministratore</span>
              </label>

              <label class="inline-flex items-center" :class="{ 'opacity-60 cursor-not-allowed': isSelfEdit }">
                <input
                  v-model="isActive"
                  type="checkbox"
                  :disabled="isSelfEdit"
                  class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <span class="ml-2 text-sm font-medium text-gray-700">Attivo</span>
                <span v-if="isSelfEdit" class="ml-2 text-xs text-gray-500 italic">(non modificabile)</span>
              </label>
            </div>

            <div class="mt-6 grid grid-cols-2 gap-3">
              <button
                type="button"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                @click="emit('close')"
              >
                Annulla
              </button>
              <button
                type="submit"
                class="w-full px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
              >
                Salva
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>