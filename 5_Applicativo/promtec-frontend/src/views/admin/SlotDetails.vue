<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50">

    <SlotHeader
      :slot="slot"
      :registeredCount="totalRegisteredStudents"
      :waitingCount="totalWaitingStudents"
      isAdminView
    />

    <!-- Admin Status Bar -->
    <div class="border-b bg-indigo-50">
      <div class="max-w-7xl mx-auto px-4 py-3 flex flex-col sm:flex-row gap-4">
        <div class="flex items-center">
          <span class="text-sm text-gray-500 mr-2">Stato iscrizioni:</span>
          <span 
            :class="[
              'px-2.5 py-0.5 rounded-full text-xs font-medium inline-flex items-center',
              slot?.is_confirmed ? 
                'bg-green-100 text-green-800' : 
                'bg-yellow-100 text-yellow-800'
            ]"
          >
            <component 
              :is="slot?.is_confirmed ? CheckCircle2 : Clock" 
              class="h-3.5 w-3.5 mr-1"
            />
            {{ slot?.is_confirmed ? 'Confermato' : 'In attesa di conferma' }}
          </span>
        </div>
        
        <div class="flex flex-wrap gap-2 sm:ml-auto">
          <button
            @click="confirmEnrollments"
            :disabled="slot?.is_confirmed"
            class="flex-1 sm:flex-none inline-flex items-center justify-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Check class="h-4 w-4 mr-1.5 flex-shrink-0" />
            <span class="whitespace-nowrap">Conferma iscrizioni</span>
          </button>
          
          <button
            @click="exportLetters"
            :disabled="totalRegisteredStudents === 0"
            class="flex-1 sm:flex-none inline-flex items-center justify-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Mail class="h-4 w-4 mr-1.5 flex-shrink-0" />
            <span class="whitespace-nowrap">Esporta lettere</span>
          </button>
          
          <!-- 
          <button
            @click="exportData"
            class="flex-1 sm:flex-none inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            <Download class="h-4 w-4 mr-1.5 flex-shrink-0" />
            <span class="whitespace-nowrap">Esporta dati</span>
          </button>
          -->
        </div>
      </div>
    </div>

    <main class="flex-1 overflow-y-auto">
      <div class="max-w-7xl mx-auto py-4 sm:py-6 px-3 sm:px-4">
        <div v-if="loading" class="flex justify-center items-center h-64">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>

        <div v-else-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <XCircle class="h-5 w-5 text-red-400 flex-shrink-0" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Si è verificato un errore</h3>
              <p class="text-sm text-red-700 mt-1">{{ error }}</p>
            </div>
          </div>
        </div>

        <div v-else>
          <!-- Mobile Navigation for sections -->
          <div class="block lg:hidden mb-4">
            <div class="bg-white rounded-lg shadow overflow-hidden">
              <div class="flex border-b border-gray-200">
                <button 
                  @click="activeTab = 'students'"
                  class="flex-1 py-3 px-2 text-center text-sm font-medium transition-colors"
                  :class="activeTab === 'students' ? 'text-indigo-600 border-b-2 border-indigo-500' : 'text-gray-500 hover:text-gray-700'"
                >
                  Iscritti ({{ totalRegisteredStudents }})
                </button>
                <button 
                  @click="activeTab = 'waiting'"
                  class="flex-1 py-3 px-2 text-center text-sm font-medium transition-colors"
                  :class="activeTab === 'waiting' ? 'text-indigo-600 border-b-2 border-indigo-500' : 'text-gray-500 hover:text-gray-700'"
                >
                  Lista d'attesa ({{ totalWaitingStudents }})
                </button>
                <button 
                  @click="activeTab = 'stats'"
                  class="flex-1 py-3 px-2 text-center text-sm font-medium transition-colors"
                  :class="activeTab === 'stats' ? 'text-indigo-600 border-b-2 border-indigo-500' : 'text-gray-500 hover:text-gray-700'"
                >
                  Statistiche
                </button>
              </div>
            </div>
          </div>

          <!-- Desktop Layout -->
          <div class="hidden lg:grid lg:grid-cols-3 gap-6">
            <!-- Left Column - All Students and School Stats -->
            <div class="lg:col-span-2 space-y-6">
              <!-- All Students List -->
              <AdminStudentList
                :students="registeredStudents"
                :is-locked="slot?.is_locked"
                :slot-gender-category="slot?.gender_category"
                @edit="editStudent"
                @delete="confirmDeleteStudent"
                @move="moveToWaitingList"
                @createStudent="handleCreateSubmit"
              />
              
              <!-- Schools Summary -->
              <SchoolSummaryList
                :schools="schoolSummary"
                :max-students-per-school="slot?.max_students_per_school || 0"
              />
              
              <!-- Gender Distribution Card -->
              <div class="bg-white shadow rounded-lg overflow-hidden">
                <div class="px-4 py-5 sm:p-6">
                  <h3 class="text-lg leading-6 font-medium text-gray-900">Distribuzione per Genere</h3>
                  <div class="mt-4 flex items-center justify-between">
                    <div class="flex items-center">
                      <div class="bg-blue-100 w-4 h-4 rounded mr-2"></div>
                      <span class="text-sm text-gray-700">Maschi: {{ maleStudentsCount }}</span>
                    </div>
                    <div class="flex items-center">
                      <div class="bg-pink-100 w-4 h-4 rounded mr-2"></div>
                      <span class="text-sm text-gray-700">Femmine: {{ femaleStudentsCount }}</span>
                    </div>
                  </div>
                  
                  <div class="mt-4 relative pt-1">
                    <div class="overflow-hidden h-6 mb-2 text-xs flex rounded bg-gray-100">
                      <div 
                        class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-300"
                        :style="{ width: malePercentage + '%' }"
                      >
                        {{ malePercentage }}%
                      </div>
                      <div 
                        class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-pink-300"
                        :style="{ width: femalePercentage + '%' }"
                      >
                        {{ femalePercentage }}%
                      </div>
                    </div>
                  </div>
                  
                  <div class="mt-4">
                    <p class="text-sm text-gray-500">
                      Totale iscritti: {{ totalRegisteredStudents }} | 
                      Rapporto M/F: {{ genderRatio }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Right Column - Waiting List -->
            <div class="lg:col-span-1">
              <!-- Waiting List By School -->
              <AdminWaitingListView
                :students="waitingList"
                :schools="uniqueSchoolsInWaitingList"
                :can-modify="!slot?.is_locked"
                :can-promote="canPromoteFromWaitingList"
                :is-admin-view="true"
                :available-slot-spots="slot ? slot.total_spots - slot.occupied_spots : 0"
                @edit="editStudent"
                @delete="confirmDeleteStudent"
                @move="moveToRegistered"
              />
            </div>
          </div>

          <!-- Mobile Layout - Tab based -->
          <div class="lg:hidden">
            <!-- Students Tab -->
            <div v-show="activeTab === 'students'" class="space-y-4">
              <AdminStudentList
                :students="registeredStudents"
                :is-locked="slot?.is_locked"
                :slot-gender-category="slot?.gender_category"
                @edit="editStudent"
                @delete="confirmDeleteStudent"
                @move="moveToWaitingList"
                @createStudent="handleCreateSubmit"
              />
            </div>
            
            <!-- Waiting List Tab -->
            <div v-show="activeTab === 'waiting'" class="space-y-4">
              <AdminWaitingListView
                :students="waitingList"
                :schools="uniqueSchoolsInWaitingList"
                :can-modify="!slot?.is_locked"
                :can-promote="canPromoteFromWaitingList"
                :is-admin-view="true"
                :available-slot-spots="slot ? slot.total_spots - slot.occupied_spots : 0"
                @edit="editStudent"
                @delete="confirmDeleteStudent"
                @move="moveToRegistered"
              />
            </div>
            
            <!-- Stats Tab -->
            <div v-show="activeTab === 'stats'" class="space-y-4">
              <!-- Schools Summary -->
              <SchoolSummaryList
                :schools="schoolSummary"
                :max-students-per-school="slot?.max_students_per_school || 0"
              />
              
              <!-- Gender Distribution Card -->
              <div class="bg-white shadow rounded-lg overflow-hidden">
                <div class="px-4 py-5">
                  <h3 class="text-lg leading-6 font-medium text-gray-900">Distribuzione per Genere</h3>
                  <div class="mt-4 flex items-center justify-between">
                    <div class="flex items-center">
                      <div class="bg-blue-100 w-4 h-4 rounded mr-2"></div>
                      <span class="text-sm text-gray-700">Maschi: {{ maleStudentsCount }}</span>
                    </div>
                    <div class="flex items-center">
                      <div class="bg-pink-100 w-4 h-4 rounded mr-2"></div>
                      <span class="text-sm text-gray-700">Femmine: {{ femaleStudentsCount }}</span>
                    </div>
                  </div>
                  
                  <div class="mt-4 relative pt-1">
                    <div class="overflow-hidden h-6 mb-2 text-xs flex rounded bg-gray-100">
                      <div 
                        class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-300"
                        :style="{ width: malePercentage + '%' }"
                      >
                        {{ malePercentage }}%
                      </div>
                      <div 
                        class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-pink-300"
                        :style="{ width: femalePercentage + '%' }"
                      >
                        {{ femalePercentage }}%
                      </div>
                    </div>
                  </div>
                  
                  <div class="mt-4">
                    <p class="text-sm text-gray-500">
                      Totale iscritti: {{ totalRegisteredStudents }}  
                    </p>
                    <p class="text-sm text-gray-500">
                      Rapporto M/F: {{ genderRatio }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Edit Student Modal -->
    <EditStudentModal
      v-if="isEditing"
      :student="form"
      :isSubmitting="isSubmitting"
      :is-admin-view="true"
      @close="cancelEdit"
      @submit="handleSubmit"
    />

    <!-- Create Student Modal -->
    <StudentRegistrationForm
      v-if="isCreating"
      :slot="slot"
      :can-register="true"
      :is-waiting-list-active="false"
      :is-submitting="isSubmitting"
      :initial-data="createForm"
      :is-editing="false"
      @submit="handleCreateSubmit"
      @cancel="isCreating = false"
    />

    <!-- Loading Modal -->
    <LoadingModal 
      v-if="isGeneratingLetters"
      :show="true"
      message="Generazione lettere in corso..."
      :hasError="!!letterGenerationError"
      :errorMessage="letterGenerationError || ''"
      @close="() => {
        isGeneratingLetters = false
        letterGenerationError = null
      }"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useNotificationStore } from '@/stores/notificationStore'
import { XCircle, Check, Mail, Download, Clock, CheckCircle2, UserPlus } from 'lucide-vue-next'
import type { Slot, Student, StudentStatus, ExtendedStudent, SchoolInfo } from '@/types/slot'
import { 
  getSlot, 
  updateStudent,
  getSlotEnrollments,
  deleteEnrollment, 
  updateEnrollmentWaitingList,
  updateSlot,
  createEnrollment,
  confirmSlot,
  type Enrollment 
} from '@/services/api'
import SlotHeader from '@/components/slots/SlotHeader.vue'
import AdminStudentList from '@/components/slots/AdminStudentList.vue'
import SchoolSummaryList from '@/components/slots/SchoolSummaryList.vue'
import AdminWaitingListView from '@/components/slots/AdminWaitingListView.vue'
import EditStudentModal from '@/components/slots/EditStudentModal.vue'
import LoadingModal from '@/components/LoadingModal.vue'
import StudentRegistrationForm from '@/components/slots/StudentRegistrationForm.vue'
import { Gender, GenderCategory } from '@/types/slot'
import { generateLettersForSlot } from '@/services/api'

interface SlotWithEnrollments extends Slot {
  registrations: Student[];
  waitingList: Student[];
  occupied_spots: number;
}

interface SchoolSummary {
  name: string;
  studentsCount: number;
  waitingCount: number;
}

const route = useRoute()
const slot = ref<SlotWithEnrollments | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const activeTab = ref('students') // For mobile tab navigation
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
  status: 'pending'
})

// New state for creating student
const isCreating = ref(false)
const createForm = ref<Partial<Student>>({
  firstName: '',
  lastName: '',
  gender: slot.value?.gender_category === GenderCategory.GIRLS ? Gender.GIRL : Gender.BOY,
  street: '',
  zipCode: '',
  city: '',
  phone: '',
  mobile: '',
  school: '',
  grade: '',
  status: 'pending'
})

// Computed properties
const totalRegisteredStudents = computed(() => registeredStudents.value.length)
const totalWaitingStudents = computed(() => waitingList.value.length)

const schoolSummary = computed(() => {
  const schoolMap = new Map<string, SchoolSummary>()
  
  // Count registered students by school
  registeredStudents.value.forEach((student: ExtendedStudent) => {
    if (!schoolMap.has(student.school)) {
      schoolMap.set(student.school, { name: student.school, studentsCount: 0, waitingCount: 0 })
    }
    const school = schoolMap.get(student.school)!
    school.studentsCount++
  })
  
  // Add waiting students count
  waitingList.value.forEach((student: ExtendedStudent) => {
    if (!schoolMap.has(student.school)) {
      schoolMap.set(student.school, { name: student.school, studentsCount: 0, waitingCount: 0 })
    }
    const school = schoolMap.get(student.school)!
    school.waitingCount++
  })
  
  // Convert map to array and sort
  return Array.from(schoolMap.values())
    .sort((a, b) => b.studentsCount - a.studentsCount || a.name.localeCompare(b.name))
})

const uniqueSchoolsInWaitingList = computed(() => {
  const schoolNames = new Set<string>()
  waitingList.value.forEach((student: ExtendedStudent) => schoolNames.add(student.school))
  return Array.from(schoolNames)
})

const canPromoteFromWaitingList = computed(() => {
  if (!slot.value) return () => false
  if (slot.value.is_locked) return () => false
  
  // Get total available spots
  const availableSpots = slot.value.total_spots - slot.value.occupied_spots
  if (availableSpots <= 0) return () => false

  // A school can't have more students than the available spots or the per-school limit
  const maxPerSchool = slot.value.max_students_per_school ?? 0
  
  return (student: ExtendedStudent) => {
    const schoolStudentsCount = registeredStudents.value.filter(
      (s: ExtendedStudent) => s.school === student.school
    ).length
    
    return schoolStudentsCount < maxPerSchool && availableSpots > 0
  }
})

// Gender distribution computations
const maleStudentsCount = computed(() => {
  return registeredStudents.value.filter(student => student.gender === Gender.BOY).length
})

const femaleStudentsCount = computed(() => {
  return registeredStudents.value.filter(student => student.gender === Gender.GIRL).length
})

const malePercentage = computed(() => {
  if (totalRegisteredStudents.value === 0) return 0
  return Math.round((maleStudentsCount.value / totalRegisteredStudents.value) * 100)
})

const femalePercentage = computed(() => {
  if (totalRegisteredStudents.value === 0) return 0
  return Math.round((femaleStudentsCount.value / totalRegisteredStudents.value) * 100)
})

const genderRatio = computed(() => {
  if (femaleStudentsCount.value === 0) return 'N/A'
  const ratio = (maleStudentsCount.value / femaleStudentsCount.value).toFixed(2)
  return ratio
})

// Helper functions
const mapAPIToStudent = (apiStudent: {
  id: number;
  first_name: string;
  last_name: string;
  school_class: string;
  school_name: string;
  gender: string;
  address: string;
  postal_code: string;
  city: string;
  landline?: string;
  mobile: string;
  created_at?: string;
}): Student => ({
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
  gender: apiStudent.gender === 'M' ? Gender.BOY : Gender.GIRL,
  status: 'confirmed',
  registrationDate: apiStudent.created_at || new Date().toISOString()
})

const mapStudentToAPI = (student: Partial<Student>) => ({
  first_name: student.firstName || '',
  last_name: student.lastName || '',
  school_class: student.grade || '',
  school_name: student.school || '',
  gender: student.gender || Gender.BOY,
  address: student.street || '',
  postal_code: student.zipCode || '',
  city: student.city || '',
  landline: student.phone,
  mobile: student.mobile || '',
})

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
  gender: e.student.gender === 'Maschio' ? Gender.BOY : Gender.GIRL,
  status,
  registrationDate: e.created_at || new Date().toISOString()
})

// Data fetching
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
      occupied_spots: slotData.occupied_spots,
      is_confirmed: slotData.is_confirmed
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

// Student management functions
const handleSubmit = async (formData: any) => {
  isSubmitting.value = true
  try {
    if (!slot.value?.id) throw new Error('Slot ID is required')

    const apiData = mapStudentToAPI(formData)

    if (isEditing.value && editingStudentId.value) {
      await updateStudent(editingStudentId.value, apiData)
      resetForm()
      await fetchSlotData()
    }
  } catch (err) {
    console.error('Failed to update student:', err)
    error.value = 'Errore nella modifica dello studente. Riprova più tardi.'
  } finally {
    isSubmitting.value = false
  }
}

const editStudent = (student: ExtendedStudent) => {
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

const deleteStudent = async (student: ExtendedStudent) => {
  try {
    await deleteEnrollment(student.enrollmentId)
    await fetchSlotData()
  } catch (err) {
    console.error('Failed to delete enrollment:', err)
    error.value = 'Errore nella cancellazione della registrazione. Riprova più tardi.'
  }
}

const confirmDeleteStudent = async (student: ExtendedStudent) => {
  if (!confirm('Sei sicuro di voler cancellare questa registrazione?')) return
  await deleteStudent(student)
}

const moveToWaitingList = async (student: ExtendedStudent) => {
  // For moving to waiting list, the only check is whether the slot is locked
  if (slot.value?.is_locked) {
    error.value = 'Impossibile modificare iscrizione in uno slot bloccato.'
    return
  }
  
  try {
    // Moving to waiting list should always be allowed if the slot is not locked
    await updateEnrollmentWaitingList(student.enrollmentId, true)
    await fetchSlotData()
    error.value = null // Clear any previous errors
  } catch (err: any) {
    console.error('Failed to move student to waiting list:', err)
    // Still handle potential errors from backend
    if (err?.response?.data?.error === 'Cannot update enrollment in locked slot') {
      error.value = 'Impossibile modificare iscrizione in uno slot bloccato.'
    } else if (err?.response?.data?.error === 'Unauthorized to update this enrollment') {
      error.value = 'Non sei autorizzato a modificare questa iscrizione.'
    } else {
      error.value = 'Errore nello spostamento dello studente. Riprova più tardi.'
    }
  }
}

const moveToRegistered = async (student: ExtendedStudent) => {
  // For admin users, we only need to check if there are available spots in total
  // For non-admin users, we need to check both total spots and per-school limit
  const availableSpots = slot.value ? (slot.value.total_spots - slot.value.occupied_spots) : 0
  
  if (availableSpots <= 0) {
    error.value = 'Non ci sono più posti disponibili in totale.'
    return
  }
  
  // For non-admin users, also check the school limit
  // We don't need this check for admins since they can bypass the school limit
  const isAdmin = true // Since this is in the admin view, we know the user is an admin
  if (!isAdmin) {
    const checkCanPromote = canPromoteFromWaitingList.value
    if (!checkCanPromote(student)) {
      error.value = 'Non ci sono posti disponibili per questa scuola.'
      return
    }
  }
  
  try {
    await updateEnrollmentWaitingList(student.enrollmentId, false)
    await fetchSlotData()
  } catch (err: any) {
    console.error('Failed to move student to registered:', err)
    if (err?.response?.data?.error === 'School capacity limit reached') {
      error.value = 'Limite di studenti per scuola raggiunto.'
    } else if (err?.response?.data?.error === 'No available spots in total') {
      error.value = 'Non ci sono più posti disponibili in totale.'
    } else {
      error.value = 'Errore nello spostamento dello studente. Riprova più tardi.'
    }
  }
}

// Admin actions
const notificationStore = useNotificationStore()

const confirmEnrollments = async () => {
  if (!slot.value?.id) return
  
  if (!confirm("Sicuro di voler confermare tutte le iscrizioni? Questo invierà le email di conferma ai responsabili delle scuole.")) {
    return
  }
  
  try {
    const response = await confirmSlot(slot.value.id)
    slot.value = {
      ...response,
      gender_category: response.gender_category as GenderCategory,
      registrations: [],
      waitingList: [],
      occupied_spots: response.occupied_spots
    }
    await fetchSlotData()
    // Show success message with schools count
    const uniqueSchools = new Set(registeredStudents.value.map(s => s.school))
    notificationStore.showNotification(
      'Iscrizioni confermate con successo!',
      `Email inviate ai responsabili di ${uniqueSchools.size} ${uniqueSchools.size === 1 ? 'scuola' : 'scuole'}.`,
      'success',
      5000
    )
  } catch (err) {
    console.error('Failed to confirm enrollments:', err)
    notificationStore.showNotification(
      'Errore nella conferma delle iscrizioni',
      'Riprova più tardi.',
      'error',
      5000
    )
  }
}

const isGeneratingLetters = ref(false)
const letterGenerationError = ref<string | null>(null)

const exportLetters = async () => {
  if (!slot.value?.id) return
  if (totalRegisteredStudents.value === 0) {
    error.value = 'Non ci sono studenti registrati per generare le lettere.'
    return
  }
  
  isGeneratingLetters.value = true
  letterGenerationError.value = null
  
  try {
    const blob = await generateLettersForSlot(slot.value.id)
    
    // Create a download link
    const url = window.URL.createObjectURL(blob)
    const downloadLink = document.createElement('a')
    downloadLink.href = url
    downloadLink.download = `lettere-slot-${slot.value.id}.pdf`
    
    // Append to body, click and remove
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)
    
    // Clean up the URL
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
      isGeneratingLetters.value = false
    }, 1000)
    
  } catch (err) {
    console.error('Failed to generate letters:', err)
    letterGenerationError.value = 'Errore nella generazione delle lettere. Riprova più tardi.'
    isGeneratingLetters.value = false
  }
}

const startCreateStudent = () => {
  if (slot.value?.is_locked) {
    error.value = 'Non puoi aggiungere studenti in uno slot bloccato.'
    return
  }
  isCreating.value = true
  createForm.value.gender = slot.value?.gender_category === GenderCategory.GIRLS ? Gender.GIRL : Gender.BOY
}

const handleCreateSubmit = async (formData: any) => {
  isSubmitting.value = true
  try {
    if (!slot.value?.id) throw new Error('Slot ID is required')
    
    const apiData = {
      first_name: formData.firstName,
      last_name: formData.lastName,
      school_class: formData.grade,
      school_name: formData.school,
      gender: formData.gender,
      address: formData.street,
      postal_code: formData.zipCode,
      city: formData.city,
      landline: formData.phone,
      mobile: formData.mobile
    }

    await createEnrollment(slot.value.id, apiData)
    isCreating.value = false
    await fetchSlotData()
  } catch (err) {
    console.error('Failed to create student:', err)
    error.value = 'Errore nella creazione dello studente. Riprova più tardi.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchSlotData()
})
</script>