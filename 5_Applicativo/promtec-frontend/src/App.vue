<script setup lang="ts">
import SidebarLayout from './components/SidebarLayout.vue'
import NavbarLayout from './components/NavbarLayout.vue'
import Toast from './components/ui/Toast.vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notificationStore'
import { computed } from 'vue'

const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const isPublicRoute = computed(() => route.meta.public === true)
</script>

<template>
  <div class="h-screen flex flex-col">
    <!-- Global Toast Notification -->
    <Toast
      :show="notificationStore.show"
      :title="notificationStore.title"
      :message="notificationStore.message"
      :type="notificationStore.type"
      @close="notificationStore.hideNotification()"
    />
    
    <template v-if="!isPublicRoute">
      <SidebarLayout v-if="authStore.isAdmin">
        <div class="h-full overflow-y-auto">
          <router-view />
        </div>
      </SidebarLayout>
      <NavbarLayout v-else>
        <router-view />
      </NavbarLayout>
    </template>
    <router-view v-else />
  </div>
</template>

<style>
html, body, #app {
  height: 100%;
}
</style>
