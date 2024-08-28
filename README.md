# UnityVR_Esp32_IOT_pyServer

**UnityVR_Esp32_IOT_pyServer** is a project that facilitates communication between Unity-based VR applications, ESP32 IoT devices, and a Python WebSocket server over a local area network (LAN). This project is particularly suited for applications where multiple clients (such as VR devices and IoT sensors) need to communicate efficiently in real-time, including the ability to stream data.

## Usage

- **Running the System:** Start the Python WebSocket server, connect the Unity VR client, and then power up the ESP32 IoT device. The server will automatically manage connections and data streams.

- **Monitoring and Logging:** The Python WebSocket server includes a GUI for monitoring connected clients, viewing logs, and managing data streams.
- 
### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/UnityVR_Esp32_IOT_pyServer.git
    cd UnityVR_Esp32_IOT_pyServer
    ```

2. **Python WebSocket Server:**

    - Install required Python packages:

      ```bash
      pip install websockets tkinter
      ```

    - Run the server:

      ```bash
      python py_Server.py
      ```
## Features

- **Multi-Client Communication:** Seamless communication between Unity VR applications, ESP32 IoT devices, and a Python WebSocket server.
- **Data Streaming:** Capable of handling continuous data streams from IoT sensors to VR clients.
- **LAN-based Communication:** All communication is handled within a LAN, providing low-latency interactions suitable for real-time applications.
- **Extensible for IoT and VR:** The system is designed to work with various IoT devices and can be integrated into VR environments, making it highly versatile.

## Project Structure

### 1. Python WebSocket Server

- **Purpose:** Acts as the central hub for communication, managing connections between Unity VR clients and ESP32 IoT devices.
- **Functionality:**
  - Receives and processes messages from multiple clients.
  - Manages data streams, enabling continuous data exchange.
  - Broadcasts messages to all connected clients or directs them to specific ones.
  - Logs and displays connection status and messages through a GUI built with Tkinter.

### 2. Unity VR Client

- **Purpose:** Allows Unity-based VR applications to communicate with the WebSocket server, sending and receiving messages and streaming data.
- **Functionality:**
  - Connects to the WebSocket server and registers the client.
  - Sends messages to the server and receives broadcasted or directed messages.
  - Requests data streams from the server and updates the VR environment accordingly.

### 3. ESP32 IoT Client

- **Purpose:** Facilitates IoT devices, particularly those using the ESP32 microcontroller, to communicate with the WebSocket server.
- **Functionality:**
  - Sends sensor data to the server.
  - Can act as a data source in a streaming scenario, continuously feeding data to the server.
  - Receives and processes commands from the server, allowing real-time interaction with connected sensors or actuators.

## Getting Started

### Prerequisites

- **Python 3.x** with the necessary packages (`websockets`, `tkinter`, etc.).
- **Unity 2020.3.x** or higher with TextMeshPro and WebSocket support.
- **ESP32 Development Board** with Arduino IDE and necessary libraries for WebSocket and sensor integration.

3. **Unity Client:**

    - Import the provided Unity package into your project.
    - Set up the WebSocket connection using the provided scripts.

4. **ESP32 Client:**

    - Flash the ESP32 with the provided Arduino sketches.
    - Ensure the device is connected to the same network as the server.


## Contributing

Feel free to contribute to this project by submitting issues or pull requests. Contributions that enhance the functionality or extend compatibility with other devices and platforms are especially welcome.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
