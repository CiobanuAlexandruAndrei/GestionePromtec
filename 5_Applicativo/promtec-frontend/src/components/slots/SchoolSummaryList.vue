<template>
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
      <h3 class="text-lg font-medium leading-6 text-gray-900">Riepilogo Scuole</h3>
      <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
        {{ schools.length }} scuole
      </span>
    </div>
    
    <div class="border-t border-gray-200">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Scuola
              </th>
              <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Studenti Iscritti
              </th>
              <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                In Attesa
              </th>
              <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Totale
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="school in schools" :key="school.name" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ school.name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="flex items-center justify-center">
                  <div :class="[
                    'px-2 py-1 inline-flex text-sm leading-5 font-medium rounded-full',
                    {
                      'bg-green-100 text-green-800': school.studentsCount < maxStudentsPerSchool,
                      'bg-yellow-100 text-yellow-800': school.studentsCount === maxStudentsPerSchool,
                      'bg-red-100 text-red-800': school.studentsCount > maxStudentsPerSchool
                    }
                  ]">
                    {{ school.studentsCount }}
                    <span class="text-gray-500 ml-1" v-if="maxStudentsPerSchool > 0">
                      / {{ maxStudentsPerSchool }}
                    </span>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="px-2 py-1 inline-flex text-sm leading-5 font-medium rounded-full bg-yellow-50 text-yellow-800">
                  {{ school.waitingCount }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-center">
                <div class="px-2 py-1 inline-flex text-sm leading-5 font-medium rounded-full bg-blue-50 text-blue-800">
                  {{ school.studentsCount + school.waitingCount }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface SchoolSummary {
  name: string;
  studentsCount: number;
  waitingCount: number;
}

defineProps<{
  schools: SchoolSummary[]
  maxStudentsPerSchool: number
}>()
</script>