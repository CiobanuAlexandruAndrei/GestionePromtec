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
        <h2 class="text-2xl font-semibold text-gray-800">Reimposta la tua password</h2>
        <p v-if="!tokenError && !resetSuccess" class="mt-2 text-sm text-gray-600">
          Inserisci una nuova password per l'account <span class="font-medium">{{ userEmail }}</span>
        </p>
      </div>
      
      <div v-if="isVerifying" class="flex justify-center items-center py-6">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
        <p class="ml-3 text-gray-700">Verifica in corso...</p>
      </div>
      
      <div v-else-if="tokenError" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm mt-4">
        <p class="font-medium mb-2">{{ tokenError }}</p>
        <p>
          Il link potrebbe essere scaduto o non essere più valido.
          <router-link to="/forgot-password" class="text-indigo-600 hover:text-indigo-500 font-medium">
            Richiedi un nuovo link
          </router-link>
        </p>
      </div>
      
      <div v-else-if="resetSuccess" class="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg text-sm mt-4">
        <p class="font-medium mb-2">{{ resetSuccess }}</p>
        <div class="text-center mt-4">
          <router-link 
            to="/login" 
            class="inline-flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            Vai al login
          </router-link>
        </div>
      </div>
      
      <form v-else class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>
        
        <div class="space-y-4">
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Nuova Password
            </label>
            <div class="relative mt-1">
              <input
                id="password"
                v-model="password"
                name="password"
                type="password"
                autocomplete="new-password"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
            <p class="mt-1 text-xs text-gray-500">La password deve contenere almeno 8 caratteri</p>
          </div>
          
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
              Conferma Password
            </label>
            <div class="relative mt-1">
              <input
                id="confirmPassword"
                v-model="confirmPassword"
                name="confirmPassword"
                type="password"
                autocomplete="new-password"
                required
                class="block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              />
            </div>
          </div>
        </div>
        
        <div v-if="password !== confirmPassword && confirmPassword" class="text-sm text-red-600 mt-2">
          Le password non corrispondono
        </div>
        
        <div v-if="password.length > 0 && password.length < 8" class="text-sm text-red-600 mt-2">
          La password deve contenere almeno 8 caratteri
        </div>
        
        <button
          type="submit"
          :disabled="isSubmitting || password.length < 8 || password !== confirmPassword"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isSubmitting">Reimpostazione in corso...</span>
          <span v-else>Reimposta password</span>
        </button>
      </form>
    </div>
    </div>
    <FooterComponent />
  </div>
</template>

<script setup lang="ts">
import FooterComponent from '@/components/FooterComponent.vue'
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { verifyResetToken, resetPassword } from '@/services/api';

const route = useRoute();
const router = useRouter();

const token = ref(route.params.token as string);
const userEmail = ref('');
const password = ref('');
const confirmPassword = ref('');
const error = ref('');
const tokenError = ref('');
const resetSuccess = ref('');
const isVerifying = ref(true);
const isSubmitting = ref(false);

onMounted(async () => {
  try {
    if (!token.value) {
      tokenError.value = 'Token non valido';
      isVerifying.value = false;
      return;
    }
    
    const response = await verifyResetToken(token.value);
    
    if (!response.valid) {
      tokenError.value = response.error || 'Token non valido o scaduto';
    } else {
      userEmail.value = response.email || '';
    }
  } catch (err) {
    tokenError.value = 'Errore durante la verifica del token';
    console.error('Error verifying token:', err);
  } finally {
    isVerifying.value = false;
  }
});

const handleSubmit = async () => {
  try {
    isSubmitting.value = true;
    error.value = '';
    
    // Validate password
    if (password.value.length < 8) {
      error.value = 'La password deve contenere almeno 8 caratteri.';
      return;
    }
    
    if (password.value !== confirmPassword.value) {
      error.value = 'Le password non corrispondono.';
      return;
    }
    
    const response = await resetPassword(token.value, password.value);
    resetSuccess.value = response.message;
    
    // Clear form
    password.value = '';
    confirmPassword.value = '';
    
    // Redirect to login after 5 seconds
    setTimeout(() => {
      router.push('/login');
    }, 5000);
    
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Si è verificato un errore durante il ripristino della password.';
    console.error('Error resetting password:', err);
  } finally {
    isSubmitting.value = false;
  }
};
</script>
