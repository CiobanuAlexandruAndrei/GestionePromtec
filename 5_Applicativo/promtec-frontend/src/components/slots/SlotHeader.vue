<template>
  <header class="bg-white shadow-sm overflow-hidden border border-gray-100">
    <div class="max-w-7xl mx-auto p-4 sm:px-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <!-- Left side: Slot info -->
        <div class="flex-shrink min-w-0">
          <!-- Department badges -->
          <div v-if="slot" class="flex flex-wrap items-center gap-2 mb-1.5">
            <span
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium"
              :class="getDepartmentColor(slot.department)"
            >
              {{ slot.department }}
            </span>
            <span
              v-if="slot.is_locked"
              class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800"
            >
              <Lock class="h-3.5 w-3.5 mr-1.5" />
              Iscrizioni bloccate
            </span>
          </div>

          <!-- Date -->
          <h1 class="text-xl font-semibold text-gray-800 mb-2">{{ formatDate(slot?.date) }}</h1>

          <!-- Period and gender info -->
          <div v-if="slot" class="flex flex-wrap items-center text-sm text-gray-500 gap-2">
            <div class="flex items-center">
              <Clock class="h-4 w-4 mr-1" />
              <span>{{ getPeriodText(slot.time_period) }}</span>
            </div>
            <span class="hidden sm:inline mx-1">•</span>
            <div class="flex items-center">
              <component
                :is="getGenderIcon(slot.gender_category)"
                class="h-4 w-4 mr-1"
                :class="getGenderColor(slot.gender_category)"
              />
              <span>{{ getGenderText(slot.gender_category) }}</span>
            </div>
          </div>
        </div>

        <!-- Right side: Stats -->
        <div class="flex flex-wrap gap-4 md:gap-8 mt-3 md:mt-0">
          <!-- Total Spots -->
          <div class="min-w-[180px] flex-1">
            <div class="flex items-center justify-between mb-1">
              <div class="flex items-center">
                <UserCheck class="h-4 w-4 text-gray-500 mr-1" />
                <span class="text-sm text-gray-500">Iscritti Totali</span>
              </div>
              <span
                class="text-sm font-medium ml-2"
                :class="slot ? getStatusTextColor(slot.occupied_spots, slot.total_spots) : ''"
              >
                {{ slot?.occupied_spots ?? 0 }}/{{ slot?.total_spots ?? 0 }}
              </span>
            </div>

            <div class="w-full bg-gray-100 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all duration-200"
                :class="slot ? getStatusColor(calculateFillPercentage(slot.occupied_spots, slot.total_spots)) : ''"
                :style="{ width: slot ? calculateFillPercentage(slot.occupied_spots, slot.total_spots) + '%' : '0%' }"
              ></div>
            </div>
          </div>

          <!-- School Spots -->
          <div class="min-w-[160px] flex-1">
            <div class="flex items-center justify-between mb-1">
              <div class="flex items-center">
                <School class="h-4 w-4 text-gray-500 mr-1" />
                <span class="text-sm text-gray-500">Per Scuola</span>
              </div>
              <span class="text-sm font-medium text-gray-900 ml-2">
                Max {{ slot?.max_students_per_school ?? 0 }}
              </span>
            </div>
            <div class="text-xs text-gray-500">
              studenti per responsabile
            </div>
          </div>
          
          
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Clock, UserCheck, Lock, Users, User, UserSquare2, School } from 'lucide-vue-next'
import { Clock as ClockIcon } from 'lucide-vue-next' // Renamed to avoid conflict with existing Clock import
import type { Slot } from '@/types/slot'

const props = defineProps<{
  slot: Slot | null
  registeredCount: number
  waitingCount: number
  isAdminView?: boolean
}>()

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
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

const getPeriodText = (period?: string): string => {
  if (!period) return ''
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

const GenderCategory = {
  MIXED: 'Misto',
  BOYS: 'Solo ragazzi',
  GIRLS: 'Solo ragazze'
}

const getGenderText = (category: string): string => {
  switch (category) {
    case GenderCategory.MIXED:
      return 'Aperto a tutti'
    case GenderCategory.BOYS:
      return 'Solo ragazzi'
    case GenderCategory.GIRLS:
      return 'Solo ragazze'
    default:
      return category
  }
}

const getGenderIcon = (category: string) => {
  switch (category) {
    case GenderCategory.MIXED:
      return Users
    case GenderCategory.BOYS:
      return User
    case GenderCategory.GIRLS:
      return UserSquare2
    default:
      return Users
  }
}

const getGenderColor = (category: string): string => {
  switch (category) {
    case GenderCategory.MIXED:
      return 'text-purple-600'
    case GenderCategory.BOYS:
      return 'text-blue-600'
    case GenderCategory.GIRLS:
      return 'text-pink-600'
    default:
      return 'text-gray-600'
  }
}

const calculateFillPercentage = (registered: number, total: number) => {
  return Math.min((registered / total) * 100, 100)
}

const getStatusColor = (percentage: number) => {
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 70) return 'bg-amber-500'
  return 'bg-emerald-500'
}

const getStatusTextColor = (registered: number, total: number) => {
  const percentage = calculateFillPercentage(registered, total)
  if (percentage >= 90) return 'text-red-600'
  if (percentage >= 70) return 'text-amber-600'
  return 'text-emerald-600'
}
</script>
