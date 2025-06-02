<template>
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
      <h3 class="text-lg font-medium leading-6 text-gray-900">Studenti Iscritti</h3>
      <div class="flex items-center gap-4">
        <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
          {{ students.length }} studenti
        </span>
        <button
          @click="isCreating = true"
          :disabled="is_locked"
          class="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <UserPlus class="h-4 w-4 mr-1.5" />
          Nuovo Studente
        </button>
      </div>
    </div>
    
    <div class="border-t border-gray-200 divide-y divide-gray-200">
      <!-- Search and filters -->
      <div class="p-4 bg-gray-50">
        <div class="flex flex-col sm:flex-row gap-3">
          <div class="flex-grow">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Cerca studente..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            />
          </div>
          <div class="w-full sm:w-auto">
            <select
              v-model="schoolFilter"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            >
              <option value="">Tutte le scuole</option>
              <option v-for="school in uniqueSchools" :key="school" :value="school">
                {{ school }}
              </option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Studente
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Scuola
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Classe
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Data
              </th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Azioni
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="filteredStudents.length === 0">
              <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">
                Nessuno studente trovato
              </td>
            </tr>
            <tr v-for="student in filteredStudents" :key="student.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ student.lastName }} {{ student.firstName }}
                    </div>
                    <div class="text-xs text-gray-500 flex">
                      <UserIcon class="h-3 w-3 mr-1 mt-0.5" />
                      {{ student.gender }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ student.school }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ student.grade }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(student.registrationDate) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <button 
                    @click="$emit('edit', student)"
                    type="button" 
                    class="text-indigo-600 hover:text-indigo-900 transition-colors"
                    :disabled="is_locked"
                  >
                    <PencilIcon class="h-4 w-4" />
                  </button>
                  <button 
                    @click="$emit('move', student)"
                    type="button" 
                    class="text-yellow-600 hover:text-yellow-900 transition-colors"
                    :disabled="is_locked"
                  >
                    <ArrowRightIcon class="h-4 w-4" />
                  </button>
                  <button 
                    @click="$emit('delete', student)"
                    type="button" 
                    class="text-red-600 hover:text-red-900 transition-colors"
                    :disabled="is_locked"
                  >
                    <TrashIcon class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Student Modal -->
    <AdminStudentRegistrationModal
      v-if="isCreating"
      :is-submitting="isSubmitting"
      :slot-gender-category="slotGenderCategory"
      @close="isCreating = false"
      @submit="handleCreateSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineEmits } from 'vue'
import { UserIcon, PencilIcon, TrashIcon, ArrowRightIcon, UserPlus } from 'lucide-vue-next'
import AdminStudentRegistrationModal from './AdminStudentRegistrationModal.vue'
import { GenderCategory } from '@/types/slot'
import type { ExtendedStudent } from '@/types/slot'

const props = defineProps<{
  students: ExtendedStudent[];
  is_locked?: boolean;
  slotGenderCategory?: GenderCategory;
}>()

const emit = defineEmits<{
  (e: 'edit', student: ExtendedStudent): void
  (e: 'delete', student: ExtendedStudent): void
  (e: 'move', student: ExtendedStudent): void
  (e: 'createStudent', data: any): void
}>()

const searchQuery = ref('')
const schoolFilter = ref('')
const isCreating = ref(false)
const isSubmitting = ref(false)

const uniqueSchools = computed(() => {
  const schoolSet = new Set<string>()
  props.students.forEach(student => schoolSet.add(student.school))
  return Array.from(schoolSet).sort()
})

const filteredStudents = computed(() => {
  return props.students.filter(student => {
    const matchesSearch = !searchQuery.value || 
      `${student.firstName} ${student.lastName}`.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      student.school.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesSchool = !schoolFilter.value || student.school === schoolFilter.value
    
    return matchesSearch && matchesSchool
  })
})

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('it-IT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const handleCreateSubmit = (formData: any) => {
  emit('createStudent', formData)
  isCreating.value = false
  isSubmitting.value = false
}
</script>