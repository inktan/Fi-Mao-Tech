using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public class WebSocketClient
{
    private const string Uri = "ws://localhost:8088/";

    public static async Task Main(string[] args)
    {
        using (var ws = new ClientWebSocket())
        {
            await ws.ConnectAsync(new Uri(Uri), CancellationToken.None);
            Console.WriteLine("WebSocket 客户端已连接");

            string message = "Hello, WebSocket!";
            byte[] buffer = Encoding.UTF8.GetBytes(message);
            await ws.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);

            Console.WriteLine("发送消息：" + message);

            buffer = new byte[1024];
            var result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
            Console.WriteLine($"收到消息：{Encoding.UTF8.GetString(buffer, 0, result.Count)}");

            await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
        }
    }
}