using UnityEngine;
using NativeWebSocket;
using UnityEngine.UI;
using System.Text;

public class WebSocketClient : MonoBehaviour
{
    private WebSocket websocket;

    public InputField inputField;
    public Text logText;
    public Button connectButton;
    public Button disconnectButton;
    public Button sendButton;

    async void Start()
    {
        connectButton.onClick.AddListener(ConnectToWebSocket);
        disconnectButton.onClick.AddListener(DisconnectWebSocket);
        sendButton.onClick.AddListener(SendMessage);

        logText.text = "WebSocket Client Ready.\n";
    }

    async void ConnectToWebSocket()
    {
        websocket = new WebSocket("ws://192.168.100.157:8080/");

        websocket.OnOpen += () =>
        {
            Debug.Log("Connection open!");
            Log("Connection open!");
        };

        websocket.OnError += (e) =>
        {
            Debug.Log("Error! " + e);
            Log("Error: " + e);
        };

        websocket.OnClose += (e) =>
        {
            Debug.Log("Connection closed!");
            Log("Connection closed!");
        };

        websocket.OnMessage += (bytes) =>
        {
            var message = Encoding.UTF8.GetString(bytes);
            Debug.Log("OnMessage! " + message);
            Log("Received: " + message);
        };

        // Connect to the server
        await websocket.Connect();
    }

    async void DisconnectWebSocket()
    {
        if (websocket != null)
        {
            await websocket.Close();
            Log("Disconnected from WebSocket.");
        }
    }

    async void SendMessage()
    {
        if (websocket != null && websocket.State == WebSocketState.Open)
        {
            var message = inputField.text;
            await websocket.SendText(message);
            Log("Sent: " + message);
        }
    }

    void Log(string message)
    {
        logText.text += message + "\n";
    }

    void Update()
    {
        if (websocket != null)
        {
            #if !UNITY_WEBGL || UNITY_EDITOR
                websocket.DispatchMessageQueue();
            #endif
        }
    }

    private async void OnApplicationQuit()
    {
        if (websocket != null)
        {
            await websocket.Close();
        }
    }
}
