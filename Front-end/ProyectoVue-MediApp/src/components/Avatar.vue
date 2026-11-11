<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{ texto: string; foto?: string | null; propia?: boolean }>()

const fallo = ref(false)
const url = computed(() => {
  const foto = props.propia ? JSON.parse(localStorage.getItem('sesion') || '{}').foto : props.foto
  return foto ? `${import.meta.env.VITE_API_URL}${foto}` : null
})

watch(url, () => (fallo.value = false))
</script>

<template>
  <div class="overflow-hidden">
    <img v-if="url && !fallo" :src="url" alt="" class="size-full object-cover" @error="fallo = true" />
    <template v-else>{{ texto }}</template>
  </div>
</template>
