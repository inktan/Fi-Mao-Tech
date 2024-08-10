<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ref, onMounted, onUnmounted } from 'vue'
import { standard_style_theme } from "@/gd_map_config.js";

const standardStyleThemeRef = ref(standard_style_theme)
const emit = defineEmits(['ChangeStyleTheme']);
const handleCommand = (command) => {
    //   ElMessage(`click on item ${command}`)
    emit('ChangeStyleTheme', command);
}
</script>

<template>
    <div class="toolbar-container">
        <div>
            <el-dropdown @command="handleCommand">
                <span class="el-dropdown-link">
                    样式切换 <el-icon>
                        <arrow-down />
                    </el-icon>
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item v-for="(item, index)  in standardStyleThemeRef" :key="index"
                            :command="index">{{ item }}</el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </div>
        <el-button circle>
            <el-icon>
                <Back />
            </el-icon>
        </el-button>
        <el-button circle>
            <el-icon>
                <Right />
            </el-icon>
        </el-button>

    </div>
</template>

<style lang="less" scoped>
.toolbar-container {
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;

    width: 420px;
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 10px;

    z-index: 0;
    background-color: aliceblue;

    .el-dropdown-link {
        background-color: rgb(255, 255, 255);
        border-radius: 20px;
        cursor: pointer;
        border: 1px solid rgb(214, 214, 214);
        margin-right: 8px;
        height: 30px;
        width: 100px;

        display: flex;
        align-items: center;
        justify-content: center;
    }
}
</style>
