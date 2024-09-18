<template>
    <el-aside width="200px">
        <!-- <div> -->
        <Avatar class="header" />
        <!-- <div class="content">
            <NavSidebar />
        </div> -->
        <NavSidebar class="content" />

        <Copyright class="footer" />
        <!-- </div> -->
    </el-aside>
</template>

<script lang="ts" setup>
import { ref, reactive, toRefs } from 'vue'
import Avatar from "./Avatar.vue"
import NavSidebar from "./NavSidebar.vue"
import Copyright from "./Copyright.vue"

</script>

<style lang="less" scoped>
/* 设置外部容器为 flex 布局，垂直方向排列 */
.el-aside {
    display: flex;
    flex-direction: column;
    height: 100%;

    .header,
    .footer {
        height: 100px;
    }

    .content {
        flex-grow: 1;
        overflow: auto;
    }
}
</style>