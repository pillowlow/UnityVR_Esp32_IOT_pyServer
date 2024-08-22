# py_iot_unity Server

## Overview

The `py_iot_unity` server is a Python-based WebSocket server designed to facilitate communication between multiple clients, including Unity applications, ESP32 devices, and Python scripts. The server supports message passing and data streaming across clients through a local area network (LAN), making it suitable for various IoT applications, including VR environments.

## Features

- **Multi-Client Communication:** Supports simultaneous connections with Unity clients, ESP32 devices, and other Python clients.
- **Message Passing:** Send and receive messages between clients, allowing real-time communication and control.
- **Data Streaming:** Stream continuous data (e.g., sensor data) from one client to another, with the ability to handle multiple streams simultaneously.
- **LAN Support:** Operates over a local area network, making it ideal for home automation, IoT projects, and VR applications.
- **VR Compatibility:** Specifically designed to work in VR environments, enabling real-time data exchange in immersive applications.

## Getting Started

### Prerequisites

- Python 3.x
- Unity 2019.4 or later (for Unity clients)
- ESP32 development board
- LAN with access to all client devices

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/py_iot_unity.git
   cd py_iot_unity
