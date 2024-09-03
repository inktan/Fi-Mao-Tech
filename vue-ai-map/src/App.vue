<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Aside from '@/components/Aside.vue'
import AIChat from '@/components/AIChat.vue'
import Trans from '@/components/Trans.vue'

</script>

<template>
  <div class="app-container">

    <div class="left-box">
      <Aside />

    </div>
    <div class="right-box">
      <RouterView />
    </div>

    <AIChat />
    <!-- <Trans /> -->
  </div>
</template>

<style lang="less" scoped>
.app-container {
  height: 100%;
  display: flex;

  .left-box {
    background-color: #000000;
    flex-shrink: 0;
  }

  .right-box {
    background-color: #f0f0f0;
    flex-grow: 1;
  }

}
</style>
