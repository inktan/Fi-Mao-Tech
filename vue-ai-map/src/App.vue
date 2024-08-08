<script setup>
import { RouterLink, RouterView } from 'vue-router'
import GdMapContainer from '@/components/GdMapContainer.vue'

</script>

<template>
  <div class="gd-map-container">
    <GdMapContainer />
  </div>
  <!-- <RouterView /> -->
</template>

<style scoped>
.gd-map-container {
  height: 600px;
  background-color: aliceblue;
}
</style>
