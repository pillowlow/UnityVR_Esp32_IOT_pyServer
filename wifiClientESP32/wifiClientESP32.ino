/*
	This is used to do my webscocket project

*/


#include <ArduinoWebsockets.h>
#include <WiFi.h>
#include <ArduinoJson.h>

using namespace websockets;

const char* ssid = "yu68"; // Enter SSID
const char* password = "2869chen"; // Enter Password
const char* websockets_server_host = "192.168.100.157"; // Enter server address
const uint16_t websockets_server_port = 8080; // Enter server port

WebsocketsClient client;

const char* client_id = "ESP32Client1"; // The ID of this ESP32 client

void setup() {
    Serial.begin(115200);
    connectToWiFi();
    connectToWebSocket();
    
    client.onMessage([&](WebsocketsMessage message){
        Serial.print("Received from server: ");
        Serial.println(message.data());
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
        } else if (input.startsWith("send ")) {
            String target_id = input.substring(5, input.indexOf(' ', 5));
            String message = input.substring(input.indexOf(' ', 5) + 1);
            sendMessageToClient(target_id, message);
        } else if (input == "start stream") {
            startStream("sensor_data");
        } else if (input == "send stream") {
            sendStreamData("sensor_data", "example_data");
        } else if (input == "close stream") {
            closeStream("sensor_data");
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
        sendClientID();
    } else {
        Serial.println("Failed to connect to WebSocket!");
    }
}

void sendClientID() {
    StaticJsonDocument<200> doc;
    doc["command"] = "client_id";
    doc["client_id"] = client_id;

    String jsonString;
    serializeJson(doc, jsonString);
    client.send(jsonString);
}

void sendMessageToClient(const String& target_id, const String& message) {
    StaticJsonDocument<200> doc;
    doc["command"] = "send_to_client";
    doc["target_id"] = target_id;
    doc["client_id"] = client_id;
    doc["data"] = message;

    String jsonString;
    serializeJson(doc, jsonString);
    client.send(jsonString);

    Serial.println("Message sent to client " + target_id);
}

void startStream(const String& stream_name) {
    StaticJsonDocument<200> doc;
    doc["command"] = "start_stream";
    doc["stream_name"] = stream_name;
    doc["client_id"] = client_id;

    String jsonString;
    serializeJson(doc, jsonString);
    client.send(jsonString);

    Serial.println("Started stream " + stream_name);
}

void sendStreamData(const String& stream_name, const String& data) {
    StaticJsonDocument<200> doc;
    doc["command"] = "stream_data";
    doc["stream_name"] = stream_name;
    doc["client_id"] = client_id;
    doc["data"] = data;

    String jsonString;
    serializeJson(doc, jsonString);
    client.send(jsonString);

    Serial.println("Sent stream data for " + stream_name + ": " + data);
}

void closeStream(const String& stream_name) {
    StaticJsonDocument<200> doc;
    doc["command"] = "close_stream";
    doc["stream_name"] = stream_name;
    doc["client_id"] = client_id;

    String jsonString;
    serializeJson(doc, jsonString);
    client.send(jsonString);

    Serial.println("Closed stream " + stream_name);
}

void restartESP() {
    Serial.println("Restarting ESP32...");
    delay(1000);
    ESP.restart();
}

void reconnectWebSocket() {
    Serial.println("Reconnecting to WebSocket...");
    client.close();
    connectToWebSocket();
}

void disconnect() {
    Serial.println("Disconnecting from WebSocket...");
    client.close();
}
