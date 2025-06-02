<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { LogOut, User } from 'lucide-vue-next'
import FooterComponent from './FooterComponent.vue'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  router.push('/logout')
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- Navigation -->
    <nav class="bg-white border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex justify-between h-16">
          <!-- Logo and Brand -->
          <div class="flex items-center">
            <div class="w-14 h-14 flex-shrink-0 bg-indigo-100 rounded-lg flex items-center justify-center">
              <img 
                src="@/assets/img/logo_cpt.jpg" 
                alt="Logo" 
                class="w-11 h-11 object-contain rounded"
              />
            </div>
            <div class="ml-4">
              <h2 class="text-lg font-semibold text-slate-800">SAMT</h2>
              <p class="text-sm font-medium text-slate-600">Gestione Promtec</p>
            </div>
          </div>
          
          <!-- Navigation Links -->
          <div class="flex items-center space-x-6">
            <router-link 
              to="/" 
              class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
              :class="{ 
                'bg-blue-50 text-blue-700': $route.path === '/' || $route.path.startsWith('/slot'),
                'text-slate-600 hover:bg-slate-50 hover:text-slate-900': !($route.path === '/' || $route.path.startsWith('/slot'))
              }"
            >
              Slots
            </router-link>
            <router-link 
              to="/contact" 
              class="px-4 py-2 text-sm font-medium rounded-md transition-colors"
              :class="{ 
                'bg-blue-50 text-blue-700': $route.path === '/contact',
                'text-slate-600 hover:bg-slate-50 hover:text-slate-900': $route.path !== '/contact'
              }"
            >
              Contatti
            </router-link>
            
            <!-- User Menu -->
            <div class="flex items-center pl-6 ml-6 border-l border-slate-200">
              <div class="flex items-center">
                <div class="w-9 h-9 rounded bg-blue-50 flex items-center justify-center text-blue-700">
                  <User class="w-5 h-5" />
                </div>
                <span class="ml-2 text-sm font-medium text-slate-700">{{ authStore.userFullName }}</span>
              </div>
              <button 
                @click="handleLogout"
                class="ml-4 p-2 rounded text-slate-400 hover:text-red-600 hover:bg-slate-100"
                title="Logout"
              >
                <LogOut class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="bg-slate-50 flex-grow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <slot></slot>
      </div>
    </main>
    
    <!-- Footer -->
    <div class="bg-white">
      <FooterComponent />
    </div>
  </div>
</template>