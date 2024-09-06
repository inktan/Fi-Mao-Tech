<script setup>
import { web_frontend_key, web_frontend_secret_key } from "@/gd_map_config.js";
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { getAmapWeatherInfo } from "@/api";

const weatherData = ref({})
const nowTime = ref(new Date());

const localTime = computed(() => {
    return nowTime.value.toLocaleTimeString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
})

let timer;
onMounted(() => {
    timer = setInterval(() => {
        nowTime.value = new Date()
    }, 1000);
    getWeatherInfo()
});

const getWeatherInfo = async function () {
    let resp = await getAmapWeatherInfo()
    let jsonData = await resp.json()
    console.log(jsonData)
    weatherData.value = jsonData.lives[0]
}

onUnmounted(() => {
    clearInterval(timer);
});

</script>

<template>
    <div class="container">
        <div class="nav">
            <div class="time">
                {{ localTime }}
            </div>
            <!-- <div class="city">
                苏州市
            </div> -->
        </div>
        <div class="city-info">
            <div class="city-name">苏州市 {{ weatherData.city }}</div>
            <div class="weather">{{ weatherData.weather }}</div>
            <div class="temp">
                <em>{{ weatherData.temperature }}</em>℃
            </div>
            <div class="detail">
                风力:{{ weatherData.windpower }}
                |
                风向:{{ weatherData.winddirection }}
                |
                空气湿度:{{ weatherData.humidity }}%
            </div>
        </div>
    </div>
</template>

<style lang="less" scoped>
.container {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 10000;
    background-color: rgba(128, 128, 128, 0.83);
    border-radius: 10px;
    padding: 5px;
    color: white;
    font-size: 12px;

    div {
        margin: 5px;
    }

    .nav {
        height: 20px;

        .time {
            float: left;
        }

        .city {
            float: right;
        }
    }

    .city-info {
        text-align: center;

        .temp {
            font-size: 18px;
        }
    }
}
</style>
