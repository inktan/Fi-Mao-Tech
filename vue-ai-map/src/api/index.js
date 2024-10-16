// import request from "./request"
// import axios from "axios"

// 请填写您自己的APIKey
// const ZhipuAI_api_key = "6afaa8e936bc8982b107416a390216e3.sSW4FmE17ZKIVldh" //到期时间：2024-08-29
// const url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions';
import { wdbeb_service_key } from "@/gd_map_config.js";

// Ai对话
// erroe axios 不支持流式传输
export async function postZhiPuAiChat(messageList) {
    // const get_url = `http://10.1.12.30:5002/ai_chat`
    const get_url = `http://110.40.230.188:8001/ai_chat`

    const data = {
        // "model": "glm-4",
        "messages": messageList,
        // stream: true,
    }
    return await fetch(get_url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // 'Authorization': `Bearer ${ZhipuAI_api_key}`
        },
        body: JSON.stringify(data),
    });
}

// 地理编码：将详细的结构化地址转换为高德经纬度坐标
export async function addressToLonLat(address) {
    let queryParams = {
        address: address,
        key: wdbeb_service_key
    };
    let queryString = new URLSearchParams(queryParams).toString();
    const url = `https://restapi.amap.com/v3/geocode/geo?${queryString}`
    return await fetch(url)
}

// 逆地理编码：将经纬度转换为详细结构化的地址
export async function lonLatToAddress(lon,lat) {
    let queryParams = {
        location: `${lon},${lat}`,
        key: wdbeb_service_key
    };
    let queryString = new URLSearchParams(queryParams).toString();
    const url = `https://restapi.amap.com/v3/geocode/regeo?${queryString}`
    return await fetch(url)

}

// 天气查询
export async function getAmapWeatherInfo() {
    let queryParams = {
        city: `320505`,
        key: wdbeb_service_key
    };
    let queryString = new URLSearchParams(queryParams).toString();
    const url = `https://restapi.amap.com/v3/weather/weatherInfo?${queryString}`
    return await fetch(url)

}

