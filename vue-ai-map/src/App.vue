<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AIChat from '@/components/AIChat.vue'
import Trans from '@/components/Trans.vue'

</script>

<template>
  <div class="app-container">
    <!-- <GdMap /> -->
    <!-- <RouterView /> -->
    <AIChat />
    <Trans />
  </div>
</template>

<style lang="less" scoped>
.app-container {
  position: relative;
  height: 100%;
}
</style>
