<template>
  <BaseModal title="Crea Nuovo Slot" @close="$emit('close')">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Display error message if exists -->
      <div v-if="error" class="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg" role="alert">
        <div class="flex items-center">
          <XCircle class="h-5 w-5 mr-2" />
          <span>{{ error }}</span>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Date -->
        <div class="col-span-2 md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Data</label>
          <div class="relative">
            <Calendar class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="text"
              v-model="displayDate"
              required
              placeholder="dd/mm/yyyy"
              maxlength="10"
              @input="formatDateInput"
              @blur="validateDate"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white"
            />
            <!-- Hidden calendar for date picker functionality -->
            <input
              type="date"
              :min="todayISO"
              class="absolute opacity-0 right-2 w-8 h-8 cursor-pointer"
              @change="handleCalendarInput"
            />
          </div>
        </div>

        <!-- Period -->
        <div class="col-span-2 md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Periodo</label>
          <div class="relative">
            <Clock class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <select
              v-model="form.time_period"
              required
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm appearance-none bg-white"
            >
              <option value="" disabled>Seleziona periodo</option>
              <option v-for="period in enums?.time_periods" :key="period" :value="period">
                {{ period }}
              </option>
            </select>
            <ChevronDown class="absolute right-3 top-2.5 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        <!-- Department -->
        <div class="col-span-2 md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Dipartimento</label>
          <div class="relative">
            <BookOpen class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <select
              v-model="form.department"
              required
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm appearance-none bg-white"
            >
              <option value="" disabled>Seleziona dipartimento</option>
              <option v-for="dept in enums?.departments" :key="dept" :value="dept">
                {{ dept }}
              </option>
            </select>
            <ChevronDown class="absolute right-3 top-2.5 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        <!-- Gender Category -->
        <div class="col-span-2 md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
          <div class="relative">
            <Users class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <select
              v-model="form.gender_category"
              required
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm appearance-none bg-white"
            >
              <option value="" disabled>Seleziona categoria</option>
              <option v-for="category in enums?.gender_categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
            <ChevronDown class="absolute right-3 top-2.5 h-4 w-4 text-gray-400 pointer-events-none" />
          </div>
        </div>

        <!-- Total Spots -->
        <div class="col-span-2 md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Posti Totali</label>
          <div class="relative">
            <Users class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="number"
              v-model.number="form.total_spots"
              required
              min="1"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white"
            />
          </div>
        </div>

        <!-- Max Students Per School -->
        <div class="col-span-2 md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Max studenti per scuola
            <span class="text-xs text-gray-500">(per responsabile)</span>
          </label>
          <div class="relative">
            <School class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="number"
              v-model.number="form.max_students_per_school"
              required
              min="1"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white"
            />
          </div>
        </div>

        <!--
       
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Note</label>
          <div class="relative">
            <ClipboardList class="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <textarea
              v-model="form.notes"
              rows="3"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white"
              placeholder="Aggiungi note o informazioni aggiuntive..."
            ></textarea>
          </div>
        </div>

    
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            <input
              type="checkbox"
              v-model="form.is_locked"
              class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            Bloccato
          </label>
        </div>

        -->
      </div>

      <div class="mt-6 flex justify-end space-x-3">
        <button
          type="button"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 bg-white"
          @click="$emit('close')"
        >
          Annulla
        </button>
        <button
          type="submit"
          class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
        >
          Crea
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Calendar, Clock, Users, ChevronDown, School, ClipboardList, BookOpen, XCircle } from 'lucide-vue-next'
import BaseModal from '../BaseModal.vue'
import type { SlotEnums, CreateSlotRequest } from '@/types/slot'
import { formatDateToDDMMYYYY, convertDDMMYYYYToISO } from '@/utils/formatting'

const props = defineProps<{
  enums: SlotEnums | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'create', slot: CreateSlotRequest): void
  (e: 'error', message: string): void
}>()

const error = ref<string | null>(null)

const form = ref<CreateSlotRequest>({
  date: '',
  time_period: '',
  department: '',
  gender_category: '',
  notes: '',
  total_spots: 24,
  max_students_per_school: 10,
  is_locked: false
})

// Date formatted as dd/mm/yyyy for display
const displayDate = ref('')

// Format input as user types to enforce dd/mm/yyyy pattern
const formatDateInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  let value = input.value.replace(/[^0-9\/]/g, '') // Keep only numbers and slashes
  
  // Auto-insert slashes
  if (value.length > 0) {
    const numbersOnly = value.replace(/\//g, '')
    
    if (numbersOnly.length <= 2) {
      // Just day
      displayDate.value = numbersOnly
    } else if (numbersOnly.length <= 4) {
      // Day and month
      displayDate.value = `${numbersOnly.substring(0, 2)}/${numbersOnly.substring(2)}`
    } else {
      // Full date
      displayDate.value = `${numbersOnly.substring(0, 2)}/${numbersOnly.substring(2, 4)}/${numbersOnly.substring(4, 8)}`
    }
  }
}

// Handle when a date is selected from the calendar
const handleCalendarInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.value) {
    form.value.date = input.value // Update the form with ISO date
    displayDate.value = formatDateToDDMMYYYY(input.value) // Update display date
  }
}

// Validate and convert the manually entered date
const validateDate = () => {
  if (!displayDate.value) return
  
  const datePattern = /^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/(\d{4})$/
  if (!datePattern.test(displayDate.value)) {
    // If invalid format, reset to empty
    displayDate.value = form.value.date ? formatDateToDDMMYYYY(form.value.date) : ''
    return
  }
  
  // Convert dd/mm/yyyy to ISO format for the form data
  form.value.date = convertDDMMYYYYToISO(displayDate.value)
}

// Generate today's date in ISO format for internal use
const todayISO = new Date().toISOString().split('T')[0]
// Format today's date as dd/mm/yyyy for display
const today = formatDateToDDMMYYYY(todayISO)

const handleSubmit = () => {
  error.value = null // Reset error before submitting
  // Validate date before submitting
  validateDate()
  try {
    emit('create', form.value)
  } catch (e: any) {
    // Handle any local validation errors
    error.value = e.message || 'Si è verificato un errore nella validazione del form'
  }
}

// Listen for errors from parent component
defineExpose({
  setError: (message: string) => {
    error.value = message
  }
})
</script>

<style scoped>
/* Add your modal styling here */
</style>