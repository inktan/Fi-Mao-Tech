<template>
    <div class="logo-container" @click="handleCollapseToggle">
        <el-avatar :size="50" :src="circleUrl" />
    </div>
</template>

<script lang="ts" setup>
import { ref, reactive, toRefs } from 'vue'
import {useProjectStore} from "@/pinia.js";

const store = useProjectStore()

const state = reactive({
    circleUrl:
        'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    squareUrl:
        'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png',
    sizeList: ['small', '', 'large'] as const,
})
const { circleUrl, squareUrl, sizeList } = toRefs(state)

function handleCollapseToggle() {
    console.log('handleCollapseToggle')
    store.navMenuCollapse = !store.navMenuCollapse

    // if (innerHeight < innerWidth){
    //     store.navMenuCollapse = !store.navMenuCollapse
        // store.navWidth = store.navMenuIsClosed ? 64 : 200
    // } else {
        // store.isShowingMenuToggleBtn = !store.isShowingMenuToggleBtn
    // }
}
</script>

<style>
.logo-container {
    padding:20px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-bottom: 1px solid;
}
</style>