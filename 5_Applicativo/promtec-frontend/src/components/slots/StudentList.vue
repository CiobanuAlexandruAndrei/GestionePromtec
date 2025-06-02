<template>
  <div class="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-100">
    <div class="border-b border-gray-100">
      <div class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-lg font-semibold text-gray-800">Studenti Iscritti</h2>
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
            <!-- Move button -->
            <button
              @click="$emit('move', student)"
              class="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md"
              :class="[
                !isLocked
                  ? 'text-indigo-700 bg-indigo-50 hover:bg-indigo-100'
                  : 'text-gray-400 bg-gray-50 cursor-not-allowed'
              ]"
              :disabled="isLocked"
              title="Sposta nella lista d'attesa"
            >
              <MoveRight class="h-4 w-4 mr-1.5" />
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
          <Users class="h-6 w-6 text-gray-400" />
        </div>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Nessuno studente iscritto</h3>
        
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Edit, Trash2, Users, MoveRight } from 'lucide-vue-next'
import type { Student, ExtendedStudent, StudentStatus } from '@/types/slot'
import { Gender } from '@/types/slot'

const isMaleGender = (gender: Gender | string) => {
  return gender === Gender.BOY || gender === 'Maschio' || gender === 'M'
}

const props = defineProps<{
  students: ExtendedStudent[];
  isLocked?: boolean;
  slotDate?: string;
  canModify?: boolean;
}>();

defineEmits<{
  edit: [student: ExtendedStudent];
  delete: [student: ExtendedStudent];
  move: [student: ExtendedStudent];
}>();

// Movement to waiting list should always be allowed if the slot is not locked
// regardless of spot availability
const canMoveToWaitingList = (student: ExtendedStudent) => {
  return !props.isLocked
}
</script>