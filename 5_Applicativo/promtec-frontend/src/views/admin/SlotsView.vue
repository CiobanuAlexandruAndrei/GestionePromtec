<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Top Navigation -->
    <header class="bg-white shadow-sm z-10">
      <div class="flex items-center justify-between h-16 px-6">
        <h1 class="text-xl font-semibold text-gray-800">Gestione Slot</h1>
        <button
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          @click="isCreateModalOpen = true"
        >
          <Plus class="h-4 w-4 mr-2" />
          Crea
        </button>
      </div>
    </header>

    <SlotFilters
      v-model:filterSection="filterDepartment"
      v-model:filterDate="filterDate"
      v-model:view="view"
      :uniqueSections="uniqueDepartments"
      :uniqueDates="uniqueDates"
    />

    <!-- Main Content Area -->
    <main class="flex-1 overflow-y-auto bg-gray-50 p-6">
      <div v-if="filteredSlots.length === 0" class="flex flex-col items-center justify-center h-full text-center p-6">
        <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <Calendar class="h-8 w-8 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-1">Nessuno slot trovato</h3>
        <p class="text-gray-500 max-w-md">
          Non ci sono slot che corrispondono ai criteri di ricerca. Prova a modificare i filtri o crea un nuovo slot.
        </p>
        <button
          class="mt-6 inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          @click="isCreateModalOpen = true"
        >
          <Plus class="h-4 w-4 mr-2" />
          Crea Nuovo Slot
        </button>
      </div>
      
      <template v-else>
        <SlotGrid
          v-if="view === 'grid'"
          :slots="filteredSlots"
          @edit="handleEdit"
          @delete="handleDelete"
        />
        <SlotTable
          v-else
          :slots="filteredSlots"
          @edit="handleEdit"
          @delete="handleDelete"
        />

        <!-- Improved Pagination - Only show when multiple pages exist -->
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
                      @click="handlePageClick(pageNum)"
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

    <CreateSlotModal
      v-if="isCreateModalOpen"
      ref="createModalRef"
      :enums="slotEnums"
      :available-dates="availableDates"
      @close="isCreateModalOpen = false"
      @create="handleCreate"
    />

    <EditSlotModal
      v-if="isEditModalOpen && selectedSlot"
      :slot="selectedSlot"
      :enums="slotEnums"
      @close="closeEditModal"
      @save="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Calendar, Plus } from 'lucide-vue-next'
import { useUserPreferencesStore } from '../../stores/userPreferences'
import SlotFilters from '../../components/slots/SlotFilters.vue'
import SlotGrid from '../../components/slots/SlotGrid.vue'
import SlotTable from '../../components/slots/SlotTable.vue'
import CreateSlotModal from '../../components/slots/CreateSlotModal.vue'
import EditSlotModal from '../../components/slots/EditSlotModal.vue'
import { getSlots, createSlot, updateSlot, deleteSlot, getSlotEnums, getAvailableDates } from '../../services/api'
import type { Slot, CreateSlotRequest } from '../../types/slot'
import { GenderCategory } from '../../types/slot'

// Components and store setup
const userPreferences = useUserPreferencesStore()
const slots = ref<Slot[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const filterDepartment = ref('')
const filterDate = ref('')
const view = computed({
  get: () => userPreferences.viewMode,
  set: (value: 'grid' | 'list') => userPreferences.setViewMode(value)
})
const isCreateModalOpen = ref(false)
const isEditModalOpen = ref(false)
const selectedSlot = ref<Slot | null>(null)
const page = ref(1)
const itemsPerPage = ref(10)
const slotEnums = ref<{
  departments: string[]
  gender_categories: string[]
  time_periods: string[]
} | null>(null)
const availableDates = ref<string[]>([])
const createModalRef = ref<{ setError: (message: string) => void } | null>(null)

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
        department: filterDepartment.value || undefined,
        date: filterDate.value || undefined
      }
    )
    // Map the response to include occupied_spots and convert gender_category to enum
    slots.value = response.slots.map(slot => ({
      ...slot,
      gender_category: slot.gender_category as GenderCategory,
      occupied_spots: (slot as any).occupied_spots ?? 0,
      is_confirmed: (slot as any).is_confirmed ?? false
    }))
    totalItems.value = response.total
    totalPages.value = response.pages
  } catch (err) {
    console.error('Failed to fetch slots:', err)
    error.value = 'Failed to load slots. Please try again.'
  } finally {
    loading.value = false
  }
}

// Fetch enums and available dates from API
const fetchEnums = async () => {
  try {
    const enumsResponse = await getSlotEnums()
    slotEnums.value = enumsResponse
  } catch (err) {
    console.error('Failed to fetch enums:', err)
    error.value = 'Failed to load form options. Please try again.'
  }
}

// Computed properties
const uniqueDepartments = computed(() => 
  Array.from(new Set(slots.value.map((slot: Slot) => slot.department)))
)
const uniqueDates = computed(() => availableDates.value)

const totalItems = ref(0)
const totalPages = ref(0)

const displayedPages = computed(() => {
  const range = 2 // Number of pages to show on each side of current page
  const pages: (number | string)[] = []

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

const filteredSlots = computed(() => {
  return slots.value.filter((slot: Slot) => {
    const matchesDepartment = filterDepartment.value === '' || slot.department === filterDepartment.value
    const matchesDate = filterDate.value === '' || slot.date === filterDate.value

    return matchesDepartment && matchesDate
  })
})

// Event handlers
const handleEdit = (slot: Slot) => {
  selectedSlot.value = slot
  isEditModalOpen.value = true
}

const handleDelete = async (id: number) => {
  if (window.confirm('Sei sicuro di voler eliminare questo slot?')) {
    try {
      await deleteSlot(id)
      await fetchSlots() // Refresh the list
    } catch (err) {
      console.error('Failed to delete slot:', err)
      error.value = 'Failed to delete slot. Please try again.'
    }
  }
}

const handleCreate = async (slotData: CreateSlotRequest) => {
  try {
    await createSlot(slotData)
    await fetchSlots() // Refresh the list
    isCreateModalOpen.value = false
  } catch (err: any) {
    console.error('Failed to create slot:', err)
    // Extract the error message from the API response and pass it to the modal
    const errorMessage = err.response?.data?.error || err.message || 'Si è verificato un errore durante la creazione dello slot'
    createModalRef.value?.setError(errorMessage)
  }
}

const handleSave = async (updatedSlot: Slot) => {
  try {
    const updateData: CreateSlotRequest = {
      date: updatedSlot.date,
      time_period: updatedSlot.time_period,
      department: updatedSlot.department,
      gender_category: updatedSlot.gender_category,
      notes: updatedSlot.notes || undefined,
      total_spots: updatedSlot.total_spots,
      max_students_per_school: updatedSlot.max_students_per_school,
      is_locked: updatedSlot.is_locked
    }
    await updateSlot(updatedSlot.id, updateData)
    await fetchSlots() // Refresh the list
    closeEditModal()
  } catch (err) {
    console.error('Failed to update slot:', err)
    error.value = 'Failed to update slot. Please try again.'
  }
}

const closeEditModal = () => {
  isEditModalOpen.value = false
  selectedSlot.value = null
}

// Update page number handling in pagination
const handlePageClick = (pageNum: string | number) => {
  if (typeof pageNum === 'number') {
    page.value = pageNum
  }
}

// Watch for filter changes
watch([filterDate, filterDepartment], () => {
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