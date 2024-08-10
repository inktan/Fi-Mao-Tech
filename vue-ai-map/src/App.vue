<script setup>
import { RouterLink, RouterView } from 'vue-router'
import GdMap from '@/views/GdMap.vue'

</script>

<template>
  <div class="app-container">
    <GdMap />
  </div>
  <!-- <RouterView /> -->
</template>

<style lang="less" scoped>
.app-container {
  position: relative;
  height: 100%;
}
</style>
