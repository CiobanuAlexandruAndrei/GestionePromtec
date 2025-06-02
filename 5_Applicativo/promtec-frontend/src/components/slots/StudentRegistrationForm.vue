<template>
  <div class="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-100">
    <div class="p-4">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-gray-800">{{ isEditing ? 'Modifica Studente' : 'Iscrivi Nuovo Studente' }}</h2>
        <button
          v-if="isEditing"
          type="button"
          class="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          @click="$emit('cancel')"
        >
          <X class="h-4 w-4 mr-1.5" />
          Annulla modifica
        </button>
      </div>

      <!-- Form Step Indicator -->
      <nav class="mb-6">
        <ol class="flex items-center">
          <li
            v-for="(step, index) in steps"
            :key="index"
            class="flex items-center"
            :class="index !== steps.length - 1 ? 'flex-1' : ''"
          >
            <div class="flex items-center relative z-10">
              <button
                type="button"
                
                :class="[
                  'flex items-center justify-center w-8 h-8 rounded-full border-2 font-semibold text-sm pointer-events-none',
                  currentStep === index 
                    ? 'border-indigo-600 bg-indigo-600 text-white'
                    : currentStep > index
                      ? 'border-indigo-600 text-indigo-600 bg-white'
                      : 'border-gray-300 text-gray-500 bg-white'
                ]"
              >
                <component 
                  :is="step.icon" 
                  v-if="currentStep > index"
                  class="h-4 w-4"
                />
                <span v-else>{{ index + 1 }}</span>
              </button>
              <div class="ml-3 whitespace-nowrap">
                <div class="text-sm font-medium">{{ step.name }}</div>
              </div>
            </div>
            <div 
              v-if="index !== steps.length - 1"
              class="w-full border-t-2 transition-colors duration-200 mx-6"
              :class="currentStep > index ? 'border-indigo-600' : 'border-gray-200'"
            />
          </li>
        </ol>
      </nav>

      <form @submit.prevent="handleSubmit" novalidate>
        <!-- Step 1: Personal Info -->
        <div v-if="currentStep === 0" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              v-model="form.firstName"
              label="Nome"
              type="text"
              :required="currentStep === 0"
              :error="errors.firstName"
              icon="User"
            />
            <FormField
              v-model="form.lastName"
              label="Cognome"
              type="text"
              :required="currentStep === 0"
              :error="errors.lastName"
              icon="User"
            />
            <!-- Gender Field -->
            <div class="relative">
              <template v-if="slot?.gender_category === GenderCategory.MIXED">
                <FormField
                  v-model="form.gender"
                  label="Sesso"
                  type="select"
                  :required="currentStep === 0"
                  :options="genderOptions"
                  :error="genderError"
                  icon="Users2"
                />
              </template>
              <template v-else>
                <div class="space-y-1">
                  <label class="block text-sm font-medium text-gray-700">Genere</label>
                  <div class="flex items-center px-3 py-2 border border-gray-200 rounded-md bg-gray-50">
                    <component 
                      :is="form.gender === Gender.BOY ? User : UserSquare2"
                      class="h-4 w-4 text-gray-400 mr-3"
                    />
                    <span class="text-sm text-gray-600">
                      {{ form.gender === Gender.BOY ? 'Maschio' : 'Femmina' }}
                    </span>
                  </div>
                  <div class="mt-1">
                    <span class="text-indigo-600 flex items-center text-sm">
                      <Info class="h-4 w-4 mr-1"/>
                      Slot riservato {{ slot?.gender_category === GenderCategory.BOYS ? 'ai ragazzi' : 'alle ragazze' }}
                    </span>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>

        <!-- Step 2: Contact Info -->
        <div v-else-if="currentStep === 1" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField
              v-model="form.street"
              label="Indirizzo"
              type="text"
              :required="currentStep === 1"
              :error="errors.street"
              icon="MapPin"
              class="md:col-span-2"
            />
            <FormField
              v-model="form.zipCode"
              label="NAP"
              type="text"
              :required="currentStep === 1"
              pattern="[0-9]{4}"
              maxlength="4"
              :error="errors.zipCode"
              icon="Hash"
            />
            <FormField
              v-model="form.city"
              label="Luogo"
              type="text"
              :required="currentStep === 1"
              :error="errors.city"
              icon="Building"
            />
            <FormField
              v-model="form.phone"
              label="Telefono Fisso"
              type="tel"
              :error="errors.phone"
              icon="Phone"
            />
            <FormField
              v-model="form.mobile"
              label="Cellulare"
              type="tel"
              :required="currentStep === 1"
              :error="errors.mobile"
              icon="Smartphone"
            />
          </div>
        </div>

        <!-- Step 3: School Info -->
        <div v-else-if="currentStep === 2" class="space-y-4">
          <div class="grid grid-cols-1 gap-4">
            <FormField
              v-model="form.grade"
              label="Classe"
              type="text"
              :required="currentStep === 2"
              :error="errors.grade"
              icon="BookOpen"
            />
          </div>
        </div>

        <!-- Navigation -->
        <div class="mt-6 flex justify-between items-center pt-4 border-t">
          <button
            type="button"
            v-if="currentStep > 0"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            @click="currentStep--"
          >
            <ChevronLeft class="h-4 w-4 mr-1.5" />
            Indietro
          </button>
          <div class="flex justify-end space-x-3">
            <button
              v-if="currentStep < steps.length - 1"
              type="button"
              :disabled="!canGoNext"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white"
              :class="[canGoNext ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-gray-400 cursor-not-allowed']"
              @click="handleStepNext"
            >
              Avanti
              <ChevronRight class="h-4 w-4 ml-1.5" />
            </button>
            <button
              v-else
              type="submit"
              :disabled="isSubmitting || !canGoNext"
              :class="[
                'inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white',
                (isSubmitting || !canGoNext) ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
              ]"
            >
              <Save v-if="isEditing" class="h-4 w-4 mr-1.5" />
              <UserPlus v-else class="h-4 w-4 mr-1.5" />
              <span v-if="isEditing">Salva Modifiche</span>
              <span v-else>{{ isWaitingListActive ? 'Metti in lista d\'attesa' : 'Registra' }}</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import {
  BookOpen,
  Building,
  ChevronLeft,
  ChevronRight,
  GraduationCap,
  Hash,
  MapPin,
  Phone,
  Save,
  Smartphone,
  User,
  UserPlus,
  Users2,
  UserSquare2,
  X,
  Info
} from 'lucide-vue-next'
import FormField from '@/components/forms/FormField.vue'
import type { Student, StudentStatus } from '@/types/slot'
import { getSchools } from '@/services/api'
import { Gender, GenderCategory, isGenderAllowed } from '@/types/slot'
import type { Slot } from '@/types/slot'

// Export the FormData interface
export interface FormData {
  firstName: string
  lastName: string
  gender: Gender // Change from string literals to Gender enum
  street: string
  zipCode: string
  city: string
  phone: string
  mobile: string
  school: string
  grade: string
  status: StudentStatus
  registrationDate: string
}

// Function declarations first
const getDefaultGender = (slotGenderCategory: GenderCategory): Gender => {
  switch (slotGenderCategory) {
    case GenderCategory.BOYS:
      return Gender.BOY
    case GenderCategory.GIRLS:
      return Gender.GIRL
    default:
      return Gender.BOY
  }
}

// Props and emits
const props = defineProps<{
  isEditing: boolean
  isSubmitting: boolean
  canRegister: boolean
  isWaitingListActive: boolean
  initialData?: Partial<Student>
  slot: Slot | null
}>()

const emit = defineEmits<{
  submit: [form: Partial<Student>]
  cancel: []
}>()

const steps = [
  { name: 'Dati Personali', icon: User },
  { name: 'Contatti', icon: Phone },
  { name: 'Scuola', icon: GraduationCap }
]

const currentStep = ref(0)
const errors = ref<Record<string, string>>({})

// Add validation computed properties
const isStep1Valid = computed(() => {
  return form.value.firstName && 
         form.value.lastName && 
         form.value.gender
})

const isStep2Valid = computed(() => {
  return form.value.street && 
         form.value.zipCode && 
         form.value.city && 
         form.value.mobile
})

const isStep3Valid = computed(() => {
  return form.value.grade
})

const canGoNext = computed(() => {
  switch (currentStep.value) {
    case 0:
      return isStep1Valid.value
    case 1:
      return isStep2Valid.value
    case 2:
      return isStep3Valid.value
    default:
      return false
  }
})

// Aggiornare logica delle opzioni del genere e selezione automatica
const genderOptions = computed(() => {
  if (!props.slot) return []
  if (props.slot.gender_category === GenderCategory.MIXED) {
    return [
      { value: Gender.BOY, label: 'Maschio' },
      { value: Gender.GIRL, label: 'Femmina' }
    ]
  } else if (props.slot.gender_category === GenderCategory.BOYS) {
    return [{ value: Gender.BOY, label: 'Maschio' }]
  } else {
    return [{ value: Gender.GIRL, label: 'Femmina' }]
  }
})

// Inizializzazione del form con il genere corretto basato sullo slot
const form = ref<FormData>({
  firstName: props.initialData?.firstName ?? '',
  lastName: props.initialData?.lastName ?? '',
  gender: !props.slot ? Gender.BOY :
          props.slot.gender_category === GenderCategory.GIRLS ? Gender.GIRL :
          props.slot.gender_category === GenderCategory.BOYS ? Gender.BOY :
          props.initialData?.gender ?? Gender.BOY,
  street: props.initialData?.street ?? '',
  zipCode: props.initialData?.zipCode ?? '',
  city: props.initialData?.city ?? '',
  phone: props.initialData?.phone ?? '',
  mobile: props.initialData?.mobile ?? '',
  school: props.initialData?.school ?? '',
  grade: props.initialData?.grade ?? '',
  status: props.initialData?.status ?? 'pending',
  registrationDate: props.initialData?.registrationDate ?? new Date().toISOString()
})

// Add genderError computed property
const genderError = computed(() => {
  if (currentStep.value === 0 && !form.value.gender) {
    return 'Il sesso è obbligatorio'
  }
  if (!isValidGender.value) {
    return 'Il genere selezionato non è consentito per questo slot'
  }
  return ''
})

// Osservare i cambiamenti della categoria dello slot per aggiornare il genere
watch(() => props.slot?.gender_category, (newCategory) => {
  if (!newCategory) return
  if (newCategory === GenderCategory.BOYS) {
    form.value.gender = Gender.BOY
  } else if (newCategory === GenderCategory.GIRLS) {
    form.value.gender = Gender.GIRL
  }
}, { immediate: true })

const schools = ref<string[]>([])
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    schools.value = await getSchools()
  } catch (err) {
    console.error('Failed to fetch schools:', err)
    error.value = 'Errore nel caricamento delle scuole. Riprova più tardi.'
  }
})

// Add validation function
const validateCurrentStep = () => {
  errors.value = {}
  
  switch (currentStep.value) {
    case 0:
      if (!form.value.firstName) errors.value.firstName = 'Il nome è obbligatorio'
      if (!form.value.lastName) errors.value.lastName = 'Il cognome è obbligatorio'
      if (!form.value.gender) errors.value.gender = 'Il sesso è obbligatorio'
      return !Object.keys(errors.value).length
    case 1:
      if (!form.value.street) errors.value.street = 'L\'indirizzo è obbligatoria'
      if (!form.value.zipCode) errors.value.zipCode = 'Il NAP è obbligatorio'
      if (!/^[0-9]{4}$/.test(form.value.zipCode)) errors.value.zipCode = 'Il NAP deve essere di 4 cifre'
      if (!form.value.city) errors.value.city = 'Il luogo è obbligatorio'
      if (!form.value.mobile) errors.value.mobile = 'Il cellulare è obbligatorio'
      return !Object.keys(errors.value).length
    case 2:
      if (!form.value.grade) errors.value.grade = 'La classe è obbligatoria'
      return !Object.keys(errors.value).length
    default:
      return false
  }
}

const handleStepNext = () => {
  if (validateCurrentStep()) {
    currentStep.value++
  }
}

const isValidGender = computed(() => {
  if (!props.slot) return true
  return isGenderAllowed(props.slot.gender_category as GenderCategory, form.value.gender as Gender)
})

const handleSubmit = (e: Event) => {
  if (!validateCurrentStep()) {
    e.preventDefault()
    return
  }
  if (!isValidGender.value) {
    alert('Il genere selezionato non è consentito per questo slot')
    return
  }
  emit('submit', form.value)
}
</script>
