<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { onMounted, ref } from "vue";
import Aside from '@/components/Aside.vue'
import AIChat from '@/components/AIChat.vue'
import Weather from '@/components/Weather.vue'
import { useProjectStore } from "@/pinia.js";

console.log('进入App.vue')
const store = useProjectStore()
onMounted(() => {
  onResize()
  window.addEventListener('resize', () => {
    onResize()
  })
})

function onResize() {
  store.windowInsets.height = window.innerHeight
  store.windowInsets.width = window.innerWidth
  store.contentInsets.heightContent = window.innerHeight - store.contentInsets.heightToolbar - store.contentInsets.heightPager
  store.contentInsets.widthContent = window.innerWidth - store.navWidth
  // console.log(store.isInPortraitMode)
}

</script>

<template>
  <RouterView />
</template>

<style lang="less" scoped>

</style>
