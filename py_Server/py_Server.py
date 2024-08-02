import asyncio
import websockets
import logging
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

clients = set()
resend_messages = True

class WebSocketServer:
    def __init__(self):
        self.server = None
        self.loop = None
        self.should_stop = False

    async def register(self, websocket):
        clients.add(websocket)
        app.add_client(websocket.remote_address)
        logging.info(f"New client connected: {websocket.remote_address}")
        try:
            async for message in websocket:
                logging.info(f"Received message from {websocket.remote_address}: {message}")
                app.log_message(f"Received message from {websocket.remote_address}: {message}")
                if resend_messages:
                    await self.notify_clients(message)
        except websockets.ConnectionClosed as e:
            logging.warning(f"Connection closed: {e}")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            clients.remove(websocket)
            app.remove_client(websocket.remote_address)
            logging.info(f"Client disconnected: {websocket.remote_address}")

    async def notify_clients(self, message):
        if clients:  # asyncio.wait doesn't accept an empty list
            await asyncio.gather(*[client.send(message) for client in clients])

    async def main(self):
        logging.info("Server started, waiting for clients to connect...")
        self.server = await websockets.serve(self.register, "0.0.0.0", 8080)
        while not self.should_stop:
            await asyncio.sleep(1)
        self.server.close()
        await self.server.wait_closed()

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.should_stop = False
        self.loop.run_until_complete(self.main())

    def stop(self):
        self.should_stop = True

server = WebSocketServer()

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebSocket Server")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(self.left_frame, text="Start Server", command=self.start_server)
        self.start_button.pack()

        self.stop_button = tk.Button(self.left_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack()

        self.log_label = tk.Label(self.left_frame, text="Server Log")
        self.log_label.pack()

        self.log_text = scrolledtext.ScrolledText(self.left_frame, state='disabled', height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.message_label = tk.Label(self.right_frame, text="Input message to broadcast:")
        self.message_label.pack()

        self.message_entry = tk.Entry(self.right_frame)
        self.message_entry.pack(fill=tk.X)
        self.message_entry.bind('<Return>', self.broadcast_message)

        self.clients_label = tk.Label(self.right_frame, text="Connected Clients")
        self.clients_label.pack()

        self.clients_list = tk.Listbox(self.right_frame)
        self.clients_list.pack(fill=tk.BOTH, expand=True)

        self.resend_button = tk.Button(self.right_frame, text="Disable Resend", command=self.toggle_resend)
        self.resend_button.pack()

    def start_server(self):
        self.server_thread = Thread(target=server.start)
        self.server_thread.start()
        self.log_message("Server starting...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_server(self):
        server.stop()
        self.server_thread.join()
        self.log_message("Server stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)

    def add_client(self, client):
        self.clients_list.insert(tk.END, str(client))

    def remove_client(self, client):
        clients = self.clients_list.get(0, tk.END)
        for i, c in enumerate(clients):
            if c == str(client):
                self.clients_list.delete(i)
                break

    def broadcast_message(self, event):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        asyncio.run_coroutine_threadsafe(server.notify_clients(message), server.loop)
        self.log_message(f"Broadcasted message: {message}")

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
