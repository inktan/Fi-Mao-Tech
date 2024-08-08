<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader';

// import HelloWorld from './components/HelloWorld.vue'
import { web_frontend_key,web_frontend_secret_key } from "@/gd_map_config.js";

// console.log(`key_web_js:${key_web_js}`)

let map = null;

onMounted(() => {
  window._AMapSecurityConfig = {
    securityJsCode: web_frontend_secret_key,
  };
  AMapLoader.load({
    key: web_frontend_key, // 申请好的Web端开发者Key，首次调用 load 时必填
    version: "2.0", // 指定要加载的 JSAPI 的版本，缺省时默认为 1.4.15
    plugins: ["AMap.Scale"], //需要使用的的插件列表，如比例尺'AMap.Scale'，支持添加多个如：['...','...']
  }).then((AMap) => {
    map = new AMap.Map("container", {
      // 设置地图容器id
      viewMode: "3D", // 是否为3D地图模式
      zoom: 11, // 初始化地图级别
      center: [116.397428, 39.90923], // 初始化地图中心点位置
    });
  }).catch((e) => {
    console.log(e);
  });
});

onUnmounted(() => {
  map?.destroy();
});
</script>

<template>
  <div id="container"></div>
</template>

<style lang="less" scoped>
#container {
  padding: 0px;
  margin: 0px;
  width: 500px;
  height: 500px;
}
</style>
