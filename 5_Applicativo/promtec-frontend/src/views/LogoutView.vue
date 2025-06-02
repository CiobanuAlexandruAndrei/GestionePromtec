<script setup lang="ts">
import FooterComponent from '@/components/FooterComponent.vue'
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {

  authStore.clearAuth()
  
  setTimeout(() => {
    router.push('/login')
  }, 2000)
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-50">
    <div class="flex-grow flex items-center justify-center">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-sm">
      <div class="flex flex-col items-center">
        <div class="h-16 w-16 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold mb-6">
          <img
            src="@/assets/img/logo_cpt.jpg"
            alt="CPT Logo"
            class="w-full h-full object-contain rounded-lg"
          />
        </div>
        <h2 class="text-2xl font-semibold text-gray-800">
          Uscendo dall'account...
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Grazie per aver utilizzato Gestione Promtec
        </p>
      </div>
    </div>
    </div>
    <FooterComponent />
  </div>
</template>