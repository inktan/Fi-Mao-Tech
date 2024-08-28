// import request from "./request"
// import axios from "axios"

// 请填写您自己的APIKey
// const ZhipuAI_api_key = "6afaa8e936bc8982b107416a390216e3.sSW4FmE17ZKIVldh" //到期时间：2024-08-29
// const url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions';

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