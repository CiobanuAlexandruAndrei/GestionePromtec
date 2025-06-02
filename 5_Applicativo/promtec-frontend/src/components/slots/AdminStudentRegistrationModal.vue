<template>
  <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl overflow-hidden max-w-3xl w-full mx-4">
      <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
        <h3 class="text-lg font-medium leading-6 text-gray-900">
          Nuovo studente
        </h3>
        <button @click="$emit('close')" type="button" class="text-gray-400 hover:text-gray-500">
          <X class="h-5 w-5" />
        </button>
      </div>

      <div class="p-6">
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
                  @click="currentStep = index"
                  :class="[
                    'flex items-center justify-center w-8 h-8 rounded-full border-2 font-semibold text-sm',
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
                <template v-if="!slotGenderCategory || slotGenderCategory === GenderCategory.MIXED">
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
                        Slot riservato {{ slotGenderCategory === GenderCategory.BOYS ? 'ai ragazzi' : 'alle ragazze' }}
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
                label="Via"
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
                v-model="form.school"
                label="Scuola"
                type="select"
                :required="currentStep === 2"
                :options="schoolOptions"
                :error="errors.school"
                icon="GraduationCap"
              />
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
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <UserPlus class="h-4 w-4 mr-1.5" />
                Registra
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, defineEmits } from 'vue'
import {
  BookOpen,
  Building,
  ChevronLeft,
  ChevronRight,
  GraduationCap,
  Hash,
  MapPin,
  Phone,
  Smartphone,
  User,
  UserPlus,
  Users2,
  UserSquare2,
  X,
  Info
} from 'lucide-vue-next'
import FormField from '@/components/forms/FormField.vue'
import type { Student } from '@/types/slot'
import { Gender, GenderCategory, isGenderAllowed } from '@/types/slot'
import { getSchools } from '@/services/api'

const props = defineProps<{
  isSubmitting: boolean
  slotGenderCategory?: GenderCategory
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', formData: Partial<Student>): void
}>()

const schools = ref<string[]>([])
const errors = ref<Record<string, string>>({})
const currentStep = ref(0)

const steps = [
  { name: 'Dati Personali', icon: User },
  { name: 'Contatti', icon: Phone },
  { name: 'Scuola', icon: GraduationCap }
]

const form = ref<Partial<Student>>({
  firstName: '',
  lastName: '',
  gender: props.slotGenderCategory === GenderCategory.GIRLS ? Gender.GIRL : 
          props.slotGenderCategory === GenderCategory.BOYS ? Gender.BOY :
          Gender.BOY,
  street: '',
  zipCode: '',
  city: '',
  phone: '',
  mobile: '',
  school: '',
  grade: '',
  status: 'pending'
})

// Validation computed properties
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
  return form.value.school &&
         form.value.grade
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

const genderOptions = computed(() => {
  if (!props.slotGenderCategory || props.slotGenderCategory === GenderCategory.MIXED) {
    return [
      { value: Gender.BOY, label: 'Maschio' },
      { value: Gender.GIRL, label: 'Femmina' }
    ]
  } else if (props.slotGenderCategory === GenderCategory.BOYS) {
    return [{ value: Gender.BOY, label: 'Maschio' }]
  } else {
    return [{ value: Gender.GIRL, label: 'Femmina' }]
  }
})

const schoolOptions = computed(() => {
  return schools.value.map(school => ({
    value: school,
    label: school
  }))
})

const genderError = computed(() => {
  if (currentStep.value === 0 && !form.value.gender) {
    return 'Il sesso è obbligatorio'
  }
  if (!isValidGender.value) {
    return 'Il genere selezionato non è consentito per questo slot'
  }
  return ''
})

const isValidGender = computed(() => {
  if (!props.slotGenderCategory) return true
  return isGenderAllowed(props.slotGenderCategory, form.value.gender as Gender)
})

watch(() => props.slotGenderCategory, (newCategory) => {
  if (!newCategory) return
  if (newCategory === GenderCategory.BOYS) {
    form.value.gender = Gender.BOY
  } else if (newCategory === GenderCategory.GIRLS) {
    form.value.gender = Gender.GIRL
  }
}, { immediate: true })

const validateCurrentStep = () => {
  errors.value = {}
  
  switch (currentStep.value) {
    case 0:
      if (!form.value.firstName) errors.value.firstName = 'Il nome è obbligatorio'
      if (!form.value.lastName) errors.value.lastName = 'Il cognome è obbligatorio'
      if (!form.value.gender) errors.value.gender = 'Il sesso è obbligatorio'
      return !Object.keys(errors.value).length
    case 1:
      if (!form.value.street) errors.value.street = 'La via è obbligatoria'
      if (!form.value.zipCode) errors.value.zipCode = 'Il NAP è obbligatorio'
      if (!form.value.zipCode || !/^[0-9]{4}$/.test(form.value.zipCode)) errors.value.zipCode = 'Il NAP deve essere di 4 cifre'
      if (!form.value.city) errors.value.city = 'Il luogo è obbligatorio'
      if (!form.value.mobile) errors.value.mobile = 'Il cellulare è obbligatorio'
      return !Object.keys(errors.value).length
    case 2:
      if (!form.value.school) errors.value.school = 'La scuola è obbligatoria'
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

const handleSubmit = (e: Event) => {
  if (!validateCurrentStep()) {
    e.preventDefault()
    return
  }
  if (!isValidGender.value) {
    alert('Il genere selezionato non è consentito per questo slot')
    return
  }
  emit('submit', {
    firstName: form.value.firstName,
    lastName: form.value.lastName,
    gender: form.value.gender,
    street: form.value.street,
    zipCode: form.value.zipCode,
    city: form.value.city,
    phone: form.value.phone,
    mobile: form.value.mobile,
    school: form.value.school,
    grade: form.value.grade,
    status: 'pending'
  })
}

onMounted(async () => {
  try {
    schools.value = await getSchools()
  } catch (err) {
    console.error('Failed to fetch schools:', err)
    errors.value.school = 'Errore nel caricamento delle scuole. Riprova più tardi.'
  }
})
</script>