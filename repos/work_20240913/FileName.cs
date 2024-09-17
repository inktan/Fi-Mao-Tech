using System;
using System.Net;
using System.Net.WebSockets;
using System.Threading;
using System.Threading.Tasks;

public class WebSocketServer
{
    private const int Port = 8088;

    public static async Task Main(string[] args)
    {
        string ipAddress = "0.0.0.0";

        var httpListener = new HttpListener();
        httpListener.Prefixes.Add($"http://{ipAddress}:{Port}/");
        httpListener.Start();
        Console.WriteLine("WebSocket 服务器启动，监听端口：" + Port);

        while (true)
        {
            var context = await httpListener.GetContextAsync();
            if (context.Request.IsWebSocketRequest)
            {
                ProcessRequest(context);
            }
            else
            {
                context.Response.StatusCode = 400;
                context.Response.Close();
            }
        }
    }

    private static async void ProcessRequest(HttpListenerContext context)
    {
        WebSocketContext wsContext;
        try
        {
            wsContext = await context.AcceptWebSocketAsync(subProtocol: null);
        }
        catch (Exception ex)
        {
            context.Response.StatusCode = 500;
            context.Response.Close();
            Console.WriteLine($"无法建立 WebSocket 连接：{ex}");
            return;
        }

        WebSocket webSocket = wsContext.WebSocket;
        try
        {
            byte[] buffer = new byte[1024];
            while (webSocket.State == WebSocketState.Open)
            {
                var result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
                if (result.MessageType == WebSocketMessageType.Text)
                {
                    Console.WriteLine($"收到消息：{System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count)}");
                    await webSocket.SendAsync(new ArraySegment<byte>(buffer, 0, result.Count), WebSocketMessageType.Text, true, CancellationToken.None);
                }
                else if (result.MessageType == WebSocketMessageType.Close)
                {
                    await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
                }
            }
        }
        catch (Exception ex)
        {
            if (webSocket.State == WebSocketState.Open)
            {
                await webSocket.CloseAsync(WebSocketCloseStatus.InternalServerError, "内部服务器错误", CancellationToken.None);
            }
            Console.WriteLine($"WebSocket 连接异常：{ex}");
        }
    }
}