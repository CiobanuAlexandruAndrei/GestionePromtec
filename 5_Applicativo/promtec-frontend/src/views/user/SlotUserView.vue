<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50">
    <SlotHeader
      :slot="slot"
      :registeredCount="registeredStudents.length"
      :waitingCount="waitingList.length"
    />

    <!-- Warning/Status Messages -->
    <div v-if="registeredStudents.length > 0 || waitingList.length > 0" class="border-b bg-indigo-50/50">
      <div class="max-w-7xl mx-auto px-4 py-2.5">
        <p v-if="slot?.is_confirmed" class="text-sm text-amber-600/80 text-center font-medium">
          Questa sessione è stata confermata e non può essere modificata.
        </p>
        <p v-else-if="slot?.is_locked" class="text-sm text-amber-600/80 text-center font-medium">
          Questa sessione è bloccata perché a meno di 2 settimane dall'evento.
        </p>
        <p v-else class="text-sm text-indigo-600/80 text-center">
          2 settimane prima dell'evento le iscrizioni verranno bloccate dalla modifica.
        </p>
      </div>
    </div>

    <main class="flex-1 overflow-y-auto">
      <div class="max-w-7xl mx-auto py-6">
        <div v-if="loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>

        <div v-else-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <XCircle class="h-5 w-5 text-red-400" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Si è verificato un errore</h3>
              <p class="text-sm text-red-700 mt-1">{{ error }}</p>
            </div>
          </div>
        </div>

        <div v-else class="space-y-9">
          <!-- Registration Form (Show only when not editing) -->
          <StudentRegistrationForm
            v-if="!isEditing && !slot?.is_locked && !slot?.is_confirmed"
            :is-editing="false"
            :is-submitting="isSubmitting"
            :can-register="canRegister"
            :is-waiting-list-active="isWaitingListActive"
            :initial-data="form"
            :slot="slot"
            @submit="handleSubmit"
          />

          <!-- Lists Container -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Registered Students -->
            <StudentList
              :students="registeredStudents"
              :is-locked="slot?.is_locked || slot?.is_confirmed"
              :slot-date="slot?.date"
              @edit="editStudent"
              @delete="(student) => deleteStudent(student)"
              @move="(student) => moveToWaitingList(student)"
            />

            <!-- Waiting List -->
            <WaitingListView
              :students="waitingList"
              :can-modify="canRegister"
              :is-locked="slot?.is_locked || slot?.is_confirmed"
              :can-promote-from-waiting-list="canPromoteFromWaitingList"
              @move="(student) => moveToRegistered(student)"
              @edit="editStudent"
              @delete="(student) => deleteStudent(student)"
            />
          </div>
        </div>
      </div>
    </main>

    <!-- Edit Student Modal -->
    <EditStudentModal
      v-if="isEditing"
      :student="form"
      :isSubmitting="isSubmitting"
      @close="cancelEdit"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { XCircle } from 'lucide-vue-next'
import type { Slot, Student, StudentStatus, ExtendedStudent } from '@/types/slot'
import { 
  getSlot, 
  createEnrollment, 
  deleteEnrollment, 
  updateEnrollmentWaitingList,
  updateStudent,
  getSlotEnrollments,
  type Enrollment 
} from '@/services/api'
import SlotHeader from '@/components/slots/SlotHeader.vue'
import StudentRegistrationForm from '@/components/slots/StudentRegistrationForm.vue'
import StudentList from '@/components/slots/StudentList.vue'
import WaitingListView from '@/components/slots/WaitingListView.vue'
import EditStudentModal from '@/components/slots/EditStudentModal.vue'
import { Gender, GenderCategory } from '@/types/slot'
import type { FormData } from '@/components/slots/StudentRegistrationForm.vue'
import { useAuthStore } from '@/stores/auth'

interface SlotWithEnrollments extends Slot {
  registrations: Student[];
  waitingList: Student[];
}

interface APIStudent {
  id: number;
  first_name: string;
  last_name: string;
  school_class: string;
  school_name: string;
  gender: string; // API returns "Maschio" or "Femmina"
  address: string;
  postal_code: string;
  city: string;
  landline?: string;
  mobile: string;
  created_at?: string;
  updated_at?: string;
}

interface CreateEnrollmentRequest {
  first_name: string;
  last_name: string;
  school_class: string;
  school_name: string;
  gender: string; // Accetta "Maschio" o "Femmina"
  address: string;
  postal_code: string;
  city: string;
  landline?: string;
  mobile: string;
  is_in_waiting_list?: boolean;
}

const route = useRoute()
const slot = ref<SlotWithEnrollments | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const isSubmitting = ref(false)
const isEditing = ref(false)
const editingStudentId = ref<number | null>(null)

const registeredStudents = ref<ExtendedStudent[]>([])
const waitingList = ref<ExtendedStudent[]>([])

const form = ref<Partial<Student>>({
  firstName: '',
  lastName: '',
  gender: Gender.BOY,
  street: '',
  zipCode: '',
  city: '',
  phone: '',
  mobile: '',
  school: '',
  grade: '',
  status: 'pending' as StudentStatus
})

const isWaitingListActive = computed(() => {
  if (!slot.value) return false
  const schoolName = form.value.school
  if (!schoolName) return false
  
  // Get count of registered students from this school (excluding those in waiting list)
  const schoolStudentsCount = registeredStudents.value.filter(
    (s: ExtendedStudent) => s.school === schoolName
  ).length
  
  // Should go to waiting list if either limit is reached
  return schoolStudentsCount >= (slot.value.max_students_per_school ?? 0) || 
         slot.value.occupied_spots >= slot.value.total_spots
})

const canRegister = computed(() => {
  if (!slot.value) return false
  if (slot.value.is_locked || slot.value.is_confirmed) return false
  // Check both total capacity and school limit
  const hasCapacity = slot.value.occupied_spots < slot.value.total_spots
  const schoolStudentsCount = registeredStudents.value.filter(
    (s: ExtendedStudent) => s.school === form.value.school
  ).length
  const hasSchoolCapacity = schoolStudentsCount < (slot.value.max_students_per_school ?? 0)
  return hasCapacity && hasSchoolCapacity
})

const canPromoteFromWaitingList = computed(() => {
  if (!slot.value) return () => false
  if (slot.value.is_locked || slot.value.is_confirmed) return () => false
  
  // First check total slot capacity - this applies to all users (including admins)
  const availableSpots = slot.value.total_spots - slot.value.occupied_spots
  if (availableSpots <= 0) return () => false
  
  // Check if current user is admin (from auth store)
  const authStore = useAuthStore()
  const isAdmin = authStore.isAdmin
  
  // For admin users, only check total available spots
  if (isAdmin) {
    return () => availableSpots > 0
  }
  
  // For non-admin users, check both total spots and school capacity
  return (student: ExtendedStudent) => {
    // Get school limit
    const schoolLimit = slot.value!.max_students_per_school ?? 0
    
    // Count current students from this school
    const schoolStudentsCount = registeredStudents.value.filter(
      (s: ExtendedStudent) => s.school === student.school
    ).length
    
    // School still has available spots if count is less than limit
    const schoolHasSpots = schoolStudentsCount < schoolLimit
    
    // Both conditions must be true: total spots available AND school has spots
    return availableSpots > 0 && schoolHasSpots
  }
})

const canMoveAny = computed(() => {
  // If slot is locked, no moves are allowed
  if (!slot.value || slot.value.is_locked) return false
  
  // Moving to waiting list is always possible if not locked
  return true
})

const mapAPIToStudent = (apiStudent: APIStudent): Student => ({
  id: apiStudent.id,
  firstName: apiStudent.first_name,
  lastName: apiStudent.last_name,
  street: apiStudent.address,
  zipCode: apiStudent.postal_code,
  city: apiStudent.city,
  phone: apiStudent.landline,
  mobile: apiStudent.mobile,
  school: apiStudent.school_name,
  grade: apiStudent.school_class,
  gender: apiStudent.gender === Gender.BOY ? Gender.BOY : Gender.GIRL,
  status: 'confirmed',
  registrationDate: apiStudent.created_at || new Date().toISOString()
})

const mapStudentToAPI = (student: Partial<Student>): CreateEnrollmentRequest => {
  // Convert Gender enum to 'Maschio' or 'Femmina' as expected by the API
  const mappedGender = student.gender === Gender.BOY ? 'Maschio' : 'Femmina'
  
  return {
    first_name: student.firstName || '',
    last_name: student.lastName || '',
    school_class: student.grade || '',
    school_name: student.school || '',
    gender: mappedGender,
    address: student.street || '',
    postal_code: student.zipCode || '',
    city: student.city || '',
    landline: student.phone,
    mobile: student.mobile || '',
  }
}

const mapEnrollmentToExtendedStudent = (e: Enrollment, status: StudentStatus): ExtendedStudent => ({
  id: e.student.id,
  enrollmentId: e.id,
  firstName: e.student.first_name,
  lastName: e.student.last_name,
  street: e.student.address,
  zipCode: e.student.postal_code,
  city: e.student.city,
  phone: e.student.landline || '',
  mobile: e.student.mobile,
  school: e.student.school_name,
  grade: e.student.school_class,
  gender: e.student.gender === 'M' ? Gender.BOY : Gender.GIRL,
  status,
  registrationDate: e.created_at || new Date().toISOString()
})

const fetchSlotData = async () => {
  loading.value = true
  error.value = null
  try {
    const slotId = parseInt(route.params.id as string)
    const [slotData, enrollmentsData] = await Promise.all([
      getSlot(slotId),
      getSlotEnrollments(slotId)
    ])
    
    slot.value = {
      ...slotData,
      gender_category: slotData.gender_category as GenderCategory,
      registrations: [],
      waitingList: [],
      occupied_spots: slotData.occupied_spots
    }
    
    registeredStudents.value = enrollmentsData
      .filter((e: Enrollment) => !e.is_in_waiting_list)
      .map(e => mapEnrollmentToExtendedStudent(e, 'confirmed'))

    waitingList.value = enrollmentsData
      .filter((e: Enrollment) => e.is_in_waiting_list)
      .map(e => mapEnrollmentToExtendedStudent(e, 'waiting'))

  } catch (err) {
    console.error('Failed to fetch slot:', err)
    error.value = 'Errore nel caricamento dei dati. Riprova più tardi.'
  } finally {
    loading.value = false
  }
}

const handleSubmit = async (formData: Partial<Student>) => {
  isSubmitting.value = true
  try {
    if (!slot.value?.id) throw new Error('Slot ID is required')

    const apiData: CreateEnrollmentRequest = {
      ...mapStudentToAPI(formData),
      is_in_waiting_list: isWaitingListActive.value
    }

    if (isEditing.value && editingStudentId.value) {
      await updateStudent(editingStudentId.value, apiData)
    } else {
      await createEnrollment(slot.value.id, apiData)
    }
    
    resetForm()
    await fetchSlotData()
  } catch (err) {
    console.error('Failed to submit form:', err)
    error.value = isEditing.value 
      ? 'Errore nella modifica dello studente. Riprova più tardi.'
      : 'Errore nella registrazione dello studente. Riprova più tardi.'
  } finally {
    isSubmitting.value = false
  }
}

const editStudent = (student: ExtendedStudent) => {
  if (slot.value?.is_locked || slot.value?.is_confirmed) return
  
  isEditing.value = true
  editingStudentId.value = student.id
  
  form.value = { ...student }
}

const cancelEdit = () => {
  isEditing.value = false
  editingStudentId.value = null
  resetForm()
}

const resetForm = () => {
  isEditing.value = false
  editingStudentId.value = null
  form.value = {
    firstName: '',
    lastName: '',
    gender: Gender.BOY,
    street: '',
    zipCode: '',
    city: '',
    phone: '',
    mobile: '',
    school: '',
    grade: '',
    status: 'pending'
  }
}

const deleteStudent = (student: ExtendedStudent) => {
  if (slot.value?.is_locked || slot.value?.is_confirmed) return
  
  if (confirm(`Sei sicuro di voler eliminare ${student.firstName} ${student.lastName}?`)) {
    isSubmitting.value = true
    deleteEnrollment(student.enrollmentId)
      .then(() => {
        fetchSlotData()
      })
      .catch((err) => {
        error.value = err.response?.data?.error || 'Errore durante l\'eliminazione dello studente'
      })
      .finally(() => {
        isSubmitting.value = false
      })
  }
}

const moveToWaitingList = (student: ExtendedStudent) => {
  // Do not allow moving if slot is locked or confirmed
  if (slot.value?.is_locked || slot.value?.is_confirmed) return
  
  if (!isEditing.value && !isSubmitting.value) {
    isSubmitting.value = true
    updateEnrollmentWaitingList(student.enrollmentId, true)
      .then(() => {
        // Remove from registered list and add to waiting list
        const updatedStudent = { ...student, status: 'waiting' as StudentStatus }
        const index = registeredStudents.value.findIndex(s => s.id === student.id)
        if (index !== -1) {
          registeredStudents.value.splice(index, 1)
          waitingList.value.push(updatedStudent)
        }
      })
      .catch((err) => {
        error.value = err.response?.data?.error || 'Errore durante lo spostamento'
      })
      .finally(() => {
        isSubmitting.value = false
        fetchSlotData() // Refresh data
      })
  }
}

const moveToRegistered = (student: ExtendedStudent) => {
  // Do not allow moving if slot is locked or confirmed
  if (slot.value?.is_locked || slot.value?.is_confirmed) return
  
  if (!isEditing.value && !isSubmitting.value) {
    const canPromote = canPromoteFromWaitingList.value(student)
    if (canPromote) {
      isSubmitting.value = true
      updateEnrollmentWaitingList(student.enrollmentId, false)
        .then(() => {
          // Remove from waiting list and add to registered
          const updatedStudent = { ...student, status: 'confirmed' as StudentStatus }
          const index = waitingList.value.findIndex(s => s.id === student.id)
          if (index !== -1) {
            waitingList.value.splice(index, 1)
            registeredStudents.value.push(updatedStudent)
          }
          
          // Update slot with new occupied spots count
          if (slot.value) {
            slot.value.occupied_spots += 1
          }
        })
        .catch((err) => {
          error.value = err.response?.data?.error || 'Errore durante lo spostamento'
        })
        .finally(() => {
          isSubmitting.value = false
          // Refresh data
          fetchSlotData()
        })
    }
  }
}

onMounted(() => {
  fetchSlotData()
})
</script>
