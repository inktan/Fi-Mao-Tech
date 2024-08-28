<script setup lang="ts">
import { ref,onUnmounted } from "vue";

const props = defineProps<{ content: string }>();

const btnTips = {
  copy: "复制全文",
  loading: "",
  success: "已复制到剪贴板！",
  error: "复制失败！",
};

const btnStatus = ref<"copy" | "loading" | "success" | "error">("copy");

const copyToClipboard = (content: string = props.content) => {
  btnStatus.value = "loading";
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard
      .writeText(content)
      .then(() => {
        const successTimeout = setTimeout(() => {
          btnStatus.value = "success";
        }, 150);
        // 如果组件销毁，清理定时器
        onUnmounted(() => clearTimeout(successTimeout));
      })
      .catch(() => {
        btnStatus.value = "error";
        console.error("Failed to copy text to clipboard");
      })
      .finally(() => {
        const resetTimeout = setTimeout(() => {
          btnStatus.value = "copy";
        }, 1500);
        // 如果组件销毁，清理定时器
        onUnmounted(() => clearTimeout(resetTimeout));
      });
  } else {
    // 浏览器不支持 clipboard API
    btnStatus.value = "error";
    console.error("Clipboard API is not supported in this browser.");
  }
};
</script>

<template>
  <div class="flex items-center cursor-pointer" @click="copyToClipboard()">
    <el-icon v-show="btnStatus === 'copy'">
      <CopyDocument />
    </el-icon>
    <el-icon v-show="btnStatus === 'loading'">
      <Loading />
    </el-icon>
    <el-icon v-show="btnStatus === 'success'">
      <SuccessFilled />
    </el-icon>
    <el-icon v-show="btnStatus === 'error'">
      <CircleClose />
    </el-icon>
    <span class="">{{ btnTips[btnStatus] }}</span>
  </div>
</template>

<style scoped></style>
