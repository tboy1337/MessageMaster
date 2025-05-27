"""
History Tab - UI for viewing message history
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class HistoryTab:
    """Message history view tab"""
    
    def __init__(self, parent, app):
        """Initialize the history tab"""
        self.parent = parent
        self.app = app
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create components
        self._create_components()
        
        # Load message history
        self.load_history()
    
    def _create_components(self):
        """Create tab components"""
        # Top control frame
        top_frame = ttk.Frame(self.frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filter options
        filter_frame = ttk.LabelFrame(top_frame, text="Filter")
        filter_frame.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5)
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var, 
                                   values=["All", "Sent", "Failed", "Delivered"], state="readonly", width=15)
        status_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Service filter
        ttk.Label(filter_frame, text="Service:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.service_var = tk.StringVar(value="All")
        self.service_combo = ttk.Combobox(filter_frame, textvariable=self.service_var, width=15)
        self.service_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Apply filter button
        self.filter_button = ttk.Button(filter_frame, text="Apply Filter", command=self.load_history)
        self.filter_button.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
        
        # Message count
        self.count_var = tk.StringVar(value="0 messages")
        ttk.Label(top_frame, textvariable=self.count_var).pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Message list
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        self.history_tree = ttk.Treeview(
            list_frame, 
            columns=("recipient", "message", "status", "service", "date"),
            show="headings", 
            selectmode="browse"
        )
        
        # Define headings
        self.history_tree.heading("recipient", text="Recipient")
        self.history_tree.heading("message", text="Message")
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("service", text="Service")
        self.history_tree.heading("date", text="Date/Time")
        
        # Define columns
        self.history_tree.column("recipient", width=120, anchor=tk.W)
        self.history_tree.column("message", width=300, anchor=tk.W)
        self.history_tree.column("status", width=80, anchor=tk.CENTER)
        self.history_tree.column("service", width=80, anchor=tk.CENTER)
        self.history_tree.column("date", width=150, anchor=tk.W)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=y_scrollbar.set)
        
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(xscrollcommand=x_scrollbar.set)
        
        # Pack tree and scrollbars
        self.history_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.history_tree.bind("<Double-1>", self._on_message_selected)
        
        # Create context menu
        self._create_context_menu()
        
        # Message details frame
        details_frame = ttk.LabelFrame(self.frame, text="Message Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Details grid
        details_grid = ttk.Frame(details_frame)
        details_grid.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Recipient
        ttk.Label(details_grid, text="Recipient:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.detail_recipient = ttk.Label(details_grid, text="")
        self.detail_recipient.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Status
        ttk.Label(details_grid, text="Status:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.detail_status = ttk.Label(details_grid, text="")
        self.detail_status.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Date
        ttk.Label(details_grid, text="Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.detail_date = ttk.Label(details_grid, text="")
        self.detail_date.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Service
        ttk.Label(details_grid, text="Service:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.detail_service = ttk.Label(details_grid, text="")
        self.detail_service.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Message ID
        ttk.Label(details_grid, text="Message ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.detail_message_id = ttk.Label(details_grid, text="")
        self.detail_message_id.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        # Message text
        ttk.Label(details_grid, text="Message:").grid(row=3, column=0, sticky=tk.NW, padx=5, pady=2)
        
        message_frame = ttk.Frame(details_grid)
        message_frame.grid(row=3, column=1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=2)
        
        self.detail_message = tk.Text(message_frame, wrap=tk.WORD, height=4, width=60)
        self.detail_message.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.detail_message.config(state=tk.DISABLED)
        
        msg_scrollbar = ttk.Scrollbar(message_frame, orient=tk.VERTICAL, command=self.detail_message.yview)
        self.detail_message.configure(yscrollcommand=msg_scrollbar.set)
        msg_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.resend_button = ttk.Button(button_frame, text="Resend", command=self._on_resend)
        self.resend_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.check_status_button = ttk.Button(button_frame, text="Check Status", command=self._on_check_status)
        self.check_status_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Initialize details
        self._clear_details()
    
    def _create_context_menu(self):
        """Create context menu for message list"""
        self.context_menu = tk.Menu(self.history_tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self._on_view_details)
        self.context_menu.add_command(label="Check Status", command=self._on_check_status)
        self.context_menu.add_command(label="Resend", command=self._on_resend)
        
        # Bind right-click event
        self.history_tree.bind("<Button-3>", self._on_context_menu)
    
    def _on_context_menu(self, event):
        """Show context menu on right-click"""
        # Select the item under the cursor
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def load_history(self):
        """Load message history from the database"""
        # Get filter values
        status_filter = self.status_var.get()
        service_filter = self.service_var.get()
        
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Get message history from database
        messages = self.app.db.get_message_history(limit=100)
        
        # Filter messages
        filtered_messages = []
        for message in messages:
            # Apply status filter
            if status_filter != "All" and status_filter.lower() != message['status'].lower():
                continue
                
            # Apply service filter
            if service_filter != "All" and service_filter != message['service']:
                continue
                
            filtered_messages.append(message)
        
        # Update message count
        self.count_var.set(f"{len(filtered_messages)} messages")
        
        # Add to treeview
        for message in filtered_messages:
            # Format date/time
            sent_at = message['sent_at']
            if sent_at:
                try:
                    dt = datetime.strptime(sent_at, '%Y-%m-%d %H:%M:%S')
                    sent_at = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            # Truncate message for display
            msg_text = message['message']
            if len(msg_text) > 50:
                msg_text = msg_text[:47] + "..."
            
            self.history_tree.insert('', tk.END, iid=str(message['id']), 
                                   values=(message['recipient'], msg_text, 
                                          message['status'], message['service'], sent_at))
        
        # Update services for filter dropdown
        self._update_service_filter()
    
    def _update_service_filter(self):
        """Update the service filter dropdown with available services"""
        # Get unique service names from history
        services = set()
        services.add("All")
        
        for item in self.history_tree.get_children():
            values = self.history_tree.item(item, "values")
            if values and len(values) > 3:
                services.add(values[3])
        
        # Update dropdown
        self.service_combo['values'] = sorted(list(services))
    
    def _on_message_selected(self, event):
        """Handle message selection via double-click"""
        self._on_view_details()
    
    def _on_view_details(self):
        """View details of selected message"""
        # Get selected item
        selected = self.history_tree.selection()
        if not selected:
            return
            
        # Get message ID
        message_id = int(selected[0])
        
        # Get message details from database
        self.app.db.cursor.execute('''
        SELECT * FROM message_history WHERE id = ?
        ''', (message_id,))
        
        message = self.app.db.cursor.fetchone()
        if not message:
            return
            
        # Update details display
        self.current_message = message
        
        # Set details fields
        self.detail_recipient.config(text=message['recipient'])
        self.detail_status.config(text=message['status'])
        self.detail_service.config(text=message['service'])
        
        # Format date
        sent_at = message['sent_at']
        if sent_at:
            try:
                dt = datetime.strptime(sent_at, '%Y-%m-%d %H:%M:%S')
                sent_at = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        self.detail_date.config(text=sent_at)
        
        # Set message ID
        msg_id = message['message_id'] or "N/A"
        self.detail_message_id.config(text=msg_id)
        
        # Set message text
        self.detail_message.config(state=tk.NORMAL)
        self.detail_message.delete("1.0", tk.END)
        self.detail_message.insert("1.0", message['message'])
        self.detail_message.config(state=tk.DISABLED)
        
        # Enable/disable buttons based on message state
        if message['status'] == 'sent' and message['message_id']:
            self.check_status_button.config(state=tk.NORMAL)
        else:
            self.check_status_button.config(state=tk.DISABLED)
            
        self.resend_button.config(state=tk.NORMAL)
    
    def _on_check_status(self):
        """Check delivery status of selected message"""
        if not hasattr(self, 'current_message') or not self.current_message:
            # No message selected
            selected = self.history_tree.selection()
            if not selected:
                messagebox.showinfo("Information", "Please select a message first")
                return
                
            # Get message ID
            message_id = int(selected[0])
            
            # Get message details from database
            self.app.db.cursor.execute('''
            SELECT * FROM message_history WHERE id = ?
            ''', (message_id,))
            
            message = self.app.db.cursor.fetchone()
            if not message:
                messagebox.showerror("Error", "Message not found")
                return
                
            self.current_message = message
        
        # Check if message has a message ID
        if not self.current_message['message_id']:
            messagebox.showinfo("Information", "This message does not have a tracking ID")
            return
            
        # Check if message has a service
        if not self.current_message['service']:
            messagebox.showinfo("Information", "Cannot check status: Unknown service")
            return
        
        # Check status in a background thread
        self.app.set_status(f"Checking message status...")
        
        # Start a background thread
        threading.Thread(
            target=self._check_status_thread,
            args=(self.current_message['message_id'], self.current_message['service'])
        ).start()
    
    def _check_status_thread(self, message_id, service_name):
        """Check message status in a background thread"""
        try:
            # Check status with the service
            result = self.app.service_manager.check_message_status(message_id, service_name)
            
            # Update UI in the main thread
            self.app.root.after(0, lambda: self._handle_status_result(result))
            
        except Exception as e:
            # Handle errors in the main thread
            self.app.root.after(0, lambda: self._handle_status_error(str(e)))
    
    def _handle_status_result(self, result):
        """Handle status check result"""
        status = result.get('status', 'unknown')
        details = result.get('details', {})
        
        # Format details for display
        detail_text = "\n".join([f"{k}: {v}" for k, v in details.items() if v])
        
        # Show status
        messagebox.showinfo(
            "Message Status", 
            f"Status: {status.upper()}\n\n{detail_text if detail_text else 'No additional details available'}"
        )
        
        # Update status in the UI
        self.detail_status.config(text=status.upper())
        
        # Refresh the list to show updated status
        self.load_history()
        
        self.app.set_status("Ready")
    
    def _handle_status_error(self, error):
        """Handle status check error"""
        messagebox.showerror("Error", f"Failed to check message status: {error}")
        self.app.set_status("Ready")
    
    def _on_resend(self):
        """Resend the selected message"""
        if not hasattr(self, 'current_message') or not self.current_message:
            # No message selected
            selected = self.history_tree.selection()
            if not selected:
                messagebox.showinfo("Information", "Please select a message first")
                return
                
            # Get message ID
            message_id = int(selected[0])
            
            # Get message details from database
            self.app.db.cursor.execute('''
            SELECT * FROM message_history WHERE id = ?
            ''', (message_id,))
            
            message = self.app.db.cursor.fetchone()
            if not message:
                messagebox.showerror("Error", "Message not found")
                return
                
            self.current_message = message
        
        # Confirm resend
        if not messagebox.askyesno("Confirm Resend", 
                                 f"Resend this message to {self.current_message['recipient']}?"):
            return
        
        # Send the message
        recipient = self.current_message['recipient']
        message_text = self.current_message['message']
        service = self.current_message['service']
        
        # Use the application's send method
        self.app.send_message(recipient, message_text, service)
    
    def _clear_details(self):
        """Clear the details display"""
        self.detail_recipient.config(text="")
        self.detail_status.config(text="")
        self.detail_service.config(text="")
        self.detail_date.config(text="")
        self.detail_message_id.config(text="")
        
        self.detail_message.config(state=tk.NORMAL)
        self.detail_message.delete("1.0", tk.END)
        self.detail_message.config(state=tk.DISABLED)
        
        self.check_status_button.config(state=tk.DISABLED)
        self.resend_button.config(state=tk.DISABLED)
        
        if hasattr(self, 'current_message'):
            delattr(self, 'current_message') 