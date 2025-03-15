import asyncio
import websockets
import json

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
        image_path = r"c:\Users\wang.tan.GOA\Pictures\企业微信截图_17013329909043.png"
        with open(image_path, "rb") as f:
            await websocket.send(f.read())  # Binary frame

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