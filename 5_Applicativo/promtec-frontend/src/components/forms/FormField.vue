<template>
  <div class="w-full">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <component
        v-if="icon"
        :is="getIcon()"
        class="absolute left-3 top-2.5 h-4 w-4 text-gray-400"
      />
      
      <select
        v-if="type === 'select'"
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
        :required="required"
        class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white"
        :class="{ 'border-red-300': error }"
      >
        <option
          v-for="option in options"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>

      <input
        v-else
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        :type="type"
        :required="required"
        :pattern="pattern"
        :maxlength="maxlength"
        class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
        :class="{ 'border-red-300': error }"
      />
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { User, Users2, MapPin, Hash, Building, Phone, Smartphone, GraduationCap, BookOpen, Building2 } from 'lucide-vue-next'

interface Props {
  modelValue: string | undefined
  label?: string
  type?: string
  required?: boolean
  error?: string
  icon?: string
  pattern?: string
  maxlength?: string
  options?: { value: string; label: string }[]
}

const props = defineProps<Props>()

const getIcon = () => {
  switch (props.icon) {
    case 'User': return User
    case 'Users2': return Users2
    case 'MapPin': return MapPin
    case 'Hash': return Hash
    case 'Building': return Building
    case 'Building2': return Building2
    case 'Phone': return Phone
    case 'Smartphone': return Smartphone
    case 'GraduationCap': return GraduationCap
    case 'BookOpen': return BookOpen
    default: return null
  }
}
</script>