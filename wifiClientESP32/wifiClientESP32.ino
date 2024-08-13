/*
	This is used to do my webscocket project

*/

#include <ArduinoWebsockets.h>
#include <WiFi.h>

const char* ssid = "yu68"; // Enter your WIFI SSID
const char* password = "2869chen"; // Enter your Password
const char* websockets_server_host = "192.168.100.157"; // Enter server address
const uint16_t websockets_server_port = 8080; // Enter server port

const char* client_id = "ESP32Client1"; // The ID that this client will send to the server

using namespace websockets;

WebsocketsClient client;

void setup() {
    Serial.begin(115200);
    connectToWiFi();
    connectToWebSocket();
    
    client.onMessage([&](WebsocketsMessage message){
      String receivedMessage = message.data();
      Serial.print("Received from server: ");
      Serial.println(receivedMessage);

      // Check if the message indicates the server is closing
      if (receivedMessage == "SERVER_CLOSING") {
          Serial.println("Server is closing, disconnecting...");
          client.close(1000, "Normal closure"); ;  // Properly close the connection
          delay(1000);     // Add a delay to ensure the close frame is sent
          ESP.restart();   // Restart the ESP32 to ensure a clean disconnection
    }
});
}

void loop() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');

        if (input == "restart") {
            restartESP();
        } else if (input == "reconnect") {
            reconnectWebSocket();
        } else if (input == "disconnect") {
            disconnect();
            
        } else {
            client.send(input.c_str());
            Serial.print("Sent to server: ");
            Serial.println(input);
        }
    }

    client.poll();
    delay(500);
}

void connectToWiFi() {
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println();
    Serial.println("Connected to WiFi");
    Serial.println(WiFi.SSID());
}

void connectToWebSocket() {
    Serial.println("Trying to connect to server");
    bool connected = client.connect(websockets_server_host, websockets_server_port, "/");
    if (connected) {
        Serial.println("Connected to WebSocket!");
        client.send(client_id);  // Send client ID to the server
        Serial.println("Sent client ID to server");
    } else {
        Serial.println("Failed to connect to WebSocket!");
        reconnectWebSocket();
    }
}

void reconnectWebSocket() {
    Serial.println("Attempting to reconnect to WebSocket...");
    while (!client.available()) {
        if (client.connect(websockets_server_host, websockets_server_port, "/")) {
            Serial.println("Reconnected to WebSocket!");
            client.send(client_id);  // Send client ID to the server
            Serial.println("Sent client ID to server");
            break;
        }
        Serial.println("Reconnection attempt failed. Retrying...");
        delay(5000); // Wait before retrying
    }
}

void disconnect() {
    client.close();
    Serial.println("Connection closed");
}

void restartESP() {
    Serial.println("Restarting ESP32...");
    delay(1000);
    ESP.restart();
}
