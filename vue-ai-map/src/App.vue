<script setup>
import { RouterLink, RouterView } from 'vue-router'
import GdMap from '@/components/GdMap.vue'

</script>

<template>
  <header>
    <GdMap />
  </header>
  <!-- <RouterView /> -->
</template>

<style scoped>
header {
  height: 120px;
  background-color: aliceblue;
}
</style>
