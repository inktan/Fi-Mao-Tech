<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'

import { ref } from 'vue'
const lng = ref(112.2148645)
const lat = ref(31.04392086)
const data = ref(null);
const panoramas = ref([])
const loading = ref(false)

const handleClick = async function () {
  loading.value = true
  const params = {
    'lng': lng.value,
    'lat': lat.value,
  }
  // 创建URLSearchParams实例并填充参数
  const searchParams = new URLSearchParams();
  for (const key in params) {
    searchParams.append(key, params[key]);
  }
  const get_url = `http://10.1.12.30:5002/get_lng_lat_info?${searchParams.toString()}`
  const response = await fetch(get_url);
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  data.value = await response.json();
  panoramas.value = data.value.panoramas;
  loading.value = false

  // console.log(panoramas.value)
}

</script>

<template>
  <div class="box">
    <p>输入经纬度，查询可下载的街景日期</p>
    <el-form label-width="auto" style="max-width: 500px">
      <el-form-item label="经度">
        <el-input v-model="lng" />
      </el-form-item>
      <el-form-item label="纬度">
        <el-input v-model="lat" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleClick">查询</el-button>
      </el-form-item>
    </el-form>
    <div>
      <p>可下载的街景日期:</p>
      <div>
        <el-table :data="panoramas" style="width: 100%" v-loading="loading">
          <el-table-column prop="road_name" label="RoadName" width="200" />
          <el-table-column prop="id" label="ID" width="300" />
          <el-table-column prop="year_month" label="Date" width="100" />
          <el-table-column prop="year" label="Year" width="100" />
          <el-table-column prop="month" label="Month" width="100" />
        </el-table>
      </div>
    </div>
    <RouterView />
  </div>

</template>

<style scoped lang=" less">

</style>
