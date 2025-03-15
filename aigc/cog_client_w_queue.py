import asyncio
import websockets
import json

async def receive_stream(streamer_enabled=True):
    """Connect to the server and handle queuing with position updates."""
    uri = "ws://10.1.30.250:8765"
    async with websockets.connect(
        uri,
        max_size=100 * 1024 * 1024,
        ping_timeout=300  # 5 minute timeout
    ) as websocket:
        try:
            # Phase 1: Queue position monitoring
            queue_position = None
            while True:
                message = await websocket.recv()
                
                if message.startswith("QUEUE_POSITION|"):
                    new_position = int(message.split("|")[1])
                    if queue_position != new_position:
                        queue_position = new_position
                        print(f"\rQueue position: {queue_position} | Waiting...", end="", flush=True)
                    
                    if queue_position == 1:
                        print("\nStarting processing...")
                        break
                        
                else:
                    print("\nUnexpected message:", message)
                    return

            # Phase 2: Send request data
            params = {
                "input_text": "Analyze the image solely based on its visual elements without adding personal interpretations. Focus on architectural features and keep your description concise within 100 words.",
                "temperature": 0.9,
                "top_p": 0.9,
                "top_k": 40,
                "streamer_enabled": streamer_enabled,
                "has_image": True
            }
            
            # Send metadata
            await websocket.send(json.dumps(params))
            
            # Send image data
            image_path = r"c:\Users\wang.tan.GOA\Pictures\a01.png"
            with open(image_path, "rb") as f:
                image_data = f.read()
                await websocket.send(image_data)

            # Phase 3: Receive responses
            if streamer_enabled:
                while True:
                    response = await websocket.recv()
                    if response == "END_OF_STREAM":
                        print("\nProcessing complete!")
                        break
                    print(response, end="", flush=True)
            else:
                response = await websocket.recv()
                if response.startswith("Error:"):
                    print(f"\n{response}")
                else:
                    print(response)

        except websockets.exceptions.ConnectionClosed as e:
            if e.code == 1000:
                print("\nConnection closed normally")
            else:
                print(f"\nConnection closed unexpectedly: {e}")
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(receive_stream(streamer_enabled=True))