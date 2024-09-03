<script lang="ts" setup>
import {
    Document,
    Menu as IconMenu,
    Location,
    Setting,
} from '@element-plus/icons-vue'

import { ref } from 'vue'

const isCollapse = ref(true)
const handleOpen = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}
</script>

<template>
    <div class="container">
        <el-radio-group v-model="isCollapse">
            <el-radio-button :value="false"></el-radio-button>
            <el-radio-button :value="true"></el-radio-button>
        </el-radio-group>

        <!-- <h5 class="mb-2">Custom colors</h5> -->
        <el-menu :collapse="isCollapse" active-text-color="#ffd04b" background-color="#545c64" default-active="2"
            text-color="#fff" @open="handleOpen" @close="handleClose">
            <el-sub-menu index="1">
                <template #title>
                    <el-icon>
                        <location />
                    </el-icon>
                    <span>Navigator One</span>
                </template>
                <el-menu-item-group title="Group One">
                    <el-menu-item index="1-1">item one</el-menu-item>
                    <el-menu-item index="1-2">item two</el-menu-item>
                </el-menu-item-group>
                <el-menu-item-group title="Group Two">
                    <el-menu-item index="1-3">item three</el-menu-item>
                </el-menu-item-group>
                <el-sub-menu index="1-4">
                    <template #title>item four</template>
                    <el-menu-item index="1-4-1">item one</el-menu-item>
                </el-sub-menu>
            </el-sub-menu>
            <el-menu-item index="2">
                <el-icon><icon-menu /></el-icon>
                <span>Navigator Two</span>
            </el-menu-item>
            <el-menu-item index="3" disabled>
                <el-icon>
                    <document />
                </el-icon>
                <span>Navigator Three</span>
            </el-menu-item>
            <el-menu-item index="4">
                <el-icon>
                    <setting />
                </el-icon>
                <span>Navigator Four</span>
            </el-menu-item>
        </el-menu>
    </div>
</template>

<style lang="less" scoped>
.container {
    // padding-top: 30px;
    background-color: #545c64;
    position: relative;
    height: 100%;

    .el-menu {
        border: 0;
    }
}
</style>
