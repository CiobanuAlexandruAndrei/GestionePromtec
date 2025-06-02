<script setup lang="ts">
interface Props {
  currentPage: number
  totalPages: number
  totalItems: number
  itemsPerPage: number
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:currentPage', value: number): void
}>()
</script>

<template>
  <div class="bg-white px-6 py-4 flex items-center justify-between border-t border-gray-200">
    <div class="flex-1 flex justify-between items-center">
      <p class="text-sm text-gray-700">
        Visualizzando
        <span class="font-medium">{{ (currentPage - 1) * itemsPerPage + 1 }}</span>
        -
        <span class="font-medium">
          {{ Math.min(currentPage * itemsPerPage, totalItems) }}
        </span>
        di
        <span class="font-medium">{{ totalItems }}</span>
        risultati
      </p>
      
      <div class="flex items-center space-x-2">
        <button
          @click="currentPage > 1 && emit('update:currentPage', currentPage - 1)"
          :disabled="currentPage === 1"
          class="relative inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="currentPage === 1 
            ? 'text-gray-400 bg-gray-50 cursor-not-allowed' 
            : 'text-gray-700 bg-white hover:bg-gray-50 border border-gray-300'"
        >
          Precedente
        </button>
        
        <div class="flex items-center space-x-1">
          <button
            v-for="page in totalPages"
            :key="page"
            @click="emit('update:currentPage', page)"
            class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors"
            :class="page === currentPage
              ? 'bg-indigo-600 text-white'
              : 'text-gray-700 hover:bg-gray-50 border border-gray-300'"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="currentPage < totalPages && emit('update:currentPage', currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="relative inline-flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors"
          :class="currentPage === totalPages
            ? 'text-gray-400 bg-gray-50 cursor-not-allowed'
            : 'text-gray-700 bg-white hover:bg-gray-50 border border-gray-300'"
        >
          Successivo
        </button>
      </div>
    </div>
  </div>
</template>