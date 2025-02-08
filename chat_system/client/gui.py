import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import threading
from queue import Queue

class ChatGUI:
    def __init__(self, 
                 on_login: Callable[[str, str], None],
                 on_create_account: Callable[[str, str], None],
                 on_send_message: Callable[[str, str], None],
                 on_list_accounts: Callable[[Optional[str]], None]):
        
        self.root = tk.Tk()
        self.root.title("Chat Client")
        self.message_queue = Queue()
        
        self.on_login = on_login
        self.on_create_account = on_create_account
        self.on_send_message = on_send_message
        self.on_list_accounts = on_list_accounts
        
        self._create_widgets()
        self._start_message_thread()
    
    def _create_widgets(self):
        # login frame
        self.login_frame = ttk.LabelFrame(self.root, text="Login/Create Account")
        self.login_frame.pack(padx=10, pady=5, fill=tk.X)
        
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(self.login_frame, text="Login", 
                  command=self._handle_login).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.login_frame, text="Create Account", 
                  command=self._handle_create_account).grid(row=2, column=1, padx=5, pady=5)
        
        # chat frame
        self.chat_frame = ttk.LabelFrame(self.root, text="Chat")
        self.chat_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.chat_text = tk.Text(self.chat_frame, height=20, width=50)
        self.chat_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # message frame
        self.message_frame = ttk.Frame(self.chat_frame)
        self.message_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.message_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.recipient_entry = ttk.Entry(self.message_frame, width=15)
        self.recipient_entry.pack(side=tk.LEFT, padx=5)
        
        self.message_entry = ttk.Entry(self.message_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(self.message_frame, text="Send", 
                  command=self._handle_send).pack(side=tk.LEFT, padx=5)
        
        #account list frame
        self.list_frame = ttk.LabelFrame(self.root, text="List Accounts")
        self.list_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.pattern_entry = ttk.Entry(self.list_frame)
        self.pattern_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        ttk.Button(self.list_frame, text="List", 
                  command=self._handle_list).pack(side=tk.LEFT, padx=5, pady=5)
    
    def _handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            self.on_login(username, password)
    
    def _handle_create_account(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username and password:
            self.on_create_account(username, password)
    
    def _handle_send(self):
        recipient = self.recipient_entry.get()
        message = self.message_entry.get()
        if recipient and message:
            self.on_send_message(recipient, message)
            self.message_entry.delete(0, tk.END)
    
    def _handle_list(self):
        pattern = self.pattern_entry.get()
        self.on_list_accounts(pattern if pattern else None)
    
    def display_message(self, message: str):
        """Display a message in the chat window."""
        self.message_queue.put(message)
    
    def _start_message_thread(self):
        """Start a thread to process messages from the queue."""
        def process_messages():
            while True:
                message = self.message_queue.get()
                self.chat_text.insert(tk.END, message + "\n")
                self.chat_text.see(tk.END)
        
        thread = threading.Thread(target=process_messages, daemon=True)
        thread.start()
    
    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop() 