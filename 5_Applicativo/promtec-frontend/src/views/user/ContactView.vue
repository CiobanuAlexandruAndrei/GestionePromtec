<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-semibold text-gray-800 mb-6">Contatti</h1>
    
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      <p class="mt-2 text-gray-600">Caricamento informazioni...</p>
    </div>
    
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
      {{ error }}
    </div>
    
    <div v-else class="bg-white rounded-lg shadow-sm p-6">
      <div class="flex items-center border-b border-gray-100 pb-4 mb-4">
        <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mr-4">
          <span class="text-xl font-semibold text-blue-600">
            {{ organizationInfo.first_name.charAt(0) }}{{ organizationInfo.last_name.charAt(0) }}
          </span>
        </div>
        <div>
          <h2 class="text-xl font-medium text-gray-800">{{ fullName }}</h2>
          <p class="text-gray-600 text-sm">Organizzatore Promtec</p>
        </div>
      </div>
      
      <div class="space-y-4">
        <div class="flex items-start">
          <div class="w-6 h-6 text-blue-500 mr-3 mt-1">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-800">Telefono</p>
            <p class="text-gray-600">{{ organizationInfo.telephone }}</p>
          </div>
        </div>
        
        <div class="flex items-start">
          <div class="w-6 h-6 text-blue-500 mr-3 mt-1">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-800">Email</p>
            <a href="mailto:{{ organizationInfo.email }}" class="text-blue-600 hover:underline">{{ organizationInfo.email }}</a>
          </div>
        </div>
        
        <div class="flex items-start">
          <div class="w-6 h-6 text-blue-500 mr-3 mt-1">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-800">Indirizzo</p>
            <p class="text-gray-600">Centro Professionale Tecnico di Trevano</p>
            <p class="text-gray-600">6952 Canobbio</p>
          </div>
        </div>
      </div>
      
      <div class="mt-8 pt-6 border-t border-gray-100">
        <h3 class="text-lg font-medium text-gray-800 mb-4">Come contattarci</h3>
        <p class="text-gray-600 mb-2">
          Se hai domande riguardo alle attività Promtec o necessiti di assistenza, non esitare a contattare direttamente l'organizzatore.
        </p>
        
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getOrganizationInfo } from '@/services/api'

const organizationInfo = ref({
  first_name: '',
  last_name: '',
  telephone: '',
  email: ''
})
const loading = ref(true)
const error = ref('')

const fullName = computed(() => {
  return `${organizationInfo.value.first_name} ${organizationInfo.value.last_name}`.trim()
})

onMounted(async () => {
  try {
    loading.value = true
    organizationInfo.value = await getOrganizationInfo()
  } catch (err) {
    error.value = 'Si è verificato un errore nel caricamento delle informazioni di contatto.'
    console.error('Error fetching organization info:', err)
  } finally {
    loading.value = false
  }
})
</script>
