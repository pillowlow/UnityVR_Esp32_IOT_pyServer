import asyncio
import websockets
import logging
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import socket  # Import socket to get the IP address

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

clients = {}  # Dictionary to store client ID and WebSocket pairs

class WebSocketServer:
    def __init__(self):
        self.server = None
        self.loop = None
        self.should_stop = False

    async def register(self, websocket):
        await websocket.send("REQUEST_ID")  # Server requests client ID
        try:
            client_id = await websocket.recv()  # Receive the client ID from the client
            clients[client_id] = websocket
            app.add_client(client_id)
            logging.info(f"New client connected: ID {client_id}")

            async for message in websocket:
                logging.info(f"Received message from ID {client_id}: {message}")
                app.log_message(f"Received from ID {client_id}: {message}")
        except websockets.ConnectionClosed as e:
            logging.warning(f"Connection closed: {e}")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            clients.pop(client_id, None)
            app.remove_client(client_id)
            logging.info(f"Client disconnected: ID {client_id}")

    async def send_message_to_client(self, client_id, message):
        client = clients.get(client_id)
        if client:
            await client.send(message)
            logging.info(f"Sent message to ID {client_id}: {message}")
            app.log_message(f"Sent to ID {client_id}: {message}")
        else:
            logging.warning(f"Client ID {client_id} not found.")
            app.log_message(f"Client ID {client_id} not found.")

    async def notify_clients(self, message):
        if clients:  # asyncio.wait doesn't accept an empty list
            logging.info(f"Broadcasting message to {len(clients)} clients: {message}")
            await asyncio.gather(*[client.send(message) for client in clients.values()])
        else:
            logging.warning("No clients connected to broadcast the message.")
            app.log_message("No clients connected to broadcast the message.")

    async def disconnect_all_clients(self):
        if clients:
            logging.info("Disconnecting all clients...")
            disconnect_tasks = []
            for client_id, websocket in list(clients.items()):
                try:
                    logging.info(f"Sending disconnect notice to client ID {client_id}")
                    await websocket.send("SERVER_CLOSING")
                    logging.info(f"Adding disconnect task for client ID {client_id}")

                    # Attempting to close the connection with a timeout
                    logging.info(f"Attempting to close connection for client ID {client_id}")
                    await asyncio.wait_for(websocket.close(), timeout=5.0)
                    logging.info(f"Connection closed for client ID {client_id}")

                except asyncio.TimeoutError:
                    logging.error(f"Timeout occurred while disconnecting client ID {client_id}")
                    # Forcefully close the connection
                    await websocket.close(code=1000, reason='Server forced closure')
                    logging.info(f"Forcefully closed connection for client ID {client_id}")
                except Exception as e:
                    logging.error(f"Error disconnecting client ID {client_id}: {e}")
            clients.clear()
            logging.info("All clients have been disconnected.")




    async def main(self):
        logging.info("Server started, waiting for clients to connect...")
        self.server = await websockets.serve(self.register, "0.0.0.0", 8080)
        try:
            while not self.should_stop:
                await asyncio.sleep(1)
        finally:
            logging.info("Server stopping, disconnecting all clients...")
            await self.disconnect_all_clients()  # Disconnect all clients before closing the server

            logging.info("All clients disconnected, closing server...")
            self.server.close()
            logging.info("Server socket closed, waiting for server to finish closing...")

            try:
                await asyncio.wait_for(self.server.wait_closed(), timeout=1.0)  # Add timeout to server closure
                logging.info("Server has been stopped successfully.")
            except asyncio.TimeoutError:
                logging.error("Timeout while waiting for server to close.")
                logging.info("Forcibly stopping the event loop and cancelling all tasks...")

                # Forcefully stop the event loop and cancel all tasks
                tasks = asyncio.all_tasks(self.loop)
                for task in tasks:
                    logging.info(f"Cancelling task: {task}")
                    task.cancel()

                logging.info("Stopping the event loop...")
                self.loop.stop()  # Attempt to stop the event loop
                logging.info("Event loop stopped.")
            except Exception as e:
                logging.error(f"Error while closing server: {e}")

            finally:
                # Attempt to clean up and close the event loop completely
                if not self.loop.is_closed():
                    logging.info("Closing the event loop forcefully...")
                    self.loop.close()
                    logging.info("Event loop closed.")



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

            # Now, safely close the server
            self.server.close()



def get_ip_address():
    """Get the server's IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "127.0.0.1"  # Default to localhost if unable to get IP
    finally:
        s.close()
    return ip_address

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

        # Display the server IP address
        self.ip_address_label = tk.Label(self.left_frame, text=f"Server IP: {get_ip_address()}")
        self.ip_address_label.pack()

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

        self.client_id_label = tk.Label(self.right_frame, text="Send message to client ID:")
        self.client_id_label.pack()

        self.client_id_entry = tk.Entry(self.right_frame)
        self.client_id_entry.pack(fill=tk.X)

        self.specific_message_entry = tk.Entry(self.right_frame)
        self.specific_message_entry.pack(fill=tk.X)
        self.specific_message_entry.bind('<Return>', self.send_message_to_specific_client)

        self.resend_button = tk.Button(self.right_frame, text="Disable Resend", command=self.toggle_resend)
        self.resend_button.pack()

    def start_server(self):
        self.server_thread = Thread(target=server.start)
        self.server_thread.start()
        self.log_message("Server starting...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_server(self):
        # Signal the server to stop
        server.stop()

        # Join the server thread to ensure it has finished
        self.server_thread.join()

        # Update the UI
        self.log_message("Server stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.config(state='disabled')
        self.log_text.yview(tk.END)

    def add_client(self, client_id):
        self.clients_list.insert(tk.END, f"Client ID {client_id}")

    def remove_client(self, client_id):
        clients = self.clients_list.get(0, tk.END)
        for i, c in enumerate(clients):
            if c == f"Client ID {client_id}":
                self.clients_list.delete(i)
                break

    def broadcast_message(self, event):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        asyncio.run_coroutine_threadsafe(server.notify_clients(message), server.loop)
        self.log_message(f"Broadcasted message: {message}")

    def send_message_to_specific_client(self, event):
        try:
            client_id = self.client_id_entry.get()
            message = self.specific_message_entry.get()
            asyncio.run_coroutine_threadsafe(server.send_message_to_client(client_id, message), server.loop)
            self.log_message(f"Sent to client ID {client_id}: {message}")
        except ValueError:
            self.log_message("Invalid client ID.")

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

