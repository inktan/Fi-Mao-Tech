<script setup>
import { RouterLink, RouterView } from 'vue-router'
import Header from './components/Header.vue'
import Main from './components/Main.vue'
</script>


<template>
  <div class="container">
    <Header />
    <Main />
  </div>

</template>

<style lang="less">
.el-header {
  background-color: var(--el-color-success-light-9)
}

.el-main {
  background-color: var(--el-color-primary-light-9)
}

.el-footer {
  background-color: var(--el-color-success-light-9)
}
</style>
