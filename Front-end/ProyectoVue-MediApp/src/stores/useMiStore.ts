import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useMiStore = defineStore('miStore', () => {
  const variable = ref<string | null>(null)

  function guardarVariable(valor: string | null) {
    variable.value = valor
  }

  return { variable, guardarVariable }
})
