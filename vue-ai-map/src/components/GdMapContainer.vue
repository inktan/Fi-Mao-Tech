<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader';
import ToolBar from '@/components/ToolBar.vue'

// import HelloWorld from './components/HelloWorld.vue'
import { web_frontend_key, web_frontend_secret_key } from "@/gd_map_config.js";
import { shanghai, suzhou, wuxi } from "@/data/shanghai.js";
import { ElSlider } from 'element-plus';
import { addressToLonLat, lonLatToAddress } from "@/api";

// console.log(`key_web_js:${key_web_js}`)
const styleTheme = ref('dark')
let map = null;
let aMap = null;
let geocoder = null;

onMounted(() => {
  window._AMapSecurityConfig = {
    securityJsCode: web_frontend_secret_key,
    // serviceHost: "http://39.98.218.136:8801/_AMapService",
  };

  AMapLoader.load({
    key: web_frontend_key, // 申请好的Web端开发者Key，首次调用 load 时必填
    version: "2.0", // 指定要加载的 JSAPI 的版本，缺省时默认为 1.4.15
    plugins: [
      "AMap.Scale",    //比例尺
      'AMap.ToolBar',    //放大 缩小控件
      "AMap.PlaceSearch",    //地点搜索
      "AMap.Driving",    //驾车导航
      "AMap.Transfer",    //公交导航
      "AMap.Walking",    //步行路导航
      "AMap.Riding",    // "AMap.Riding" 骑行导航
      "AMap.TruckDriving",    // 货车导航
      "AMap.DragRoute",
      "AMap.Geocoder",
    ],
  }).then((AMap) => {
    aMap = AMap;

    const layer = new aMap.createDefaultLayer({
      zooms: [3, 20], //可见级别
      visible: true, //是否可见
      opacity: 1, //透明度
      zIndex: 0, //叠加层级
    });

    map = new aMap.Map("container", {
      rotateEnable: false,
      pitchEnable: true,
      viewMode: "2D", // 是否为3D地图模式
      zoom: 16, // 初始化地图级别
      // center: [116.397428, 39.90923], // 初始化地图中心点位置-北京
      center: [120.629029, 31.32416], // 初始化地图中心点位置-苏州拙政园
      mapStyle: `amap://styles/${styleTheme.value}`, //设置地图的显示样式
      layers: [layer], //layer为创建的默认图层
    });


    var geocoder = new aMap.Geocoder({
      city: "苏州", // city 指定进行编码查询的城市，支持传入城市名、adcode 和 citycode
    });

    // end
  })
});

function getDragRoute() {
}

onUnmounted(() => {
  map?.destroy();
});

const btnNavigation = async function () {
  const addresses = ['苏州市拙政园', '苏州平江历史文化街区', '苏州市留园']
  var points = [];

  for (let address of addresses)  // x 为属性名
  {
    let resp = await addressToLonLat(address)
    let jsonData = await resp.json()
    var coord = jsonData.geocodes[0].location
    points.push(coord.split(',').map(str => parseFloat(str)));
  }

  var startLngLat = points[0]; //起始点坐标
  var endLngLat = points[2]; //终点坐标
  var opts = {
    waypoints: [points[1]], //途经点参数，最多支持传入16个途经点
  };

  var driving = new AMap.Driving({
    policy: 11, //驾车路线规划策略，0是速度优先的策略
    map: map,
    //panel 指定将结构化的路线详情数据显示的对应的 DOM 上，传入值需是 DOM 的 ID
    panel: "drive-panel", 
  });

  driving.search(startLngLat, endLngLat, opts, function (status, result) {
    //status：complete 表示查询成功，no_data 为查询无结果，error 代表查询错误
    //查询成功时，result 即为对应的驾车导航信息
    console.log(status)
    console.log(result)
  });




}

const reSet = async function () {
  // 重置地图界面
  map = new aMap.Map("container", {
    rotateEnable: false,
    pitchEnable: true,
    viewMode: "2D", // 是否为3D地图模式
    zoom: 16, // 初始化地图级别
    // center: [116.397428, 39.90923], // 初始化地图中心点位置-北京
    center: [120.629029, 31.32416], // 初始化地图中心点位置-苏州拙政园
    mapStyle: `amap://styles/${styleTheme.value}`, //设置地图的显示样式
    // layers: [layer], //layer为创建的默认图层
  });
}
const test = async function () {
  const resp = await addressToLonLat(120.629211, 31.324194)
  const jsonData = await resp.json()
  console.log(jsonData.geocodes[0].formatted_address)
}

const handleChangeStyleTheme = function (index) {
  console.log(index);
  const styleName = `amap://styles/${index}`
  map.setMapStyle(styleName);
}

</script>

<template>
  <div id="container"></div>
  <div id="search-panel"></div>
  <div id="drive-panel"></div>
  <div id="panel"></div>
  <div id="panel02"></div>
  <ToolBar @ChangeStyleTheme="handleChangeStyleTheme" @btnNavigation="btnNavigation" @reSet="reSet" @test="test" />

</template>

<style lang="less" scoped>
#container {
  height: 100%;
  height: calc(100% + 20px);
}

#search-panel {
  position: absolute;
  background-color: white;
  max-height: 90%;
  overflow-y: auto;
  top: 10px;
  right: 10px;
  width: 280px;
  // height: 300px;
}
</style>
