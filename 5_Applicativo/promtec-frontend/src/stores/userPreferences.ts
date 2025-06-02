import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

type ViewMode = 'grid' | 'list'

export const useUserPreferencesStore = defineStore('userPreferences', () => {
  // State
  const viewMode = ref<ViewMode>(localStorage.getItem('preferredView') as ViewMode || 'grid')

  // Actions
  function setViewMode(mode: ViewMode) {
    viewMode.value = mode
    localStorage.setItem('preferredView', mode)
  }

  return {
    // State
    viewMode: computed(() => viewMode.value),
    
    // Actions
    setViewMode
  }
})