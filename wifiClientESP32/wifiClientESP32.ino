/*
	This is used to do my webscocket project

*/

#include <ArduinoWebsockets.h>
#include <WiFi.h>

const char* ssid = "yu68"; // Enter SSID
const char* password = "2869chen"; // Enter Password
const char* websockets_server_host = "192.168.100.157"; // Enter server address
const uint16_t websockets_server_port = 8080; // Enter server port

using namespace websockets;

WebsocketsClient client;

void setup() {
    Serial.begin(115200);
    connectToWiFi();
    connectToWebSocket();
    
    // Run callback when messages are received
    client.onMessage([&](WebsocketsMessage message){
        Serial.print("Received from server: ");
        Serial.println(message.data());
    });
}

void loop() {
    // Check for serial input and send to server
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

    // Let the websockets client check for incoming messages
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
        client.send("Hello Server, I am ESP32");
        Serial.println("Sent to server: Hello Server, I am ESP32");
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
            client.send("Hello Server, I am ESP32");
            Serial.println("Sent to server: Hello Server, I am ESP32");
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