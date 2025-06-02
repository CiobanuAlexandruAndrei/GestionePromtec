<template>
  <div class="bg-white border-b px-6 py-3">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
      <!-- Left side filters -->
      <div class="flex flex-wrap gap-2">
        <!-- Section Filter -->
        <div class="relative">
          <select
            :value="filterSection"
            @change="$emit('update:filterSection', ($event.target as HTMLSelectElement).value)"
            class="block w-full pl-3 pr-8 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm appearance-none bg-white"
          >
            <option value="">Tutte le sezioni</option>
            <option v-for="section in uniqueSections" :key="section" :value="section">
              {{ section }}
            </option>
          </select>
          <ChevronDown class="absolute right-3 top-2.5 h-4 w-4 text-gray-400 pointer-events-none" />
        </div>

        <!--  
        <div class="relative">
          <select
            :value="filterDate"
            @change="$emit('update:filterDate', ($event.target as HTMLSelectElement).value)"
            class="block w-full pl-3 pr-8 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm appearance-none bg-white"
          >
            <option value="">Tutte le date</option>
            <option v-for="date in uniqueDates" :key="date" :value="date">
              {{ formatShortDate(date) }}
            </option>
          </select>
          <ChevronDown class="absolute right-3 top-2.5 h-4 w-4 text-gray-400 pointer-events-none" />
        </div>
        -->
      </div>

      <!-- Right side view toggle -->
      <div class="flex rounded-md border border-gray-300 overflow-hidden">
        <button
          class="px-2 py-1.5"
          :class="view === 'grid' ? 'bg-indigo-50 text-indigo-600' : 'bg-white text-gray-500'"
          @click="$emit('update:view', 'grid')"
        >
          <LayoutGrid class="h-4 w-4" />
        </button>
        <button
          class="px-2 py-1.5"
          :class="view === 'list' ? 'bg-indigo-50 text-indigo-600' : 'bg-white text-gray-500'"
          @click="$emit('update:view', 'list')"
        >
          <List class="h-4 w-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChevronDown, LayoutGrid, List } from 'lucide-vue-next'

defineProps<{
  filterSection: string
  filterDate: string
  view: 'grid' | 'list'
  uniqueSections: string[]
  uniqueDates: string[]
}>()

defineEmits<{
  'update:filterSection': [value: string]
  'update:filterDate': [value: string]
  'update:view': [value: 'grid' | 'list']
}>()

const formatShortDate = (dateString: string) => {
  const options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('it-IT', options)
}
</script>