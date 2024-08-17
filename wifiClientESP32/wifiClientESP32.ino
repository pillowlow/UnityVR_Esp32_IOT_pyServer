/*
	This is used to do my webscocket project

*/


#include <ArduinoWebsockets.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <stdlib.h> // For random number generation

using namespace websockets;

const char* ssid = "yu68"; // Enter SSID
const char* password = "2869chen"; // Enter Password
const char* websockets_server_host = "192.168.100.157"; // Enter server address
const uint16_t websockets_server_port = 8080; // Enter server port

WebsocketsClient client;

const char* client_id = "ESP32Client1"; // The ID of this ESP32 client

const char* stream_name = "esp32Stream1"; // Stream name
bool stream_active = false;
String current_stream_mode = "testing_data"; // Default to sensor data mode
float stream_resolution = 100;  // Default stream data resolution 

void setup() {
    Serial.begin(115200);
    connectToWiFi();
    connectToWebSocket();
    
    client.onMessage([&](WebsocketsMessage message){
    Serial.print("Received from server: ");
    Serial.println(message.data());

    // Attempt to parse the message as JSON
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, message.data());

    if (error) {
        Serial.println("Failed to parse message as JSON:");
        Serial.println(message.data());  // Log the raw message for debugging
        return;
    }

    String command = doc["command"];

    if (command == "REQUEST_ID") {
          sendClientID();
      } else if (command == "SERVER_CLOSING") {
          Serial.println("Server is closing, disconnecting...");
          client.close();
      } else if (command == "broadcast") {
          String broadcast_message = doc["data"];
          Serial.print("Broadcast message from server: ");
          Serial.println(broadcast_message);
      } else if (command == "message"){
          String message = doc["data"];
          Serial.print("Recieve message: ");
          Serial.println(message);
      } else {
          Serial.println("Unknown command received:");
          serializeJsonPretty(doc, Serial);
      }
    });


    randomSeed(analogRead(0)); // Initialize random number generator
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
            startStream(stream_name,current_stream_mode);
            stream_active = true;
        } else if (input == "close stream") {
            closeStream(current_stream_mode);
            stream_active = false;
        } else if (input == "switch to sensor mode") {
            current_stream_mode = "sensor_data";
            Serial.println("Switched to sensor mode.");
        } else if (input == "switch to testing mode") {
            current_stream_mode = "testing_data";
            Serial.println("Switched to testing mode.");
        } else {
        // Create a JSON object to send
        StaticJsonDocument<200> jsonDoc;
        jsonDoc["command"] = "message";
        jsonDoc["data"] = input;

        // Serialize the JSON document to a string
        String jsonString;
        serializeJson(jsonDoc, jsonString);

        // Send the JSON string
        client.send(jsonString.c_str());

        Serial.print("Sent to server: ");
        Serial.println(jsonString);
      }
    }
    if(stream_active == true){
      sendStreamData(stream_name,current_stream_mode);
    }

    client.poll();
    delay(stream_resolution);
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
    Serial.println("send ID to server");
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

void startStream(const String& stream_name, const String& stream_mode) {
    StaticJsonDocument<200> doc;
    doc["command"] = "start_stream";
    doc["stream_name"] = stream_name;
    doc["client_id"] = client_id;

    String jsonString;
    serializeJson(doc, jsonString);
    client.send(jsonString);

    Serial.println("Started stream " + stream_name);
}

void sendStreamData(const String& stream_name , const String& stream_mode) {
    String data;
    if (stream_mode == "sensor_data") {
        data = getSensorData();  // Placeholder for real sensor data
    } else if (stream_mode == "testing_data") {
        data = String(random(1, 1000) / 100.0, 2); // Random float between 1.00 and 10.00
    }

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

String getSensorData() {
    // Placeholder for real sensor data acquisition
    // Replace this with actual sensor data reading code
    return String(analogRead(0)); // Example sensor data
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
