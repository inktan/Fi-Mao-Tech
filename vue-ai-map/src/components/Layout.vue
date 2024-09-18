<script setup>
import Aside from '@/components/Aside.vue'
</script>

<template>
  <div class="common-layout">
    <el-container>
      <Aside />
      <el-main>
        <RouterView />
      </el-main>
    </el-container>
  </div>

  <AIChat />
  <Weather />
</template>

<style lang="less" scoped>
.common-layout {
  height: 100%;

  .el-container {
    height: 100%;

    .el-main {
      margin: 0;
      padding: 0;
      height: 100%;

    }
  }
}
</style>
