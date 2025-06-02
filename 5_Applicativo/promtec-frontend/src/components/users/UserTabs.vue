<script setup lang="ts">
import { Users, Clock } from 'lucide-vue-next'

interface Props {
  activeTab: 'all' | 'pending'
  totalUsers: number
  pendingUsersCount: number
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:activeTab', value: 'all' | 'pending'): void
}>()
</script>

<template>
  <div class="flex border-b border-gray-200 mb-6">
    <button
      class="px-4 py-2 text-sm font-medium relative"
      :class="activeTab === 'all' 
        ? 'text-indigo-600 border-b-2 border-indigo-600' 
        : 'text-gray-500 hover:text-gray-700'"
      @click="emit('update:activeTab', 'all')"
    >
      <div class="flex items-center">
        <Users class="h-4 w-4 mr-2" />
        Tutti gli utenti ({{ totalUsers }})
      </div>
    </button>
    <button
      class="px-4 py-2 text-sm font-medium relative"
      :class="activeTab === 'pending' 
        ? 'text-indigo-600 border-b-2 border-indigo-600' 
        : 'text-gray-500 hover:text-gray-700'"
      @click="emit('update:activeTab', 'pending')"
    >
      <div class="flex items-center">
        <Clock class="h-4 w-4 mr-2" />
        Da approvare
        <span v-if="pendingUsersCount > 0"
          class="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
        >
          {{ pendingUsersCount }}
        </span>
      </div>
    </button>
  </div>
</template>