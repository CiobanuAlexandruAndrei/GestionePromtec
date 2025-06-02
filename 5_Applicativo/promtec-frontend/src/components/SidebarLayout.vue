<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  User,
  Users,
  GraduationCap,
  Building,
  Calendar,
  LogOut,
  Menu,
  X,
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const isSidebarOpen = ref(false)

const handleLogout = () => {
  router.push('/logout')
}

// Updated navigation items
const navItems = [
  { icon: Calendar, label: 'Slots', path: '/' },
  //{ icon: Building, label: 'Scuole', path: '/schools' },
  //{ icon: GraduationCap, label: 'Studenti', path: '/students' },
  { icon: Users, label: 'Utenti', path: '/users' },
]
</script>

<template>
  <div class="h-full bg-slate-50">
    <div class="flex h-full">
      <!-- Mobile Menu Button -->
      <button 
        @click="isSidebarOpen = !isSidebarOpen"
        class="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-white shadow-sm"
      >
        <Menu v-if="!isSidebarOpen" class="w-6 h-6" />
        <X v-else class="w-6 h-6" />
      </button>

      <!-- Sidebar -->
      <div 
        :class="[
          'fixed top-0 left-0 h-full w-64 bg-white border-r border-slate-200 transform transition-transform duration-200 ease-in-out z-40',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        ]"
      >
        <div class="flex flex-col h-full">
          <!-- Logo Section -->
          <div class="p-6 ">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 flex-shrink-0 bg-indigo-100 rounded-lg flex items-center justify-center">
                <img 
                  src="@/assets/img/logo_cpt.jpg" 
                  alt="Logo" 
                  class="w-11 h-11 object-contain rounded"
                />
              </div>
              <div>
                <h2 class="text-lg font-semibold text-slate-800">SAMT</h2>
                <p class="text-sm font-medium text-slate-600">Gestione Promtec</p>
              </div>
            </div>
          </div>

          <!-- Navigation Links -->
          <nav class="flex-1 py-8 px-4">
            <div class="space-y-2">
              <router-link
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                @click="isSidebarOpen = false"
                class="flex items-center px-4 py-3 text-sm font-medium rounded-md transition-colors"
                :class="[
                  $route.path === item.path
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                ]"
              >
                <component :is="item.icon" class="w-5 h-5 mr-4" :class="$route.path === item.path ? 'text-blue-700' : 'text-slate-400'" />
                {{ item.label }}
              </router-link>
            </div>
          </nav>

          <!-- User Profile -->
          <div class="p-4 border-t border-slate-200 bg-slate-50">
            <div class="flex items-center justify-between px-2">
              <div class="flex items-center">
                <div class="w-9 h-9 rounded bg-blue-50 flex items-center justify-center">
                  <User class="w-5 h-5 text-blue-600" />
                </div>
                <div class="ml-3">
                  <p class="text-sm font-medium text-slate-700">{{ authStore.userFullName }}</p>
                  <p class="text-xs text-slate-500">{{ authStore.isAdmin ? 'Amministratore' : 'Utente' }}</p>
                </div>
              </div>
              <button 
                @click="handleLogout"
                class="p-2 rounded text-slate-400 hover:text-red-600 hover:bg-slate-100"
                title="Logout"
              >
                <LogOut class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Overlay -->
      <div 
        v-if="isSidebarOpen" 
        class="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-30 lg:hidden"
        @click="isSidebarOpen = false"
      ></div>

      <!-- Main Content -->
      <div class="flex-1 ml-0 lg:ml-64">
        <slot></slot>
      </div>
    </div>
  </div>
</template>