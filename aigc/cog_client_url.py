import asyncio
import websockets
import json
import requests
import base64
from io import BytesIO
from PIL import Image
import asyncio
import websockets

async def receive_stream(streamer_enabled=True):
    uri = "ws://10.1.30.250:8765"
    async with websockets.connect(
        uri,
        max_size=100 * 1024 * 1024  # 100 MB limit
    ) as websocket:
        # Prepare parameters (no image bytes here)
        params = {
            "input_text": "Analyze the image...", 
            "temperature": 0.9,
            "top_p": 0.9,
            "top_k": 40,
            "streamer_enabled": streamer_enabled,
            "has_image": True  # Signal that image will follow
        }
        await websocket.send(json.dumps(params))  # Send metadata as JSON

        # Send raw image bytes in a separate binary message
        # 通过网址获取图片
        img_url = "http://10.1.12.30:5173\\static_1\\gooood\\Chongming Rice Culture Center Phase II, China by UD Design Studio - 谷德设计网\\59_069-chongming-rice-culture-center-phase-ii-china-by-ud-studio.jpeg"
        response = requests.get(img_url)
        response.raise_for_status()  # 如果请求失败，将抛出HTTPError异常
        proinfo_img = Image.open(BytesIO(response.content))
        image_bytes = BytesIO()
        proinfo_img.save(image_bytes, format=proinfo_img.format)
        image_bytes = image_bytes.getvalue()

        # 假设这是你的 WebSocket 地址
        async with websockets.connect(uri) as websocket:
            # 发送图片数据
            await websocket.send(image_bytes)
            print("Image data sent successfully.")

        if streamer_enabled:
            while True:
                try:
                    response = await websocket.recv()
                    if response == "END_OF_STREAM":
                        break
                    print(response, end="", flush=True)
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed unexpectedly")
                    break
        else:
            response = await websocket.recv()
            if response.startswith("Error:"):
                print(f"\n{response}")
            else:
                print(response)

if __name__ == "__main__":
    # Set streamer_enabled to False to receive the full response in one go
    asyncio.run(receive_stream(streamer_enabled=True))