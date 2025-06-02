<template>
  <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl overflow-hidden max-w-lg w-full mx-4">
      <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
        <h3 class="text-lg font-medium leading-6 text-gray-900">
          Modifica studente
        </h3>
        <button @click="$emit('close')" type="button" class="text-gray-400 hover:text-gray-500">
          <XIcon class="h-5 w-5" />
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit">
        <div class="p-6 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Input fields -->
            <div class="relative">
              <label for="firstName" class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input
                id="firstName"
                v-model="form.firstName"
                type="text"
                required
                disabled
                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
              />
            </div>

            <div class="relative">
              <label for="lastName" class="block text-sm font-medium text-gray-700 mb-1">Cognome</label>
              <input
                id="lastName"
                v-model="form.lastName"
                type="text"
                required
                disabled
                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
              />
            </div>

            <div class="relative">
              <label for="school" class="block text-sm font-medium text-gray-700 mb-1">Scuola</label>
              <input
                id="school"
                v-model="form.school"
                type="text"
                required
                disabled
                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
              />
            </div>
            
            <!-- Grade -->
            <div class="relative">
              <label for="grade" class="block text-sm font-medium text-gray-700 mb-1">Classe</label>
              <input
                id="grade"
                v-model="form.grade"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block hover:border-gray-400 transition-colors"
              />
            </div>
            
           
          </div>
          
          <!-- Address Section -->
          <div class="space-y-4">
            <div class="relative">
              <label for="street" class="block text-sm font-medium text-gray-700 mb-1">Indirizzo</label>
              <input
                id="street"
                v-model="form.street"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block hover:border-gray-400 transition-colors"
              />
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="relative">
                <label for="zipCode" class="block text-sm font-medium text-gray-700 mb-1">CAP</label>
                <input
                  id="zipCode"
                  v-model="form.zipCode"
                  type="text"
                  required
                  class="w-full px-4 py-2.5 bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block hover:border-gray-400 transition-colors"
                />
              </div>
              
              <div class="relative">
                <label for="city" class="block text-sm font-medium text-gray-700 mb-1">Città</label>
                <input
                  id="city"
                  v-model="form.city"
                  type="text"
                  required
                  class="w-full px-4 py-2.5 bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block hover:border-gray-400 transition-colors"
                />
              </div>
            </div>
          </div>
          
          <!-- Contact Details -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="relative">
              <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Telefono</label>
              <input
                id="phone"
                v-model="form.phone"
                type="text"
                class="w-full px-4 py-2.5 bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block hover:border-gray-400 transition-colors"
              />
            </div>
            
            <div class="relative">
              <label for="mobile" class="block text-sm font-medium text-gray-700 mb-1">Cellulare</label>
              <input
                id="mobile"
                v-model="form.mobile"
                type="text"
                required
                class="w-full px-4 py-2.5 bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block hover:border-gray-400 transition-colors"
              />
            </div>
          </div>
        </div>
        
        <div class="px-6 py-4 bg-gray-50 flex justify-end space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Annulla
          </button>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 flex items-center"
          >
            <LoaderIcon v-if="isSubmitting" class="animate-spin h-4 w-4 mr-2" />
            Salva modifiche
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { XIcon, LoaderIcon } from 'lucide-vue-next'
import type { Student } from '@/types/slot'
import { Gender } from '@/types/slot'

const props = defineProps({
  student: {
    type: Object as () => Partial<Student>,
    required: true
  },
  isSubmitting: {
    type: Boolean,
    default: false
  },
  isAdminView: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', formData: Partial<Student>): void
}>()

const form = ref<Partial<Student>>({
  firstName: '',
  lastName: '',
  school: '',
  grade: '',
  gender: Gender.BOY,
  street: '',
  zipCode: '',
  city: '',
  phone: '',
  mobile: ''
})

onMounted(() => {
  // Initialize form with student data
  if (props.student) {
    form.value = { ...props.student }
  }
})

const handleSubmit = () => {
  emit('submit', form.value)
}
</script>