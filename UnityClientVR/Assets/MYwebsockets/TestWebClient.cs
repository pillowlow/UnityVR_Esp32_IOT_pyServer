using UnityEngine;
using NativeWebSocket;
using TMPro;
using UnityEngine.UI;
using System.Text;

public class WebSocketClient : MonoBehaviour
{
    private WebSocket websocket;
    public string clientId = "UnityClient1"; // The ID that the client will send to the server
    public TMP_InputField inputField; 
    public TextMeshProUGUI logText; 
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
        Log("Attempting to connect...");

        websocket = new WebSocket("ws://192.168.100.157:8080/");

        websocket.OnOpen += async () =>
        {
            Debug.Log("Connection open!");
            Log("Connection open!");

            // Send client ID to the server
            await websocket.SendText(clientId);
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

        await websocket.Connect();
    }

    async void DisconnectWebSocket()
    {
        Log("Disconnecting...");
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
        else
        {
            Log("WebSocket is not connected.");
        }
    }

    void Log(string message)
    {
        Debug.Log("Log: " + message);

        if (logText != null)
        {
            // Add the new message to the log
            logText.text += message + "\n";

            // Split the log into lines
            string[] lines = logText.text.Split(new[] { '\n' }, System.StringSplitOptions.RemoveEmptyEntries);

            // If the number of lines exceeds 6, remove the oldest line
            if (lines.Length > 6)
            {
                logText.text = string.Join("\n", lines, 1, lines.Length - 1) + "\n";
            }

            // Force TextMeshPro to update the text
            logText.ForceMeshUpdate();
        }
        else
        {
            Debug.LogError("logText is null. Make sure it is assigned in the Inspector.");
        }
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
