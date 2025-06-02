`<template>
  <div class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex min-h-screen items-center justify-center px-4 py-6 sm:p-0">
      <div 
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
        @click="canClose && $emit('close')" 
      />

      <div class="relative w-full max-w-2xl transform overflow-hidden rounded-lg bg-white shadow-xl transition-all">
        <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
          <button
            v-if="canClose"
            type="button"
            class="rounded-md bg-white text-gray-400 hover:text-gray-500"
            @click="$emit('close')"
          >
            <span class="sr-only">Chiudi</span>
            <X class="h-6 w-6" />
          </button>
        </div>

        <div class="bg-white px-4 py-5 sm:p-6">
          <div class="mb-4">
            <h3 class="text-lg font-medium leading-6 text-gray-900">{{ title }}</h3>
          </div>
          
          <slot></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'

defineProps<{
  title?: string
  canClose?: boolean
}>()

defineEmits<{
  close: []
}>()
</script>`