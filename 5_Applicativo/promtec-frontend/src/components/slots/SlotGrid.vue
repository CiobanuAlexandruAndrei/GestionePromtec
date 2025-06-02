<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
    <article
      v-for="slot in slots"
      :key="slot.id"
      class="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-100 hover:shadow-md transition-shadow duration-200 max-w-sm"
    >
      <div class="p-4">
        <div class="flex justify-between items-start mb-4">
          <div>
            <div class="flex items-center gap-2 mb-1.5">
              <span
                class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium"
                :class="getDepartmentColor(slot.department)"
              >
                {{ slot.department }}
              </span>
            </div>
            <h3 class="text-lg font-semibold text-gray-800 mt-1">{{ formatDate(slot.date) }}</h3>
            <div class="flex items-center text-sm text-gray-500 mt-0.5">
              <Clock class="h-4 w-4 mr-1" />
              <span>{{ getPeriodText(slot.time_period ?? '') }}</span>
              <span class="mx-1">•</span>
              <div class="flex items-center">
                <component
                  :is="getGenderIcon(slot.gender_category ?? '')"
                  class="h-4 w-4 mr-1"
                  :class="getGenderColor(slot.gender_category ?? '')"
                />
                <span>{{ getGenderText(slot.gender_category ?? '') }}</span>
              </div>
            </div>
          </div>
          <div v-if="auth.isAdmin" class="flex space-x-1">
            <button
              class="p-1 rounded-md text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
              @click="$emit('edit', slot)"
            >
              <Edit class="h-4 w-4" />
            </button>
            <button
              class="p-1 rounded-md text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
              @click="$emit('delete', slot.id)"
            >
              <Trash2 class="h-4 w-4" />
            </button>
          </div>
        </div>

        <div class="mt-2">
          <div class="flex items-center justify-between mb-1">
            <div class="flex items-center">
              <UserCheck class="h-4 w-4 text-gray-500 mr-1" />
              <span class="text-sm text-gray-500">Iscritti</span>
            </div>
            <span class="text-sm font-medium">{{ slot.occupied_spots }}/{{ slot.total_spots }}</span>
          </div>

          <div class="w-full bg-gray-100 rounded-full h-2">
            <div
              class="h-2 rounded-full"
              :class="getStatusColor(calculateFillPercentage(slot.occupied_spots, slot.total_spots))"
              :style="{ width: calculateFillPercentage(slot.occupied_spots, slot.total_spots) + '%' }"
            ></div>
          </div>
        </div>

        <div class="mt-3 pt-2 border-t border-gray-100 flex justify-between items-center">
          <span
            v-if="slot.is_locked"
            class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800"
          >
            <Lock class="h-3.5 w-3.5 mr-1.5" />
            Iscrizioni bloccate
          </span>
          <span v-else class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <CheckCircle2 class="h-3.5 w-3.5 mr-1.5" />
            Iscrizioni aperte
          </span>
          <RouterLink
            :to="'/slot/' + slot.id"
            class="flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-700"
          >
            Dettagli
            <ChevronRight class="h-4 w-4 ml-1" />
          </RouterLink>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { Clock, UserCheck, Edit, Trash2, ChevronRight, Lock, Users, User, UserSquare2, CheckCircle2 } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth'
import type { Slot } from '@/types/slot'

const auth = useAuthStore()

defineProps<{
  slots: Slot[]
}>()

defineEmits<{
  edit: [slot: Slot]
  delete: [id: number]
}>()

const formatDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: '2-digit', day: '2-digit' }
  return new Date(dateString).toLocaleDateString('it-IT', options)
}

const getDepartmentColor = (department: string | null | undefined) => {
  if (!department) return 'bg-gray-100 text-gray-800'
  
  switch (department) {
    case 'Settore Tecnologie Innovative':
      return 'bg-indigo-100 text-indigo-800'
    case 'Settore Costruzioni':
      return 'bg-amber-100 text-amber-800'
    case 'Settore Chimica':
      return 'bg-emerald-100 text-emerald-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getPeriodText = (period: string | null | undefined): string => {
  if (!period) return 'N/D'
  
  switch (period.toLowerCase()) {
    case 'mattina':
    case 'morning':
      return 'Mattina'
    case 'pomeriggio':
    case 'afternoon':
      return 'Pomeriggio'
    default:
      return period
  }
}

const getGenderIcon = (gender: string | null | undefined) => {
  if (!gender) return Users
  
  switch (gender.toLowerCase()) {
    case 'misto':
    case 'mixed':
      return Users
    case 'solo ragazzi':
    case 'boys only':
      return User
    case 'solo ragazze':
    case 'girls only':
      return UserSquare2
    default:
      return Users
  }
}

const getGenderColor = (gender: string | null | undefined) => {
  if (!gender) return 'text-gray-500'
  
  switch (gender.toLowerCase()) {
    case 'misto':
      return 'text-purple-500'
    case 'solo ragazzi':
    case 'maschile':
      return 'text-blue-500'
    case 'solo ragazze':
    case 'femminile':
      return 'text-pink-500'
    default:
      return 'text-gray-500'
  }
}

const getGenderText = (gender: string | null | undefined): string => {
  if (!gender) return 'N/D'
  return gender // The API already returns the correct Italian text
}

const calculateFillPercentage = (registered: number, total: number) => {
  return (registered / total) * 100
}

const getStatusColor = (percentage: number) => {
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 70) return 'bg-amber-500'
  return 'bg-emerald-500'
}
</script>