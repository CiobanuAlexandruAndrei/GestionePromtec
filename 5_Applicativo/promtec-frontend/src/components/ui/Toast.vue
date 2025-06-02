<template>
  <Transition
    enter-active-class="transform ease-out duration-300 transition"
    enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
    enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="show"
      class="fixed inset-x-0 top-4 z-50 flex items-center justify-center px-4 sm:px-6"
    >
      <div
        class="max-w-sm w-full shadow-lg rounded-lg pointer-events-auto overflow-hidden"
        :class="[
          type === 'success' ? 'bg-green-50 ring-1 ring-green-200' : 
          type === 'error' ? 'bg-red-50 ring-1 ring-red-200' : 
          'bg-blue-50 ring-1 ring-blue-200'
        ]"
      >
        <div class="p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <CheckCircle 
                v-if="type === 'success'" 
                class="h-5 w-5 text-green-500" 
              />
              <AlertCircle 
                v-else-if="type === 'error'" 
                class="h-5 w-5 text-red-500" 
              />
              <InfoIcon 
                v-else 
                class="h-5 w-5 text-blue-500" 
              />
            </div>
            <div class="ml-3 w-0 flex-1 pt-0.5">
              <p 
                class="text-sm font-medium"
                :class="[
                  type === 'success' ? 'text-green-800' : 
                  type === 'error' ? 'text-red-800' : 
                  'text-blue-800'
                ]"
              >
                {{ title }}
              </p>
              <p 
                v-if="message" 
                class="mt-1 text-sm"
                :class="[
                  type === 'success' ? 'text-green-700' : 
                  type === 'error' ? 'text-red-700' : 
                  'text-blue-700'
                ]"
              >
                {{ message }}
              </p>
            </div>
            <div class="ml-4 flex-shrink-0 flex">
              <button
                @click="$emit('close')"
                class="inline-flex rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <span class="sr-only">Close</span>
                <X class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { CheckCircle, AlertCircle, X, Info as InfoIcon } from 'lucide-vue-next'

defineProps<{
  show: boolean
  title: string
  message?: string
  type: 'success' | 'error' | 'info'
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>
