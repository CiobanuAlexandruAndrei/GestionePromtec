<script setup lang="ts">
import { CheckCircle, XCircle, ChevronDown } from 'lucide-vue-next'

interface PendingUser {
  id: number
  name: string
  email: string
  phone: string
  school: string
  requestedAt: string
}

interface Props {
  users: PendingUser[]
  sortField: string | null
  sortDirection: 'asc' | 'desc'
  error?: string | null
  loading?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'approve', id: number): void
  (e: 'reject', id: number): void
  (e: 'sort', field: string): void
}>()

const handleSort = (field: string) => {
  // Map frontend field names to backend field names
  const fieldMap: { [key: string]: string } = {
    nome: 'first_name',
    email: 'email',
    scuola: 'school_name',
    'data-richiesta': 'created_at'
  }
  emit('sort', fieldMap[field] || field)
}

const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  
  try {
    // Ensure the date string is in ISO format
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '-'

    // Format date in Italian locale
    return new Intl.DateTimeFormat('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(date)
  } catch (e) {
    console.error('Error formatting date:', e)
    return '-'
  }
}
</script>

<template>
  <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
    <!-- Error State -->
    <div v-if="error" class="p-4 bg-red-50 border-b border-red-200">
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-8 text-center">
      <p class="text-sm text-slate-600">Caricamento utenti in corso...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!users.length" class="p-8 text-center">
      <p class="text-sm text-slate-600">Nessun utente in attesa di approvazione</p>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              @click="handleSort('first_name')"
            >
              <div class="flex items-center">
                <span>Nome</span>
                <ChevronDown
                  v-if="sortField === 'first_name'"
                  class="ml-1 h-4 w-4"
                  :class="{ 'transform rotate-180': sortDirection === 'desc' }"
                />
              </div>
            </th>
            <th
              scope="col" 
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              @click="handleSort('email')"
            >
              <div class="flex items-center">
                <span>Email</span>
                <ChevronDown
                  v-if="sortField === 'email'"
                  class="ml-1 h-4 w-4"
                  :class="{ 'transform rotate-180': sortDirection === 'desc' }"
                />
              </div>
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              @click="handleSort('school_name')"
            >
              <div class="flex items-center">
                <span>Scuola</span>
                <ChevronDown
                  v-if="sortField === 'school_name'"
                  class="ml-1 h-4 w-4"
                  :class="{ 'transform rotate-180': sortDirection === 'desc' }"
                />
              </div>
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
              @click="handleSort('created_at')"
            >
              <div class="flex items-center">
                <span>Data richiesta</span>
                <ChevronDown
                  v-if="sortField === 'created_at'"
                  class="ml-1 h-4 w-4"
                  :class="{ 'transform rotate-180': sortDirection === 'desc' }"
                />
              </div>
            </th>
            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Azioni
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in users" :key="user.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ user.email }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ user.school }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(user.requestedAt) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button 
                @click="emit('approve', user.id)"
                class="text-emerald-600 hover:text-emerald-900 mr-3"
                title="Approva"
              >
                <CheckCircle class="h-4 w-4" />
              </button>
              <button 
                @click="emit('reject', user.id)"
                class="text-rose-600 hover:text-rose-900"
                title="Rifiuta"
              >
                <XCircle class="h-4 w-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>