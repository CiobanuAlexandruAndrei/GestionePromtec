<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-100">
    <!-- Header -->
    <div class="border-b border-gray-100">
      <div class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-lg font-semibold text-gray-800">Lista d'attesa</h2>
              <div class="relative group">
                <HelpCircle class="h-5 w-5 text-gray-400 hover:text-gray-500 cursor-help relative z-10" />
                <div class="fixed opacity-0 invisible group-hover:opacity-100 group-hover:visible -translate-y-full bg-gray-900 text-white text-sm rounded-lg p-3 shadow-xl transition-all duration-200 pointer-events-none"
                     :style="{
                       top: 'var(--tooltip-y, 0px)',
                       left: 'var(--tooltip-x, 0px)',
                       width: '288px', // w-72 equivalent
                     }"
                >
                  <p class="text-white">La lista d'attesa si attiva automaticamente quando tutti i posti sono occupati. Gli studenti vengono inseriti in ordine di registrazione e verranno automaticamente spostati nella lista degli iscritti se si libera un posto.</p>
                  <div class="absolute left-1/2 -translate-x-1/2 top-full w-2 h-2 bg-gray-900 transform rotate-45"></div>
                </div>
              </div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                {{ students.length }} {{ students.length === 1 ? 'studente' : 'studenti' }}
              </span>
            </div>

            <p class="mt-1 text-sm text-stone-500">
                Se ci dovessero essere cambiamenti modifica gli studenti nella lista
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Students List -->
    <div class="divide-y divide-gray-100">
      <div 
        v-for="student in students" 
        :key="student.id"
        class="p-4 hover:bg-gray-50 transition-colors duration-150"
      >
        <div class="flex items-center justify-between">
          <!-- Student Info -->
          <div class="min-w-0 flex-1">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div 
                  class="h-10 w-10 rounded-full flex items-center justify-center bg-gray-100"
                >
                  <User
                    class="h-5 w-5 text-gray-600"
                  />
                </div>
              </div>
              <div>
                <h3 class="text-sm font-medium text-gray-900">
                  {{ student.firstName }} {{ student.lastName }}
                </h3>
                <div class="mt-1 text-sm text-gray-500">
                  {{ student.grade }}
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center space-x-3">
            <button
  
              @click="$emit('move', student)"
              class="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md"
              :class="[
                canPromoteFromWaitingList(student) && !isLocked
                  ? 'text-indigo-700 bg-indigo-50 hover:bg-indigo-100'
                  : 'text-gray-400 bg-gray-50 cursor-not-allowed'
              ]"
              :title="isLocked ? 'Slot bloccato' : (!canPromoteFromWaitingList(student) ? 'Limite scuola raggiunto' : 'Sposta negli iscritti')"
              :disabled="isLocked || !canPromoteFromWaitingList(student)"
            >
              <MoveLeft class="h-4 w-4 mr-1.5" />
              Sposta
            </button>

            <!-- Edit/Delete buttons -->
            <div class="flex items-center space-x-1">
              <button
                @click="$emit('edit', student)"
                class="p-1.5 rounded-md text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                title="Modifica"
              >
                <Edit class="h-4 w-4" />
              </button>
              <button
                @click="$emit('delete', student)"
                class="p-1.5 rounded-md text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
                title="Elimina"
              >
                <Trash2 class="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="students.length === 0" class="p-8 text-center">
        <div class="mx-auto h-12 w-12 rounded-full bg-gray-100 flex items-center justify-center">
          <ClipboardList class="h-6 w-6 text-gray-400" />
        </div>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Nessuno studente in lista d'attesa</h3>
        
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  User, 
  Edit, 
  Trash2, 
  MoveLeft,
  ClipboardList,
  HelpCircle
} from 'lucide-vue-next'
import type { ExtendedStudent, StudentStatus } from '@/types/slot'
import { Gender } from '@/types/slot'
import { onMounted, onUnmounted } from 'vue'

const isMaleGender = (gender: Gender | string) => {
  return gender === Gender.BOY || gender === 'Maschio' || gender === 'M'
}

const props = defineProps<{
  students: ExtendedStudent[];
  canModify?: boolean;
  isLocked?: boolean;
  canPromoteFromWaitingList: (student: ExtendedStudent) => boolean;
}>();

defineEmits<{
  move: [student: ExtendedStudent];
  edit: [student: ExtendedStudent];
  delete: [student: ExtendedStudent];
}>();

// Add tooltip positioning logic
onMounted(() => {
  const updateTooltipPosition = () => {
    const helpIcon = document.querySelector('.group .cursor-help') as HTMLElement
    if (helpIcon) {
      const rect = helpIcon.getBoundingClientRect()
      document.documentElement.style.setProperty('--tooltip-y', `${rect.top}px`)
      document.documentElement.style.setProperty('--tooltip-x', `${rect.left - 144 + rect.width/2}px`) // 144px is half of tooltip width
    }
  }

  window.addEventListener('scroll', updateTooltipPosition)
  window.addEventListener('resize', updateTooltipPosition)
  updateTooltipPosition()

  onUnmounted(() => {
    window.removeEventListener('scroll', updateTooltipPosition)
    window.removeEventListener('resize', updateTooltipPosition)
  })
})
</script>