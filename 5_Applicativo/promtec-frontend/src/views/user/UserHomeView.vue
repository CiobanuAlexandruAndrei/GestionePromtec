<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50">
    <!-- Top Navigation -->
    <header class="bg-white shadow-sm z-10 mt-8">
      <div class="flex items-center h-16 px-6">
        <h1 class="text-xl font-semibold text-gray-800">Slot Disponibili</h1>
      </div>
    </header>

    <SlotFilters
      v-model:filterSection="filterSection"
      v-model:filterDate="filterDate"
      v-model:view="view"
      :uniqueSections="uniqueSections"
      :uniqueDates="uniqueDates"
    />

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto my-8">
      <div v-if="loading" class="flex justify-center items-center h-full">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>

      <div v-else-if="error" class="flex flex-col items-center justify-center h-full text-center p-6">
        <div class="bg-red-50 text-red-600 p-4 rounded-lg max-w-md">
          {{ error }}
        </div>
      </div>

      <div v-else-if="filteredSlots.length === 0" class="flex flex-col items-center justify-center h-full text-center p-6">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <Calendar class="h-8 w-8 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-1">Nessuno slot trovato</h3>
      </div>
      
      <template v-else>
        <SlotGrid
          v-if="view === 'grid'"
          :slots="filteredSlots"
        />
        <SlotTable
          v-else
          :slots="filteredSlots"
        />

        <!-- Improved Pagination -->
        <div v-if="totalPages > 1" class="mt-6">
          <div class="bg-white px-6 py-4 flex items-center justify-between border border-gray-200 rounded-lg shadow-sm">
            <div class="flex-1 flex justify-between items-center">
              <p class="text-sm text-gray-700">
                Visualizzando
                <span class="font-medium">{{ (page - 1) * itemsPerPage + 1 }}</span>
                -
                <span class="font-medium">
                  {{ Math.min(page * itemsPerPage, totalItems) }}
                </span>
                di
                <span class="font-medium">{{ totalItems }}</span>
                risultati
              </p>
              
              <div class="flex items-center space-x-2">
                <button
                  @click="page > 1 && (page--)"
                  :disabled="page <= 1"
                  class="relative inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                  :class="page <= 1 
                    ? 'text-gray-400 bg-gray-50 cursor-not-allowed' 
                    : 'text-gray-700 bg-white hover:bg-gray-50 border border-gray-300'"
                >
                  Precedente
                </button>
                
                <div class="flex items-center space-x-1">
                  <template v-for="pageNum in displayedPages" :key="pageNum">
                    <span 
                      v-if="pageNum === '...'" 
                      class="px-3 py-2 text-sm text-gray-500"
                    >
                      ...
                    </span>
                    <button
                      v-else
                      @click="page = Number(pageNum)"
                      class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors"
                      :class="pageNum === page
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-700 hover:bg-gray-50 border border-gray-300'"
                    >
                      {{ pageNum }}
                    </button>
                  </template>
                </div>

                <button
                  @click="page < totalPages && (page++)"
                  :disabled="page >= totalPages"
                  class="relative inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                  :class="page >= totalPages
                    ? 'text-gray-400 bg-gray-50 cursor-not-allowed'
                    : 'text-gray-700 bg-white hover:bg-gray-50 border border-gray-300'"
                >
                  Successivo
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Calendar } from 'lucide-vue-next'
import { useUserPreferencesStore } from '../../stores/userPreferences'
import SlotFilters from '../../components/slots/SlotFilters.vue'
import SlotGrid from '../../components/slots/SlotGrid.vue'
import SlotTable from '../../components/slots/SlotTable.vue'
import { getSlots, getSlotEnums, getAvailableDates } from '../../services/api'
import type { Slot, SlotEnums } from '../../types/slot'
import { GenderCategory } from '../../types/slot'

const userPreferences = useUserPreferencesStore()
const slots = ref<Slot[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const filterSection = ref('')
const filterDate = ref('')
const page = ref(1)
const itemsPerPage = ref(10)
const slotEnums = ref<SlotEnums | null>(null)
const availableDates = ref<string[]>([])
const totalItems = ref(0)
const totalPages = ref(0)

const view = computed({
  get: () => userPreferences.viewMode,
  set: (value: 'grid' | 'list') => userPreferences.setViewMode(value)
})

// Add displayedPages computed property
const displayedPages = computed(() => {
  const range = 2 // Number of pages to show on each side of current page
  const pages = []

  // Always show first page
  pages.push(1)

  // Calculate range around current page
  let start = Math.max(2, page.value - range)
  let end = Math.min(totalPages.value - 1, page.value + range)

  // Add ellipsis after first page if needed
  if (start > 2) {
    pages.push('...')
  }

  // Add pages in range
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  // Add ellipsis before last page if needed
  if (end < totalPages.value - 1) {
    pages.push('...')
  }

  // Always show last page if there is more than one page
  if (totalPages.value > 1) {
    pages.push(totalPages.value)
  }

  return pages
})

// Fetch slots from API
const fetchSlots = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await getSlots(
      page.value,
      itemsPerPage.value,
      undefined,
      undefined,
      {
        department: filterSection.value || undefined,
        date: filterDate.value || undefined
      }
    )
    slots.value = response.slots.map(slot => ({
      ...slot,
      gender_category: slot.gender_category as GenderCategory,
      is_confirmed: (slot as any).is_confirmed ?? true,
      occupied_spots: (slot as any).occupied_spots ?? 0
    }))
    totalItems.value = response.total
    totalPages.value = response.pages
  } catch (err) {
    console.error('Failed to fetch slots:', err)
    error.value = 'Si è verificato un errore durante il caricamento degli slot. Riprova più tardi.'
  } finally {
    loading.value = false
  }
}

// Fetch enums from API
const fetchEnums = async () => {
  try {
    const enumsResponse = await getSlotEnums()
    slotEnums.value = enumsResponse
  } catch (err) {
    console.error('Failed to fetch enums:', err)
    error.value = 'Si è verificato un errore durante il caricamento delle opzioni. Riprova più tardi.'
  }
}

const uniqueSections = computed(() => 
  Array.from(new Set(slots.value.map((slot: Slot) => slot.department)))
)

const uniqueDates = computed(() => availableDates.value)

const filteredSlots = computed(() => {
  return slots.value.filter((slot: Slot) => {
    const matchesSection = filterSection.value === '' || slot.department === filterSection.value
    const matchesDate = filterDate.value === '' || slot.date === filterDate.value
    return matchesSection && matchesDate
  })
})

// Watch for filter changes
watch([filterDate, filterSection], () => {
  page.value = 1 // Reset to first page when filters change
  fetchSlots()
})

// Watch for page changes
watch(page, () => {
  fetchSlots()
})

onMounted(async () => {
  await Promise.all([
    fetchSlots(),
    fetchEnums()
  ])
})


</script>