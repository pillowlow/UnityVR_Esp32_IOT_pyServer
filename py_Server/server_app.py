import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import asyncio
import logging
from websocket_server import WebSocketServer  # Import the WebSocketServer class

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebSocket Server")
        

        # Create an instance of WebSocketServer and pass `self` (ServerApp instance) to it
        self.websocket_server = WebSocketServer(self)

        # Main frame that holds all the components
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top controls frame (Start, Stop)
        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.start_button = tk.Button(self.top_frame, text="Start", command=self.start_server)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(self.top_frame, text="Stop", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        # Dropdown to select stream
        self.select_streams_dropdown = tk.StringVar(self.top_frame)
        self.select_streams_dropdown.set("Select Stream")  # Default value
        self.select_streams_menu = tk.OptionMenu(self.top_frame, self.select_streams_dropdown, "Select Stream", *self.websocket_server.streams.keys())
        self.select_streams_menu.pack(side=tk.LEFT, padx=5)
        
        # IP and Port label
        self.server_info_label = tk.Label(self.top_frame, text="........")
        self.server_info_label.pack(side=tk.RIGHT, padx=10)

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
        self.select_clients_menu = tk.OptionMenu(self.select_client_frame, self.select_clients_dropdown, "Select Client", *self.websocket_server.clients.keys())
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
        
        # update stream log 
        self.update_log_loop()

    def start_server(self):
        self.server_thread = Thread(target=self.websocket_server.start)
        self.server_thread.start()
        logging.info("Server starting.")
        self.log_message("Server starting...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
    def update_IP_config(self,host,port):
        self.server_info_label.config(text=f"IP: {host} Port: {port}")

    def stop_server(self):
        self.websocket_server.stop()
        self.server_thread.join()
        self.log_message("Server stopped.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.server_info_label.config(text="")  # Clear IP and Port info when the server stops

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
        for client_id in self.websocket_server.clients.keys():
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
    
    def update_log_loop(self):
        """This function will run periodically to update the logs."""
        # Check the selected stream and refresh the log display
        selected_stream = self.select_streams_dropdown.get()
        self.update_stream_log(selected_stream)

        # Schedule this function to run again after 1 second (1000 ms)
        self.root.after(100, self.update_log_loop)
        
    def update_stream_log(self, selected_stream):
        max_lines = 20
        if selected_stream != "Select Stream" and selected_stream in self.websocket_server.streams:
            current_data = self.websocket_server.streams[selected_stream]
            self.stream_data_display.config(state='normal')
            
            # Insert the new log entry
            self.stream_data_display.insert(tk.END, f"{current_data}\n")
            
            # Check the number of lines in the log
            num_lines = int(self.stream_data_display.index('end-1c').split('.')[0])
            
            # If the number of lines exceeds max_lines, delete the oldest ones
            if num_lines > max_lines:
                self.stream_data_display.delete('1.0', '2.0')
            
            self.stream_data_display.config(state='disabled')
            self.stream_data_display.yview(tk.END)
        else:
            self.stream_data_display.config(state='normal')
            # self.stream_data_display.insert(tk.END, "No valid stream selected or stream not found.\n")
            
            # Optional: Check and delete lines here as well, if needed
            num_lines = int(self.stream_data_display.index('end-1c').split('.')[0])
            if num_lines > max_lines:
                self.stream_data_display.delete('1.0', '2.0')
            
            self.stream_data_display.config(state='disabled')

    def refresh_stream_dropdown(self):
        """Refresh the dropdown menu to include all streams from the WebSocketServer."""
        current_selection = self.select_streams_dropdown.get()  # Preserve the current selection
        menu = self.select_streams_menu["menu"]
        menu.delete(0, "end")  # Clear the existing menu options

        # Add each stream from the WebSocketServer
        for stream_name in self.websocket_server.streams.keys():
            menu.add_command(label=stream_name, command=lambda value=stream_name: self.select_streams_dropdown.set(value))

        # Reapply the preserved selection if it still exists
        if current_selection in self.websocket_server.streams:
            self.select_streams_dropdown.set(current_selection)
        else:
            self.select_streams_dropdown.set("Select Stream")

    def toggle_resend(self):
        global resend_messages
        resend_messages = not resend_messages
        if resend_messages:
            self.resend_button.config(text="Disable Resend")
            self.log_message("Resend messages enabled.")
        else:
            self.resend_button.config(text="Enable Resend")
            self.log_message("Resend messages disabled.")
