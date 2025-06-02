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
        <h2 class="text-2xl font-semibold text-gray-800">Recupero Password</h2>
        <p class="mt-2 text-sm text-gray-600">
          Inserisci l'indirizzo email associato al tuo account e riceverai un link per reimpostare la password.
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div v-if="message" class="bg-blue-50 border border-blue-200 text-blue-600 px-4 py-3 rounded-lg text-sm">
          {{ message }}
        </div>
        
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>
        
        <div class="space-y-4">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email
            </label>
            <div class="relative mt-1">
              <input
                id="email"
                v-model="email"
                name="email"
                type="email"
                autocomplete="email"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                placeholder="nome@esempio.com"
              />
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="text-sm">
            <router-link to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">
              Torna al login
            </router-link>
          </div>
        </div>
        
        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isSubmitting">Invio in corso...</span>
          <span v-else>Invia link di recupero</span>
        </button>
      </form>
    </div>
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { forgotPassword } from '@/services/api';
import FooterComponent from '@/components/FooterComponent.vue';

const email = ref('');
const error = ref('');
const message = ref('');
const isSubmitting = ref(false);

const handleSubmit = async () => {
  try {
    isSubmitting.value = true;
    error.value = '';
    message.value = '';
    
    // Validate email
    if (!email.value) {
      error.value = 'Inserisci un indirizzo email.';
      return;
    }
    
    const response = await forgotPassword(email.value);
    message.value = response.message;
    
    // Clear the form
    email.value = '';
    
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Si è verificato un errore durante l\'invio della richiesta.';
    console.error('Error requesting password reset:', err);
  } finally {
    isSubmitting.value = false;
  }
};
</script>
