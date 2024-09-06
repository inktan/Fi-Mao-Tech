<template>
    <el-radio-group v-model="isCollapse" style="margin-bottom: 20px">
        <el-radio-button :value="false"></el-radio-button>
        <el-radio-button :value="true"></el-radio-button>
    </el-radio-group>
    <el-menu default-active="2" class="el-menu-vertical-demo" :collapse="isCollapse" @open="handleOpen"
        @close="handleClose">
        <el-sub-menu index="1">
            <template #title>
                <el-icon>
                    <user />
                </el-icon>
                <span>游客身份</span>
            </template>
            <el-menu-item-group>
                <template #title><span>身份组合</span></template>
                <el-menu-item index="1-1">儿童</el-menu-item>
                <el-menu-item index="1-2">老人</el-menu-item>
            </el-menu-item-group>
            <el-menu-item-group title="角色">
                <el-menu-item index="1-3">登山者</el-menu-item>
                <el-menu-item index="1-3">骑行者</el-menu-item>
            </el-menu-item-group>
        </el-sub-menu>
        <el-menu-item index="2">
            <el-icon><icon-menu /></el-icon>
            <template #title>Navigator Two</template>
        </el-menu-item>
        <el-menu-item index="3" disabled>
            <el-icon>
                <document />
            </el-icon>
            <template #title>Navigator Three</template>
        </el-menu-item>
        <el-menu-item index="4">
            <el-icon>
                <setting />
            </el-icon>
            <template #title>设置</template>
        </el-menu-item>
    </el-menu>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import {
    Document,
    Menu as IconMenu,
    Location,
    Setting,
} from '@element-plus/icons-vue'

const isCollapse = ref(true)
const handleOpen = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
    console.log(key, keyPath)
}
</script>

<style>
.el-menu-vertical-demo:not(.el-menu--collapse) {
    width: 200px;
    min-height: 400px;
}
</style>