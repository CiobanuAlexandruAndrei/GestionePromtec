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
          Pagina non trovata
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          La pagina che stai cercando non esiste.
        </p>
        <router-link 
          to="/" 
          class="mt-6 w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
        >
          Torna alla home
        </router-link>
      </div>
    </div>
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import FooterComponent from '@/components/FooterComponent.vue'

</script>