<template>
  <div class="bg-white shadow rounded-lg overflow-hidden h-full">
    <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
      <h3 class="text-lg font-medium leading-6 text-gray-900">Lista di attesa</h3>
      <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
        {{ students.length }} studenti
      </span>
    </div>

    <!-- Admin note about bypassing school limits -->
    <div v-if="isAdminView" class="px-4 py-2 bg-indigo-50 border-t border-b border-indigo-100 flex items-center">
      <InfoIcon class="h-4 w-4 text-indigo-500 mr-1.5 flex-shrink-0" />
      <span class="text-xs text-indigo-700">
        Come amministratore, puoi spostare studenti nella lista iscritti anche se il limite per scuola è stato raggiunto.
      </span>
    </div>  

    <!-- No spots warning -->
    <div v-if="availableSlotSpots <= 0" class="px-4 py-2 bg-red-50 border-t border-b border-red-100 flex items-center">
      <AlertCircleIcon class="h-4 w-4 text-red-500 mr-1.5 flex-shrink-0" />
      <span class="text-xs text-red-700">
        Non ci sono posti disponibili nello slot. Impossibile spostare studenti nella lista iscritti.
      </span>
    </div>
    
    <div class="border-t border-gray-200 divide-y divide-gray-200 overflow-y-auto h-full" >
      <div v-if="students.length === 0" class="p-6 text-center text-gray-500">
        Nessuno studente in lista d'attesa
      </div>
      
      <!-- Group by school -->
      <div v-for="school in schools" :key="school" class="bg-gray-50">
        <div class="px-4 py-3 flex justify-between items-center bg-yellow-50 border-b border-yellow-100">
          <h4 class="text-sm font-medium text-gray-700">{{ school }}</h4>
          <span class="text-xs text-gray-500">
            {{ studentsForSchool(school).length }} studenti
          </span>
        </div>
        
        <div class="divide-y divide-gray-100">
          <div 
            v-for="student in studentsForSchool(school)" 
            :key="student.id"
            class="px-4 py-3 hover:bg-gray-50"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="text-sm font-medium text-gray-900">
                  {{ student.lastName }} {{ student.firstName }}
                </div>
                <div class="text-xs text-gray-500 flex items-center">
                  <UserIcon class="h-3 w-3 mr-1" />
                  {{ student.gender }} · {{ student.grade }}
                </div>
              </div>
              
              <div class="flex space-x-2">
                <button 
                  v-if="canPromote(student) || isAdminView"
                  @click="$emit('move', student)"
                  type="button" 
                  class="inline-flex items-center p-1 rounded-md text-gray-500 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                  :disabled="!canModify || availableSlotSpots <= 0"
                  :title="isAdminView ? (availableSlotSpots <= 0 ? 'Nessun posto disponibile' : 'Sposta negli iscritti (ignora limite scuola)') : 'Sposta negli iscritti'"
                  :class="{'opacity-50 cursor-not-allowed': availableSlotSpots <= 0}"
                >
                  <ArrowLeftIcon class="h-4 w-4" />
                </button>
                <button 
                  @click="$emit('edit', student)"
                  type="button" 
                  class="inline-flex items-center p-1 rounded-md text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                  :disabled="!canModify"
                  title="Modifica"
                >
                  <PencilIcon class="h-4 w-4" />
                </button>
                <button 
                  @click="$emit('delete', student)"
                  type="button" 
                  class="inline-flex items-center p-1 rounded-md text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
                  :disabled="!canModify"
                  title="Elimina"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </div>
            </div>
            
            <div class="mt-1 text-xs text-gray-500">
              {{ formatDate(student.registrationDate) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { UserIcon, PencilIcon, TrashIcon, ArrowLeftIcon, Info as InfoIcon, AlertCircle as AlertCircleIcon } from 'lucide-vue-next'
import type { ExtendedStudent } from '@/types/slot'

const props = defineProps<{
  students: ExtendedStudent[]
  schools: string[]
  canModify: boolean
  canPromote: (student: ExtendedStudent) => boolean
  isAdminView?: boolean
  availableSlotSpots: number
}>()

defineEmits<{
  (e: 'edit', student: ExtendedStudent): void
  (e: 'delete', student: ExtendedStudent): void
  (e: 'move', student: ExtendedStudent): void
}>()

const studentsForSchool = (schoolName: string) => {
  return props.students.filter(student => student.school === schoolName)
    .sort((a, b) => {
      // Sort by registration date (oldest first)
      return new Date(a.registrationDate || '').getTime() - new Date(b.registrationDate || '').getTime()
    })
}

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('it-IT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>