<template>
  <!-- Desktop view (lg and above) -->
  <div class="hidden lg:block overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="(header, index) in ['Data', 'Settore', 'Periodo', 'Genere', 'Iscritti per scuola', 'Stato']"
            :key="index"
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            {{ header }}
          </th>
          <th
            v-if="auth.isAdmin"
            scope="col"
            class="relative px-6 py-3"
          >
            <span class="sr-only">Azioni</span>
          </th>
          <th
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="slot in slots" :key="slot.id">
          <td class="px-6 py-4 whitespace-nowrap">
            {{ formatDate(slot.date) }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <span
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="getDepartmentColor(slot.department)"
            >
              {{ slot.department }}
            </span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            {{ getPeriodText(slot.time_period ?? '') }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center text-sm text-gray-900">
              <component
                :is="getGenderIcon(slot.gender_category ?? '')"
                class="h-4 w-4 mr-1"
                :class="getGenderColor(slot.gender_category ?? '')"
              />
              {{ getGenderText(slot.gender_category ?? '') }}
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm text-gray-900">
              {{ slot.occupied_spots }}/{{ slot.total_spots }}
            </div>
            <div class="w-24 bg-gray-100 rounded-full h-1.5 mt-1">
              <div
                class="h-1.5 rounded-full"
                :class="getStatusColor(calculateFillPercentage(slot.occupied_spots, slot.total_spots))"
                :style="{ width: calculateFillPercentage(slot.occupied_spots, slot.total_spots) + '%' }"
              ></div>
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <span
              v-if="slot.is_locked"
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800"
            >
              <Lock class="h-3.5 w-3.5 mr-1.5" />
              Iscrizioni bloccate
            </span>
            <span
              v-else
              class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800"
            >
              <CheckCircle2 class="h-3.5 w-3.5 mr-1.5" />
              Iscrizioni aperte
            </span>
          </td>
          <td
            v-if="auth.isAdmin"
            class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"
          >
            <div class="flex justify-end space-x-2">
              <button
                class="text-gray-500 hover:text-indigo-600"
                @click="$emit('edit', slot)"
                aria-label="Modifica slot"
              >
                <Edit class="h-4 w-4" />
              </button>
              <button
                class="text-gray-500 hover:text-red-600"
                @click="$emit('delete', slot.id)"
                aria-label="Elimina slot"
              >
                <Trash2 class="h-4 w-4" />
              </button>
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <RouterLink
              :to="'/slot/' + slot.id"
              class="flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-700"
            >
              Dettagli
              <ChevronRight class="h-4 w-4 ml-1" />
            </RouterLink>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- Mobile view (smaller than lg) -->
  <div class="lg:hidden space-y-4">
    <div 
      v-for="slot in slots" 
      :key="slot.id" 
      class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 space-y-3"
    >
      <div class="flex justify-between items-start">
        <div>
          <div class="font-medium">{{ formatDate(slot.date) }}</div>
          <div class="text-sm text-gray-500">{{ getPeriodText(slot.time_period ?? '') }}</div>
        </div>
        <span
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
          :class="getDepartmentColor(slot.department)"
        >
          {{ slot.department }}
        </span>
      </div>

      <div class="flex justify-between items-center border-t border-gray-100 pt-2">
        <div class="flex items-center text-sm text-gray-700">
          <component
            :is="getGenderIcon(slot.gender_category ?? '')"
            class="h-4 w-4 mr-1.5"
            :class="getGenderColor(slot.gender_category ?? '')"
          />
          {{ getGenderText(slot.gender_category ?? '') }}
        </div>
        <div>
          <div class="text-sm text-gray-700 text-right">
            {{ slot.occupied_spots }}/{{ slot.total_spots }}
          </div>
          <div class="w-20 bg-gray-100 rounded-full h-1.5 mt-1">
            <div
              class="h-1.5 rounded-full"
              :class="getStatusColor(calculateFillPercentage(slot.occupied_spots, slot.total_spots))"
              :style="{ width: calculateFillPercentage(slot.occupied_spots, slot.total_spots) + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <div class="flex justify-between items-center border-t border-gray-100 pt-2">
        <span
          v-if="slot.is_locked"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
        >
          <Lock class="h-3 w-3 mr-1" />
          Bloccato
        </span>
        <span
          v-else
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
        >
          <CheckCircle2 class="h-3 w-3 mr-1" />
          Aperto
        </span>
      </div>
      
      <!-- Admin actions and details link -->
      <div class="flex justify-between items-center border-t border-gray-100 pt-2">
        <RouterLink
          :to="'/slot/' + slot.id"
          class="flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-700"
        >
          Dettagli
          <ChevronRight class="h-4 w-4 ml-1" />
        </RouterLink>
        
        <div v-if="auth.isAdmin" class="flex space-x-3">
          <button
            class="flex items-center justify-center rounded-md bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 hover:bg-indigo-100"
            @click="$emit('edit', slot)"
            aria-label="Modifica slot"
          >
            <Edit class="h-3.5 w-3.5 mr-1" />
            Modifica
          </button>
          <button
            class="flex items-center justify-center rounded-md bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700 hover:bg-red-100"
            @click="$emit('delete', slot.id)"
            aria-label="Elimina slot"
          >
            <Trash2 class="h-3.5 w-3.5 mr-1" />
            Elimina
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Edit, Trash2, Lock, CheckCircle2, Users, User, UserSquare2, ChevronRight } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'
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
  return gender
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

<style scoped>
</style>