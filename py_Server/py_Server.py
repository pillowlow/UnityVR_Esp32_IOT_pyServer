import asyncio
import websockets
import logging
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import json



logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

clients = {}  # Dictionary to store client ID and WebSocket pairs
streams = {}  # Dictionary to store active streams and their current values

class WebSocketServer:
    def __init__(self,app):
        
        self.app = app  # Reference to the ServerApp instance
        self.server = None
        self.loop = None
        self.should_stop = False
        self.log_text_widget = None  # Add a reference to the log widget

    async def register(self, websocket):
        await websocket.send(json.dumps({"command": "REQUEST_ID"}))
        try:
            message = await websocket.recv()
            data = json.loads(message)
            client_id = data.get("client_id")

            if client_id:
                clients[client_id] = websocket
                self.app.log_message(f"New client connected: ID {client_id}")
                self.app.add_client(client_id)  # Update the client list in the GUI
                await self.listen_to_client(client_id, websocket)

        except websockets.ConnectionClosed as e:
            self.app.log_message(f"Connection closed: {e}")
        except Exception as e:
            self.app.log_message(f"Error: {e}")
        finally:
            if client_id in clients:
                clients.pop(client_id)
                self.app.log_message(f"Client disconnected: ID {client_id}")
                self.app.remove_client(client_id)

    async def listen_to_client(self, client_id, websocket):
        try:
            async for message in websocket:
                logging.info(f"Received message from ID {client_id}: {message}")
                self.app.log_message(f"Received message from ID {client_id}: {message}")
                data = json.loads(message)
                await self.handle_message(client_id, data)
        except websockets.ConnectionClosed as e:
            logging.warning(f"Connection closed: {e}")
            self.app.log_message(f"Connection closed: {e}")
        except Exception as e:
            logging.error(f"Error: {e}")
            self.app.log_message(f"Error: {e}")

    async def handle_message(self, client_id, data):
        command = data.get("command")

        if command == "send_to_client":
            target_id = data.get("target_id")
            target_client = clients.get(target_id)
            if target_client:
                await target_client.send(json.dumps(data))
                log_message = f"Message from {client_id} sent to {target_id}"
                logging.info(log_message)
                self.app.log_message(log_message)
            else:
                log_message = f"Client {target_id} not found."
                logging.warning(log_message)
                self.app.log_message(log_message)

        elif command == "start_stream":
            
            # Start a new stream and refresh the dropdown menu
            stream_name = data.get("stream_name")
            streams[stream_name] = None  # Initialize the stream with no data
            self.app.refresh_stream_dropdown() # Refresh the stream dropdown in the UI
            log_message = f"Stream '{stream_name}' started by {client_id}"
            logging.info(log_message)
            self.app.log_message(log_message)

        elif command == "stream_data":
             # Update stream data and refresh the stream display if this stream is selected
            stream_name = data.get("stream_name")
            stream_data = data.get("data")
            streams[stream_name] = stream_data
            self.app.log_message(f"Received stream data for '{stream_name}' from {client_id}: {stream_data}")

            # If the currently selected stream is the one that just got updated, refresh the display
            if self.app.stream_dropdown.get() == stream_name:
                self.app.update_stream_display(stream_name)
                

        elif command == "request_stream_data":
            stream_name = data.get("stream_name")
            if stream_name in streams:
                current_data = streams.get(stream_name)
                response = {
                    "command": "stream_data",
                    "stream_name": stream_name,
                    "data": current_data
                }
                await clients[client_id].send(json.dumps(response))
                log_message = f"Sent current stream data for '{stream_name}' to {client_id}"
                logging.info(log_message)
                self.app.log_message(log_message)
            else:
                log_message = f"Stream '{stream_name}' not found."
                logging.warning(log_message)
                self.app.log_message(log_message)

        elif command == "close_stream":
            stream_name = data.get("stream_name")
            if stream_name in streams:
                streams.pop(stream_name, None)
                log_message = f"Stream '{stream_name}' closed by {client_id}"
                logging.info(log_message)
                self.app.log_message(log_message)

        elif command == "broadcast":
            broadcast_message = data.get("data")
            await self.broadcast_message(broadcast_message, exclude_client=client_id)
            log_message = f"Broadcast message: {broadcast_message}"
            logging.info(log_message)
            self.app.log_message(log_message)

        elif command == "client_id":
            log_message = f"Received client_id command from {client_id}: {data.get('client_id')}"
            logging.info(log_message)
            self.app.log_message(log_message)

        else:
            log_message = f"Unknown command from {client_id}: {command}"
            logging.warning(log_message)
            self.app.log_message(log_message)
    
    async def send_to_client(self, client_id, message):
        """Send a message to a specific client by ID."""
        client = clients.get(client_id)
        if client:
            await client.send(json.dumps({"command": "message", "data": message}))
            log_message = f"Sent message to {client_id}: {message}"
            self.app.log_message(log_message)
        else:
            log_message = f"Client {client_id} not found."
            self.app.log_message(log_message)
        

    async def broadcast_message(self, message, exclude_client=None):
        for cid, websocket in clients.items():
            if cid != exclude_client:
                await websocket.send(json.dumps({
                    "command": "broadcast",
                    "data": message
                }))
        logging.info(f"Broadcasted message: {message}")
        self.app.log_message(f"Broadcasted message: {message}")

    async def main(self):
        logging.info("Server started, waiting for clients to connect...")
        self.app.log_message("Server started, waiting for clients to connect...")
        self.server = await websockets.serve(self.register, "0.0.0.0", 8080)
        try:
            while not self.should_stop:
                await asyncio.sleep(1)
        finally:
            logging.info("Server stopping, disconnecting all clients...")
            self.app.log_message("Server stopping, disconnecting all clients...")
            await self.disconnect_all_clients()
            self.server.close()
            await self.server.wait_closed()
            logging.info("Server has been stopped.")
            self.app.log_message("Server has been stopped.")

    async def disconnect_all_clients(self):
        if clients:
            logging.info("Disconnecting all clients...")
            self.app.log_message("Disconnecting all clients...")
            disconnect_tasks = []
            for client_id, websocket in list(clients.items()):
                await websocket.send(json.dumps({"command": "SERVER_CLOSING"}))
                disconnect_tasks.append(websocket.close())
            await asyncio.gather(*disconnect_tasks)
            clients.clear()
            logging.info("All clients have been disconnected.")
            self.app.log_message("All clients have been disconnected.")

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.should_stop = False
        try:
            self.loop.run_until_complete(self.main())
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def stop(self):
        self.should_stop = True
        if self.server is not None:
            asyncio.run_coroutine_threadsafe(self.disconnect_all_clients(), self.loop).result()
            self.server.close()
            
    

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebSocket Server")

        # Create an instance of WebSocketServer and pass `self` (ServerApp instance) to it
        self.websocket_server = WebSocketServer(self)

        # Main frame that holds all the components
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top controls frame (Start, Stop, Select Stream)
        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.start_button = tk.Button(self.top_frame, text="Start", command=self.start_server)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.top_frame, text="Stop", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        self.stream_label = tk.Label(self.top_frame, text="Select Stream")
        self.stream_label.pack(side=tk.LEFT, padx=10)

        self.stream_dropdown = tk.StringVar(self.top_frame)
        self.stream_dropdown.set("Select Stream")  # Default value
        self.stream_menu = tk.OptionMenu(self.top_frame, self.stream_dropdown, "Select Stream", *streams.keys(), command=self.update_stream_display)
        self.stream_menu.pack(side=tk.LEFT)

        # Bottom frame for Broadcast and Select Client Input Bars
        self.bottom_frame = tk.Frame(self.main_frame)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.broadcast_label = tk.Label(self.bottom_frame, text="Broadcast:")
        self.broadcast_label.pack(side=tk.LEFT, padx=5)

        self.broadcast_entry = tk.Entry(self.bottom_frame)
        self.broadcast_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.broadcast_entry.bind('<Return>', self.broadcast_message)

        # Select Client and Message Input area
        self.select_client_frame = tk.Frame(self.bottom_frame)
        self.select_client_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        self.select_clients_dropdown = tk.StringVar(self.select_client_frame)
        self.select_clients_dropdown.set("Select Client")  # Default value
        self.select_clients_menu = tk.OptionMenu(self.select_client_frame, self.select_clients_dropdown, "Select Client", *clients.keys())
        self.select_clients_menu.pack(side=tk.LEFT, padx=5)

        self.client_message_entry = tk.Entry(self.select_client_frame)
        self.client_message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.client_message_entry.bind('<Return>', self.send_to_selected_client)

        # Middle frame for logs and client list
        self.middle_frame = tk.Frame(self.main_frame)
        self.middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Server log frame with 2/3 width
        self.server_log_frame = tk.Frame(self.middle_frame, width=(self.main_frame.winfo_width() * 2 // 3))
        self.server_log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Stream log and client list frame with 1/3 width each
        self.side_frame = tk.Frame(self.middle_frame, width=(self.main_frame.winfo_width() // 3))
        self.side_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.stream_log_frame = tk.Frame(self.side_frame)
        self.stream_log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.clients_frame = tk.Frame(self.side_frame)
        self.clients_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Server log
        self.log_label = tk.Label(self.server_log_frame, text="Server Log")
        self.log_label.pack()

        self.log_text = scrolledtext.ScrolledText(self.server_log_frame, state='disabled', height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Stream data log
        self.stream_data_label = tk.Label(self.stream_log_frame, text="Stream Data Log")
        self.stream_data_label.pack()

        self.stream_data_display = scrolledtext.ScrolledText(self.stream_log_frame, state='disabled', height=20, wrap=tk.WORD)
        self.stream_data_display.pack(fill=tk.BOTH, expand=True)

        # Connected clients list
        self.clients_label = tk.Label(self.clients_frame, text="Connected Clients")
        self.clients_label.pack()

        self.clients_list = scrolledtext.ScrolledText(self.clients_frame, state='disabled', height=20)
        self.clients_list.pack(fill=tk.BOTH, expand=True)

        # Resend toggle button at the bottom-right
        self.resend_button = tk.Button(self.bottom_frame, text="Disable Resend", command=self.toggle_resend)
        self.resend_button.pack(side=tk.RIGHT, padx=10)

    def start_server(self):
        self.server_thread = Thread(target=self.websocket_server.start)
        self.server_thread.start()
        self.log_message("Server starting...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_server(self):
        self.websocket_server.stop()
        self.server_thread.join()
        self.log_message("Server stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)

    def add_client(self, client_id):
        self.clients_list.config(state='normal')
        self.clients_list.insert(tk.END, f"Client ID {client_id}\n")
        self.clients_list.config(state='disabled')
        self.clients_list.yview(tk.END)
        self.refresh_client_dropdown()

    def remove_client(self, client_id):
        self.clients_list.config(state='normal')
        clients = self.clients_list.get("1.0", tk.END).splitlines()
        self.clients_list.delete("1.0", tk.END)
        for client in clients:
            if client != f"Client ID {client_id}":
                self.clients_list.insert(tk.END, client + "\n")
        self.clients_list.config(state='disabled')
        self.refresh_client_dropdown()

    def refresh_client_dropdown(self):
        menu = self.select_clients_menu["menu"]
        menu.delete(0, "end")
        for client_id in clients.keys():
            menu.add_command(label=client_id, command=lambda value=client_id: self.select_clients_dropdown.set(value))

    def broadcast_message(self, event=None):
        message = self.broadcast_entry.get()
        if message:
            asyncio.run_coroutine_threadsafe(self.websocket_server.broadcast_message(message), self.websocket_server.loop)
            self.log_message(f"Broadcasting message: {message}")
            self.broadcast_entry.delete(0, tk.END)

    def send_to_selected_client(self, event=None):
        selected_client = self.select_clients_dropdown.get()
        message = self.client_message_entry.get()
        if selected_client != "Select Client" and message:
            asyncio.run_coroutine_threadsafe(self.websocket_server.send_to_client(selected_client, message), self.websocket_server.loop)
            self.log_message(f"Sent to {selected_client}: {message}")
            self.client_message_entry.delete(0, tk.END)

    def update_stream_display(self, selected_stream):
        if selected_stream in streams:
            current_data = streams[selected_stream]
            self.stream_data_display.config(state='normal')
            self.stream_data_display.insert(tk.END, f"{current_data}\n")
            self.stream_data_display.config(state='disabled')
            self.stream_data_display.yview(tk.END)
        else:
            self.stream_data_display.config(state='normal')
            self.stream_data_display.insert(tk.END, "Stream not found.\n")
            self.stream_data_display.config(state='disabled')

    def refresh_stream_dropdown(self):
        menu = self.stream_menu["menu"]
        menu.delete(0, "end")
        for stream_name in streams.keys():
            menu.add_command(label=stream_name, command=lambda value=stream_name: self.update_stream_display(value))

    def toggle_resend(self):
        global resend_messages
        resend_messages = not resend_messages
        if resend_messages:
            self.resend_button.config(text="Disable Resend")
            self.log_message("Resend messages enabled.")
        else:
            self.resend_button.config(text="Enable Resend")
            self.log_message("Resend messages disabled.")

app = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()
