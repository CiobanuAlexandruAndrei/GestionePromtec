<script setup lang="ts">
import { Edit, Trash2, ChevronDown, UserCog } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

interface User {
  id: number
  name: string
  email: string
  phone: string
  school: string
  role: 'admin' | 'user'
  status: 'active' | 'inactive'
  lastLogin: string
}

interface Props {
  users: User[]
  sortField: string | null
  sortDirection: 'asc' | 'desc'
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'edit', id: number): void
  (e: 'delete', id: number): void
  (e: 'sort', field: string): void
}>()

const handleSort = (field: string) => {
  // Map frontend field names to backend field names
  const fieldMap: { [key: string]: string } = {
    nome: 'first_name',
    email: 'email',
    scuola: 'school_name',
    'ultimo-accesso': 'last_login'
  }
  emit('sort', fieldMap[field] || field)
}

const getStatusBadgeColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-emerald-50 text-emerald-700 border border-emerald-200'
    case 'inactive':
      return 'bg-amber-50 text-amber-700 border border-amber-200'
    default:
      return 'bg-gray-100 text-gray-800 border border-gray-200'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'active':
      return 'Attivo'
    case 'inactive':
      return 'Inattivo'
    default:
      return status
  }
}

const getRoleBadgeColor = (role: string) => {
  switch (role) {
    case 'admin':
      return 'bg-amber-50 text-amber-700 border border-amber-200'
    case 'user':
      return 'bg-indigo-50 text-indigo-600 border border-indigo-200'
    default:
      return 'bg-gray-100 text-gray-800 border border-gray-200'
  }
}

const getRoleText = (role: string) => {
  switch (role) {
    case 'admin':
      return 'Amministratore'
    case 'user':
      return 'Utente'
    default:
      return role
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('it-IT', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Get current logged in user for comparison
const authStore = useAuthStore()

// Check if user is trying to delete their own account
const isSelfDelete = (userEmail: string) => {
  if (!authStore.user) return false
  
  // Compare by email since id may not be present in localStorage
  return authStore.user.email === userEmail
}
</script>

<template>
  <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer group"
              @click="handleSort('nome')"
            >
              <div class="flex items-center">
                <span>Nome</span>
                <ChevronDown 
                  v-if="sortField === 'first_name'"
                  class="ml-1 h-4 w-4 transition-transform"
                  :class="{ 'rotate-180': sortDirection === 'desc' }"
                />
              </div>
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer group"
              @click="handleSort('email')"
            >
              <div class="flex items-center">
                <span>Email</span>
                <ChevronDown 
                  v-if="sortField === 'email'"
                  class="ml-1 h-4 w-4 transition-transform"
                  :class="{ 'rotate-180': sortDirection === 'desc' }"
                />
              </div>
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer group"
              @click="handleSort('scuola')"
            >
              <div class="flex items-center">
                <span>Scuola</span>
                <ChevronDown 
                  v-if="sortField === 'school_name'"
                  class="ml-1 h-4 w-4 transition-transform"
                  :class="{ 'rotate-180': sortDirection === 'desc' }"
                />
              </div>
            </th>
            <th
              scope="col"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              Stato
            </th>
            
            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Azioni
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in users" :key="user.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center space-x-2">
                <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
                <div v-if="user.role === 'admin'" class="bg-amber-100 p-1 rounded-md">
                  <UserCog class="h-4 w-4 text-amber-600" />
                </div>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ user.email }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">{{ user.school }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStatusBadgeColor(user.status)"
              >
                {{ getStatusText(user.status) }}
              </span>
            </td>
            
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button 
                @click="emit('edit', user.id)"
                class="text-indigo-600 hover:text-indigo-900 mr-3"
                title="Modifica"
              >
                <Edit class="h-4 w-4" />
              </button>
              
              
              <button 
                @click="emit('delete', user.id)"
                class="text-red-600 hover:text-red-900"
                :class="{ 'opacity-50 cursor-not-allowed': isSelfDelete(user.email) }"
                :disabled="isSelfDelete(user.email)"
                :title="isSelfDelete(user.email) ? 'Non puoi eliminare il tuo account' : 'Elimina'"
              >
                <Trash2 class="h-4 w-4" />
              </button>
              
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>