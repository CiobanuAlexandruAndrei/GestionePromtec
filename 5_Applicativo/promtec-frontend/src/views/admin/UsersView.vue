<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'
import { getApprovedUsers, getPendingUsers, getUser, deleteUser, approveUser, getSchools } from '@/services/api'
import UserSearchFilters from '@/components/users/UserSearchFilters.vue'
import UserTabs from '@/components/users/UserTabs.vue'
import UserTable from '@/components/users/UserTable.vue'
import PendingUserTable from '@/components/users/PendingUserTable.vue'
import UserPagination from '@/components/users/UserPagination.vue'
import EditUserModal from '@/components/users/EditUserModal.vue'
import CreateUserModal from '@/components/users/CreateUserModal.vue'

interface ApiUser {
  id: number
  email: string
  first_name: string
  last_name: string
  is_admin: boolean
  is_active: boolean
  school_name: string
  created_at: string
}

interface TableUser {
  id: number
  name: string
  email: string
  phone: string
  school: string
  role: 'admin' | 'user'
  status: 'active' | 'inactive'
  lastLogin: string
}

interface PendingTableUser {
  id: number
  name: string
  email: string
  phone: string
  school: string
  requestedAt: string
}

const activeTab = ref<'all' | 'pending'>('all')
const currentPage = ref(1)
const itemsPerPage = ref(10)
const approvedTotal = ref(0)
const pendingTotal = ref(0)
const totalPages = ref(0)
const apiUsers = ref<ApiUser[]>([])
const apiPendingUsers = ref<ApiUser[]>([])
const pendingUsersCount = ref(0)
const sortField = ref<string | null>(null)
const sortDirection = ref<'asc' | 'desc'>('asc')
const searchTerm = ref('')
const selectedSchool = ref<string | null>(null)
const selectedRole = ref<string | null>(null)
const selectedStatus = ref<string | null>(null)
const selectedUser = ref<ApiUser | null>(null)
const isEditModalOpen = ref(false)
const showCreateUserModal = ref(false)
const schools = ref<string[]>([])

const mapApiUserToTableUser = (apiUser: ApiUser): TableUser => ({
  id: apiUser.id,
  name: `${apiUser.first_name} ${apiUser.last_name}`,
  email: apiUser.email,
  phone: '-', // Add this field when available from API
  school: apiUser.school_name,
  role: apiUser.is_admin ? 'admin' : 'user',
  status: apiUser.is_active ? 'active' : 'inactive',
  lastLogin: apiUser.created_at || (new Date()).toISOString() // Add this field when available from API
})

const mapApiUserToPendingUser = (apiUser: ApiUser): PendingTableUser => ({
  id: apiUser.id,
  name: `${apiUser.first_name} ${apiUser.last_name}`,
  email: apiUser.email,
  phone: '-', // Add this field when available from API
  school: apiUser.school_name,
  requestedAt: new Date().toISOString() // Add this field when available from API
})

const users = computed(() => apiUsers.value.map(mapApiUserToTableUser))
const pendingUsers = computed(() => apiPendingUsers.value.map(mapApiUserToPendingUser))

// Add a function to update totals
const updateTotals = async () => {
  try {
    const [approvedResponse, pendingResponse] = await Promise.all([
      getApprovedUsers(1, 1), // Get just one item to get total count
      getPendingUsers(1, 1)   // Get just one item to get total count
    ])
    approvedTotal.value = approvedResponse.total
    pendingTotal.value = pendingResponse.total
  } catch (error) {
    console.error('Error updating totals:', error)
  }
}

// Update the loadUsers function
const loadUsers = async () => {
  try {
    const filters = {
      school_name: selectedSchool.value || undefined,
      is_admin: selectedRole.value === 'admin' ? true : selectedRole.value === 'user' ? false : undefined,
      is_active: selectedStatus.value === 'active' ? true : selectedStatus.value === 'inactive' ? false : undefined
    }

    if (activeTab.value === 'all') {
      const response = await getApprovedUsers(
        currentPage.value, 
        itemsPerPage.value,
        sortField.value || undefined,
        sortDirection.value,
        searchTerm.value,
        filters
      )
      apiUsers.value = response.users
      approvedTotal.value = response.total
      totalPages.value = response.pages
    } else {
      const response = await getPendingUsers(
        currentPage.value, 
        itemsPerPage.value,
        sortField.value || undefined,
        sortDirection.value,
        searchTerm.value,
        { school_name: selectedSchool.value || undefined }
      )
      apiPendingUsers.value = response.users
      pendingTotal.value = response.total
      totalPages.value = response.pages
    }
    await updateTotals()
  } catch (error) {
    console.error('Error loading users:', error)
  }
}

const handleSort = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
  loadUsers()
}

const handleEdit = async (userId: number) => {
  try {
    selectedUser.value = await getUser(userId)
    isEditModalOpen.value = true
  } catch (error) {
    console.error('Failed to fetch user details:', error)
    // TODO: Show error notification
  }
}

const handleEditSave = async () => {
  // ... existing edit save logic ...
  await updateTotals()  // Update totals after successful edit
}

const handleDelete = async (userId: number) => {
  if (!confirm('Sei sicuro di voler eliminare questo utente?')) {
    return
  }
  
  try {
    await deleteUser(userId)
    await loadUsers() // This will update the totals
    // TODO: Show success notification
  } catch (error) {
    console.error('Failed to delete user:', error)
    // TODO: Show error notification
  }
}

const notificationStore = useNotificationStore()

const handleApprove = async (userId: number) => {
  try {
    await approveUser(userId, true)
    await loadUsers() // This will update the totals
    notificationStore.showNotification(
      'Utente approvato con successo',
      'L\'utente può ora accedere al sistema.',
      'success',
      5000
    )
  } catch (error) {
    console.error('Failed to approve user:', error)
    notificationStore.showNotification(
      'Errore durante l\'approvazione',
      'Si è verificato un problema. Riprova più tardi.',
      'error',
      5000
    )
  }
}

const handleReject = async (userId: number) => {
  if (!confirm('Sei sicuro di voler rifiutare questa richiesta? L\'azione è irreversibile')) {
    return
  }

  try {
    await approveUser(userId, false)
    await loadUsers()
    notificationStore.showNotification(
      'Utente rifiutato',
      'La richiesta di registrazione è stata rifiutata.',
      'info',
      5000
    )
  } catch (error) {
    console.error('Failed to reject user:', error)
    notificationStore.showNotification(
      'Errore durante il rifiuto',
      'Si è verificato un problema. Riprova più tardi.',
      'error',
      5000
    )
  }
}

const handleUpdateComplete = async () => {
  await loadUsers() // Reload the users list
  isEditModalOpen.value = false
  selectedUser.value = null
}

const updatePendingCount = async () => {
  try {
    const response = await getPendingUsers(1, 1) // Get just first page to get total
    pendingUsersCount.value = response.total
  } catch (error) {
    console.error('Failed to fetch pending users count:', error)
  }
}

// Watch for page changes
watch(currentPage, () => {
  loadUsers()
})

// Watch for tab changes
watch(activeTab, () => {
  currentPage.value = 1 // Reset to first page when changing tabs
  loadUsers()
})

// Watch for search term changes
watch(searchTerm, () => {
  currentPage.value = 1 // Reset to first page
  loadUsers()
})

// Watch for filter changes
watch([selectedSchool, selectedRole, selectedStatus], () => {
  currentPage.value = 1 // Reset to first page
  loadUsers()
})

onMounted(async () => {
  await Promise.all([
    loadUsers(),
    getSchools().then(s => schools.value = s)
  ])
})

// Auto-refresh pending count periodically
const pendingCountInterval = setInterval(updatePendingCount, 60000) // Every minute

onUnmounted(() => {
  clearInterval(pendingCountInterval)
})

const resetFilters = () => {
  searchTerm.value = ''
  selectedSchool.value = null
  selectedRole.value = null
  selectedStatus.value = null
  currentPage.value = 1
  loadUsers()
}

// Mock data for schools (replace with actual data from your API)
const roles = ['admin', 'user']
const statuses = ['active', 'inactive']

// Define user type for the creation event
interface CreatedUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

const handleUserCreated = (user: CreatedUser) => {
  showCreateUserModal.value = false
  
  // Call showNotification with the correct parameters (title, message, type)
  notificationStore.showNotification(
    'Operazione completata',
    `Utente ${user.first_name} ${user.last_name} creato con successo.`,
    'success'
  )
  
  // Reload the user list to include the new user
  loadUsers()
  updatePendingCount()
}
</script>

<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Gestione Utenti</h1>
      <button
        @click="showCreateUserModal = true"
        class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Crea nuovo utente
      </button>
    </div>

    <UserTabs
      v-model:activeTab="activeTab"
      :total-users="approvedTotal"
      :pending-users-count="pendingTotal"
    />

    <UserSearchFilters
      :schools="schools"
      :roles="roles"
      :statuses="statuses"
      v-model:search-term="searchTerm"
      v-model:selected-school="selectedSchool"
      v-model:selected-role="selectedRole"
      v-model:selected-status="selectedStatus"
      @reset-filters="resetFilters"
    />

    <template v-if="activeTab === 'all'">
      <UserTable
        :users="users"
        :sort-field="sortField"
        :sort-direction="sortDirection"
        @sort="handleSort"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </template>

    <template v-else>
      <PendingUserTable
        :users="pendingUsers"
        :sort-field="sortField"
        :sort-direction="sortDirection"
        @sort="handleSort"
        @approve="handleApprove"
        @reject="handleReject"
      />
    </template>

    <UserPagination
      v-if="totalPages > 1"
      v-model:current-page="currentPage"
      :total-pages="totalPages"
      :total-items="activeTab === 'all' ? approvedTotal : pendingTotal"
      :items-per-page="itemsPerPage"
    />

    <EditUserModal
      v-if="selectedUser"
      :user="selectedUser"
      :is-open="isEditModalOpen"
      @close="isEditModalOpen = false"
      @update="handleUpdateComplete"
    />
    
    <!-- Create User Modal -->
    <CreateUserModal 
      :show="showCreateUserModal" 
      @close="showCreateUserModal = false" 
      @user-created="handleUserCreated"
    />
  </div>
</template>