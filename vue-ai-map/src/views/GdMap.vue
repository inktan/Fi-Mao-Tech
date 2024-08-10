<script setup>
import { RouterLink, RouterView } from 'vue-router'
import GdMapContainer from '@/components/GdMapContainer.vue'

</script>

<template>
  <div class="gd-map-container">
    <GdMapContainer />
  </div>
</template>

<style lang="less" scoped>
.gd-map-container {
  height: 100%;
  background-color: aliceblue;
  position: relative;
  overflow: hidden;
}
</style>
