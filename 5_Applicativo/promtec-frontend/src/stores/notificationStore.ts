import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const show = ref(false)
  const title = ref('')
  const message = ref('')
  const type = ref<'success' | 'error' | 'info'>('info')
  let timeout: number | null = null

  function showNotification(
    newTitle: string,
    newMessage: string = '',
    newType: 'success' | 'error' | 'info' = 'info',
    duration: number = 5000
  ) {
    // Clear any existing timeout
    if (timeout) {
      clearTimeout(timeout)
      timeout = null
    }

    // Set new notification data
    title.value = newTitle
    message.value = newMessage
    type.value = newType
    show.value = true

    // Auto-hide after duration
    if (duration > 0) {
      timeout = window.setTimeout(() => {
        hideNotification()
      }, duration)
    }
  }

  function hideNotification() {
    show.value = false
    if (timeout) {
      clearTimeout(timeout)
      timeout = null
    }
  }

  return {
    show,
    title,
    message,
    type,
    showNotification,
    hideNotification
  }
})
