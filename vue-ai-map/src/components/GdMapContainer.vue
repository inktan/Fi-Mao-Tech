<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader';
import ToolBar from '@/components/ToolBar.vue'

// import HelloWorld from './components/HelloWorld.vue'
import { web_frontend_key, web_frontend_secret_key } from "@/gd_map_config.js";
import { shanghai, suzhou, wuxi } from "@/data/shanghai.js";

// console.log(`key_web_js:${key_web_js}`)
const styleTheme = ref('dark')
let map = null;
let aMap = null;

onMounted(() => {
  window._AMapSecurityConfig = {
    securityJsCode: web_frontend_secret_key,
    // serviceHost: "http://39.98.218.136:8801/_AMapService",
  };

  AMapLoader.load({
    key: web_frontend_key, // 申请好的Web端开发者Key，首次调用 load 时必填
    version: "2.0", // 指定要加载的 JSAPI 的版本，缺省时默认为 1.4.15
    // plugins
    // "AMap.Scale" 比例尺
    // 'AMap.ToolBar' 放大 缩小控件
    // "AMap.PlaceSearch" 地点搜索
    // "AMap.Driving" 驾车导航
    // "AMap.Transfer" 公交导航
    // "AMap.Walking" 步行路导航
    // "AMap.Riding" 骑行导航
    // "AMap.TruckDriving" 货车导航】
    plugins: ["AMap.Scale", 'AMap.ToolBar', "AMap.PlaceSearch", "AMap.Driving", "AMap.Transfer", "AMap.Walking", "AMap.Riding", "AMap.TruckDriving"], //需要使用的的插件列表，如比例尺'AMap.Scale'，支持添加多个如：['...','...']
  }).then((AMap) => {
    aMap = AMap;

    const layer = new AMap.createDefaultLayer({
      zooms: [3, 20], //可见级别
      visible: true, //是否可见
      opacity: 1, //透明度
      zIndex: 0, //叠加层级
    });

    map = new AMap.Map("container", {
      rotateEnable: false,
      pitchEnable: true,
      viewMode: "2D", // 是否为3D地图模式
      zoom: 16, // 初始化地图级别
      // center: [116.397428, 39.90923], // 初始化地图中心点位置-北京
      center: [120.629029, 31.32416], // 初始化地图中心点位置-苏州拙政园
      mapStyle: `amap://styles/${styleTheme.value}`, //设置地图的显示样式
      layers: [layer], //layer为创建的默认图层
    });

    var toolbar = new AMap.Scale(
      {
        position: {
          right: '10px',
          bottom: '25px'
        }
      }); //缩放工具条实例化
    map.addControl(toolbar); //添加控件

    // 驾车导航
    // const driving = new AMap.Driving({
    //   map: map, //展现结果的地图实例
    //   panel: "drive-panel",
    // 公交导航
    const driving = new AMap.Transfer({
      map: map, //展现结果的地图实例
      panel: "drive-panel",
    })
    // 步行路导航
    // const driving = new AMap.Walking({
    //   map: map, //展现结果的地图实例
    //   panel: "drive-panel",
    // })
    // 骑行导航
    // const driving = new AMap.Riding({
    //   map: map, //展现结果的地图实例
    //   panel: "drive-panel",
    // })

    const points = [
      { keyword: '拙政园', city: '苏州' },
      { keyword: '留园', city: '苏州' },
      { keyword: '平江历史街区', city: '苏州' },
      { keyword: '苏州博物馆', city: '苏州' },
    ]
    //获取起终点规划线路
    driving.search(points, function (status, result) {
      if (status === "complete") {
        //status：complete 表示查询成功，no_data 为查询无结果，error 代表查询错误
        //查询成功时，result 即为对应的驾车导航信息
        console.log(result);
        // 如何展示导航的文字信息
      } else {
        console.log("获取驾车数据失败：" + result);
      }
    });

  }).catch((e) => {
    console.log(e);
  });
});

onUnmounted(() => {
  map?.destroy();
});

function addPolygon(data) {
  let polygon = new aMap.Polygon({
    path: data,
    fillColor: '#ccebc5',
    strokeOpacity: 1,
    fillOpacity: 0.5,
    strokeColor: '#2b8cbe',
    strokeWeight: 1,
    strokeStyle: 'dashed',
    strokeDasharray: [5, 5],
  });
  polygon.on('mouseover', () => {
    polygon.setOptions({
      fillOpacity: 0.7,
      fillColor: '#7bccc4'
    })
  })
  polygon.on('mouseout', () => {
    polygon.setOptions({
      fillOpacity: 0.5,
      fillColor: '#ccebc5'

    })
  })
  map.add(polygon);
}

//在指定位置打开信息窗体
function openInfo() {
  //构建信息窗体中显示的内容
  var info = [];
  info.push("<div>");
  info.push("<img style=\"height: 0.8rem;\" src=\" https://webapi.amap.com/images/autonavi.png \"/>");
  info.push("<p style=\"line-height: 2rem;font-size: 12px;height: 2rem;\">中文名 : 拙政园</p>");
  info.push("<p style=\"line-height: 1rem;font-size: 12px;height: 1rem;\">地址 :江苏省苏州市姑苏区东北街178号</p>");
  info.push("</div>");

  const infoWindow = new aMap.InfoWindow({
    content: info.join(""), //使用默认信息窗体框样式，显示信息内容
    // isCustom: false,
    // size: new aMap.Size(200, 200)
  });

  infoWindow.open(map, [120.629029, 31.32416]);
}

// let styleIndex = 0;

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
  <!-- <ToolBar @ChangeStyleTheme="handleChangeStyleTheme" /> -->

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
