<script setup lang="ts">
import { Search, Filter, X } from 'lucide-vue-next'
import { computed } from 'vue'

interface Props {
  schools: string[]
  roles: string[]
  statuses: string[]
  searchTerm: string
  selectedSchool: string | null
  selectedRole: string | null
  selectedStatus: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:searchTerm', value: string): void
  (e: 'update:selectedSchool', value: string | null): void
  (e: 'update:selectedRole', value: string | null): void
  (e: 'update:selectedStatus', value: string | null): void
  (e: 'resetFilters'): void
}>()

const hasActiveFilters = computed(() => {
  return props.selectedSchool !== null || 
         props.selectedRole !== null || 
         props.selectedStatus !== null
})

const activeFiltersCount = computed(() => {
  return (props.selectedSchool ? 1 : 0) + 
         (props.selectedRole ? 1 : 0) + 
         (props.selectedStatus ? 1 : 0)
})
</script>

<template>
  <div class="mb-6">
    <div class="flex flex-col md:flex-row md:items-center gap-4">
      <!-- Search Box -->
      <div class="relative flex-1">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search class="h-4 w-4 text-gray-400" />
        </div>
        <input
          type="text"
          :value="searchTerm"
          @input="emit('update:searchTerm', ($event.target as HTMLInputElement).value)"
          placeholder="Cerca per nome, email o scuola..."
          class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm placeholder-gray-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <!-- Filter Button -->
      <button
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        @click="($refs.filterPanel as HTMLElement).classList.toggle('hidden')"
      >
        <Filter class="h-4 w-4 mr-2" />
        Filtri
        <span
          v-if="activeFiltersCount > 0"
          class="ml-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 text-xs font-medium text-indigo-700"
        >
          {{ activeFiltersCount }}
        </span>
      </button>
    </div>

    <!-- Filter Panel -->
    <div ref="filterPanel" class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200 hidden">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- School Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Scuola
          </label>
          <select
            :value="selectedSchool"
            @change="emit('update:selectedSchool', ($event.target as HTMLSelectElement).value || null)"
            class="w-full px-3 py-2 border border-gray-300 bg-white rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          >
            <option value="">Tutte le scuole</option>
            <option v-for="school in schools" :key="school" :value="school">
              {{ school }}
            </option>
          </select>
        </div>

        <!-- Role Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Ruolo
          </label>
          <select
            :value="selectedRole"
            @change="emit('update:selectedRole', ($event.target as HTMLSelectElement).value || null)"
            class="w-full px-3 py-2 border border-gray-300 bg-white rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          >
            <option value="">Tutti i ruoli</option>
            <option v-for="role in roles" :key="role" :value="role">
              {{ role === 'admin' ? 'Amministratore' : 'Utente' }}
            </option>
          </select>
        </div>

        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Stato
          </label>
          <select
            :value="selectedStatus"
            @change="emit('update:selectedStatus', ($event.target as HTMLSelectElement).value || null)"
            class="w-full px-3 py-2 border border-gray-300 bg-white rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          >
            <option value="">Tutti gli stati</option>
            <option v-for="status in statuses" :key="status" :value="status">
              {{ status === 'active' ? 'Attivo' : 'Inattivo' }}
            </option>
          </select>
        </div>
      </div>

      <!-- Reset Filters Button -->
      <button
        v-if="hasActiveFilters"
        class="mt-4 inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50"
        @click="emit('resetFilters')"
      >
        <X class="h-4 w-4 mr-2" />
        Reset filtri
      </button>
    </div>
  </div>
</template>