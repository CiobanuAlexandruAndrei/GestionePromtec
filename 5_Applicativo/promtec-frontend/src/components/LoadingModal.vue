<template>
  <BaseModal :show="show" :canClose="hasError" @close="onClose">
    <div class="flex flex-col items-center justify-center p-6">
      <div v-if="!hasError" class="flex flex-col items-center space-y-4">
        <div class="text-indigo-600 text-xl font-semibold mb-2">
          {{ message }}
        </div>
        <div class="w-full max-w-sm bg-gray-200 rounded-full h-2.5">
          <div class="bg-indigo-600 h-2.5 rounded-full w-full animate-pulse"></div>
        </div>
      </div>
      
      <div v-else class="flex flex-col items-center space-y-4">
        <div class="text-red-600 text-xl mb-2">
          Errore
        </div>
        <p class="text-gray-700 text-center">{{ errorMessage }}</p>
        <button
          @click="onClose"
          class="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Chiudi
        </button>
      </div>
    </div>
  </BaseModal>
</template>

<script setup lang="ts">
import BaseModal from './BaseModal.vue'

defineProps<{
  show: boolean
  message: string
  hasError?: boolean
  errorMessage?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const onClose = () => {
  emit('close')
}
</script>