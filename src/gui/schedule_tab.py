"""
Schedule Tab - UI for scheduling and automating messages
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import json

class ScheduleTab:
    """Schedule and automation tab"""
    
    def __init__(self, parent, app):
        """Initialize the schedule tab"""
        self.parent = parent
        self.app = app
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create components
        self._create_components()
        
        # Load scheduled messages
        self.load_scheduled_messages()
    
    def _create_components(self):
        """Create tab components"""
        # Split into left and right panels
        paned_window = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for scheduled messages list
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Right panel for schedule details/form
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        # Create components for each panel
        self._create_list_panel(left_frame)
        self._create_form_panel(right_frame)
    
    def _create_list_panel(self, parent):
        """Create the scheduled messages list panel"""
        # Header and controls
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="Scheduled Messages", style="Title.TLabel").pack(side=tk.LEFT)
        
        refresh_button = ttk.Button(header_frame, text="Refresh", command=self.load_scheduled_messages)
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Filter frame
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Show:").pack(side=tk.LEFT, padx=5)
        
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            filter_frame, textvariable=self.status_var, 
            values=["All", "Pending", "Sent", "Failed"], 
            state="readonly", width=10
        )
        status_combo.pack(side=tk.LEFT, padx=5)
        
        self.filter_button = ttk.Button(
            filter_frame, text="Apply Filter", 
            command=self.load_scheduled_messages
        )
        self.filter_button.pack(side=tk.LEFT, padx=5)
        
        # Message list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        self.schedule_tree = ttk.Treeview(
            list_frame, 
            columns=("recipient", "time", "recurrence", "status"),
            show="headings", 
            selectmode="browse"
        )
        
        # Define headings
        self.schedule_tree.heading("recipient", text="Recipient")
        self.schedule_tree.heading("time", text="Scheduled Time")
        self.schedule_tree.heading("recurrence", text="Recurrence")
        self.schedule_tree.heading("status", text="Status")
        
        # Define columns
        self.schedule_tree.column("recipient", width=150, anchor=tk.W)
        self.schedule_tree.column("time", width=150, anchor=tk.W)
        self.schedule_tree.column("recurrence", width=100, anchor=tk.CENTER)
        self.schedule_tree.column("status", width=80, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind tree events
        self.schedule_tree.bind("<Double-1>", self._on_schedule_selected)
        
        # Create context menu
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Create context menu for scheduled message list"""
        self.context_menu = tk.Menu(self.schedule_tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self._on_edit_schedule)
        self.context_menu.add_command(label="Delete", command=self._on_delete_schedule)
        
        # Bind right-click event
        self.schedule_tree.bind("<Button-3>", self._on_context_menu)
    
    def _on_context_menu(self, event):
        """Show context menu on right-click"""
        # Select the item under the cursor
        item = self.schedule_tree.identify_row(event.y)
        if item:
            self.schedule_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _create_form_panel(self, parent):
        """Create the schedule form panel"""
        # Header
        ttk.Label(parent, text="Schedule Message", style="Title.TLabel").pack(padx=5, pady=5, anchor=tk.W)
        
        # Form frame
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Recipient
        ttk.Label(form_frame, text="Recipient:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.recipient_var = tk.StringVar()
        recipient_entry = ttk.Entry(form_frame, textvariable=self.recipient_var, width=30)
        recipient_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Contact button
        contact_button = ttk.Button(form_frame, text="Choose Contact", command=self._on_choose_contact)
        contact_button.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Date and time
        ttk.Label(form_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_picker = DateEntry(form_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_picker.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Time:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.time_var = tk.StringVar(value="12:00")
        time_entry = ttk.Entry(form_frame, textvariable=self.time_var, width=10)
        time_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Recurrence
        ttk.Label(form_frame, text="Recurrence:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.recurrence_var = tk.StringVar(value="Once")
        recurrence_options = ["Once", "Daily", "Weekly", "Monthly", "Custom"]
        recurrence_combo = ttk.Combobox(form_frame, textvariable=self.recurrence_var, 
                                       values=recurrence_options, state="readonly", width=15)
        recurrence_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        recurrence_combo.bind("<<ComboboxSelected>>", self._on_recurrence_changed)
        
        # Custom recurrence frame (hidden by default)
        self.custom_frame = ttk.Frame(form_frame)
        self.custom_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W+tk.E, padx=5, pady=5)
        self.custom_frame.grid_remove()  # Hide initially
        
        ttk.Label(self.custom_frame, text="Every").pack(side=tk.LEFT, padx=2)
        self.custom_days_var = tk.StringVar(value="1")
        custom_days_entry = ttk.Spinbox(self.custom_frame, from_=1, to=365, width=5, 
                                      textvariable=self.custom_days_var)
        custom_days_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(self.custom_frame, text="days").pack(side=tk.LEFT, padx=2)
        
        # SMS Service
        ttk.Label(form_frame, text="SMS Service:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.service_var = tk.StringVar(value="Default")
        self.service_combo = ttk.Combobox(form_frame, textvariable=self.service_var, state="readonly", width=15)
        self.service_combo.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Update services in dropdown
        self._update_services()
        
        # Message text
        ttk.Label(form_frame, text="Message:").grid(row=5, column=0, sticky=tk.NW, padx=5, pady=5)
        
        message_frame = ttk.Frame(form_frame)
        message_frame.grid(row=5, column=1, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        self.message_text = tk.Text(message_frame, wrap=tk.WORD, height=10, width=40)
        self.message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        message_scrollbar = ttk.Scrollbar(message_frame, orient=tk.VERTICAL, command=self.message_text.yview)
        self.message_text.configure(yscrollcommand=message_scrollbar.set)
        message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Character counter
        self.char_count_var = tk.StringVar(value="0/160 characters")
        ttk.Label(form_frame, textvariable=self.char_count_var).grid(
            row=6, column=1, columnspan=3, sticky=tk.E, padx=5, pady=2)
        
        # Bind text changes to update character count
        self.message_text.bind("<KeyRelease>", self._update_char_count)
        
        # Template dropdown
        ttk.Label(form_frame, text="Template:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.template_var = tk.StringVar()
        self.template_dropdown = ttk.Combobox(form_frame, textvariable=self.template_var, state="readonly", width=30)
        self.template_dropdown.grid(row=7, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        self.template_dropdown.bind("<<ComboboxSelected>>", self._on_template_selected)
        
        # Load templates
        self._load_templates()
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=4, sticky=tk.E, padx=5, pady=10)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self._clear_form)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        self.save_button = ttk.Button(button_frame, text="Schedule", command=self._on_save_schedule)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        # Initialize form
        self._clear_form()
    
    def _update_services(self):
        """Update the services dropdown"""
        # Get available services
        services = ["Default"] + self.app.service_manager.get_configured_services()
        self.service_combo['values'] = services
        
        # Set default
        self.service_var.set("Default")
    
    def _load_templates(self):
        """Load message templates from the database"""
        templates = self.app.db.get_templates()
        
        # Format template names for the dropdown
        template_names = ["-- Select Template --"]
        self.templates = {}
        
        for template in templates:
            name = template['name']
            template_names.append(name)
            self.templates[name] = template['content']
        
        # Update dropdown
        self.template_dropdown['values'] = template_names
        self.template_dropdown.current(0)
    
    def _on_template_selected(self, event=None):
        """Handle template selection"""
        template_name = self.template_var.get()
        
        if template_name and template_name != "-- Select Template --":
            # Get the template content
            content = self.templates.get(template_name, "")
            
            # Insert the template into the message field
            self.message_text.delete("1.0", tk.END)
            self.message_text.insert("1.0", content)
            self._update_char_count()
    
    def _update_char_count(self, event=None):
        """Update the character count display"""
        text = self.message_text.get("1.0", tk.END)
        count = len(text.strip())
        
        # SMS messages are typically limited to 160 characters
        # but can be sent as multiple messages
        parts = count // 160 + (1 if count % 160 > 0 else 0)
        
        if parts > 1:
            self.char_count_var.set(f"{count} characters ({parts} messages)")
        else:
            self.char_count_var.set(f"{count}/160 characters")
    
    def _on_recurrence_changed(self, event=None):
        """Handle recurrence selection change"""
        recurrence = self.recurrence_var.get()
        
        if recurrence == "Custom":
            self.custom_frame.grid()  # Show custom options
        else:
            self.custom_frame.grid_remove()  # Hide custom options
    
    def _on_choose_contact(self):
        """Open contact selection dialog"""
        # Switch to contacts tab
        self.app.notebook.select(1)  # Index 1 is the Contacts tab
        
        # Tell the contacts tab we're selecting for the schedule tab
        self.app.tabs["contacts"].set_selection_mode(True)
    
    def load_scheduled_messages(self):
        """Load scheduled messages from the database"""
        # Get filter status
        status_filter = self.status_var.get().lower()
        
        # Clear existing items
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
            
        # Get scheduled messages
        if status_filter == "all":
            messages = self.app.scheduler.get_scheduled_messages()
        else:
            messages = self.app.scheduler.get_scheduled_messages(status=status_filter)
            
        # Add to treeview
        for message in messages:
            # Format schedule time
            schedule_time = message['scheduled_time']
            if schedule_time:
                try:
                    dt = datetime.strptime(schedule_time, '%Y-%m-%d %H:%M:%S')
                    schedule_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            # Format recurrence
            recurrence = message.get('recurrence', 'Once')
            if recurrence is None:
                recurrence = "Once"
                
            # Insert item
            self.schedule_tree.insert('', tk.END, iid=str(message['id']), 
                                    values=(message['recipient'], schedule_time, 
                                           recurrence.capitalize(), message['status'].capitalize()))
    
    def _on_schedule_selected(self, event):
        """Handle schedule selection via double-click"""
        self._on_edit_schedule()
    
    def _on_edit_schedule(self):
        """Edit the selected scheduled message"""
        # Get selected item
        selected = self.schedule_tree.selection()
        if not selected:
            messagebox.showinfo("Information", "Please select a scheduled message to edit")
            return
            
        # Get schedule ID
        schedule_id = int(selected[0])
        
        # Get schedule details from database
        self.app.db.cursor.execute('''
        SELECT * FROM scheduled_messages WHERE id = ?
        ''', (schedule_id,))
        
        schedule = self.app.db.cursor.fetchone()
        if not schedule:
            messagebox.showerror("Error", "Failed to load schedule details")
            return
            
        # Set form for editing
        self.editing_id = schedule_id
        
        # Set recipient
        self.recipient_var.set(schedule['recipient'])
        
        # Set schedule time
        try:
            dt = datetime.strptime(schedule['scheduled_time'], '%Y-%m-%d %H:%M:%S')
            self.date_picker.set_date(dt.date())
            self.time_var.set(dt.strftime('%H:%M'))
        except:
            # Use current date/time if parsing fails
            now = datetime.now()
            self.date_picker.set_date(now.date())
            self.time_var.set(now.strftime('%H:%M'))
        
        # Set recurrence
        recurrence = schedule.get('recurrence')
        if recurrence is None:
            recurrence = "Once"
        self.recurrence_var.set(recurrence.capitalize())
        
        # Set custom recurrence data if applicable
        if recurrence == "custom":
            recurrence_data = schedule.get('recurrence_data')
            if recurrence_data:
                try:
                    if isinstance(recurrence_data, str):
                        data = json.loads(recurrence_data)
                    else:
                        data = recurrence_data
                        
                    if 'days_interval' in data:
                        self.custom_days_var.set(str(data['days_interval']))
                except:
                    self.custom_days_var.set("1")
            self.custom_frame.grid()  # Show custom options
        else:
            self.custom_frame.grid_remove()  # Hide custom options
        
        # Set service
        service = schedule.get('service')
        if service:
            self.service_var.set(service)
        else:
            self.service_var.set("Default")
        
        # Set message
        self.message_text.delete("1.0", tk.END)
        self.message_text.insert("1.0", schedule['message'])
        self._update_char_count()
        
        # Update button text
        self.save_button.config(text="Update Schedule")
    
    def _on_delete_schedule(self):
        """Delete the selected scheduled message"""
        # Get selected item
        selected = self.schedule_tree.selection()
        if not selected:
            messagebox.showinfo("Information", "Please select a scheduled message to delete")
            return
            
        # Get schedule ID
        schedule_id = int(selected[0])
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this scheduled message?"):
            return
            
        # Delete the schedule
        success = self.app.scheduler.cancel_scheduled_message(schedule_id)
        
        if success:
            messagebox.showinfo("Success", "Scheduled message deleted")
            
            # Refresh the list
            self.load_scheduled_messages()
            
            # Clear the form if we were editing this schedule
            if hasattr(self, 'editing_id') and self.editing_id == schedule_id:
                self._clear_form()
        else:
            messagebox.showerror("Error", "Failed to delete scheduled message")
    
    def _on_save_schedule(self):
        """Save or update a scheduled message"""
        # Get form values
        recipient = self.recipient_var.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        # Validate required fields
        if not recipient:
            messagebox.showerror("Error", "Recipient is required")
            return
            
        if not message:
            messagebox.showerror("Error", "Message is required")
            return
        
        # Get schedule time
        try:
            date_str = self.date_picker.get_date().strftime('%Y-%m-%d')
            time_str = self.time_var.get()
            
            # Validate time format
            datetime.strptime(time_str, '%H:%M')
            
            # Combine date and time
            schedule_time = datetime.strptime(f"{date_str} {time_str}:00", '%Y-%m-%d %H:%M:%S')
            
            # Check that time is in the future
            if schedule_time <= datetime.now():
                messagebox.showerror("Error", "Schedule time must be in the future")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM")
            return
        
        # Get recurrence
        recurrence = self.recurrence_var.get().lower()
        if recurrence == "once":
            recurrence = None
            recurrence_data = None
        else:
            # Handle custom recurrence
            if recurrence == "custom":
                try:
                    days = int(self.custom_days_var.get())
                    if days < 1:
                        messagebox.showerror("Error", "Days interval must be at least 1")
                        return
                        
                    recurrence_data = {"days_interval": days}
                except ValueError:
                    messagebox.showerror("Error", "Invalid days value")
                    return
            else:
                recurrence_data = None
        
        # Get service
        service = self.service_var.get()
        if service == "Default":
            service = None
        
        # Save or update the schedule
        if hasattr(self, 'editing_id'):
            # Update existing schedule
            success = self.app.scheduler.update_scheduled_message(
                message_id=self.editing_id,
                recipient=recipient,
                message=message,
                schedule_time=schedule_time,
                recurrence=recurrence,
                recurrence_data=recurrence_data,
                service=service
            )
            
            if success:
                messagebox.showinfo("Success", "Schedule updated successfully")
            else:
                messagebox.showerror("Error", "Failed to update schedule")
        else:
            # Create new schedule
            message_id = self.app.scheduler.schedule_message(
                recipient=recipient,
                message=message,
                schedule_time=schedule_time,
                recurrence=recurrence,
                recurrence_data=recurrence_data,
                service=service
            )
            
            if message_id:
                messagebox.showinfo("Success", "Message scheduled successfully")
            else:
                messagebox.showerror("Error", "Failed to schedule message")
        
        # Refresh the list and clear the form
        self.load_scheduled_messages()
        self._clear_form()
    
    def _clear_form(self):
        """Clear the schedule form"""
        # Clear recipient and message
        self.recipient_var.set("")
        self.message_text.delete("1.0", tk.END)
        
        # Reset date/time to tomorrow at noon
        tomorrow = datetime.now() + timedelta(days=1)
        self.date_picker.set_date(tomorrow.date())
        self.time_var.set("12:00")
        
        # Reset recurrence
        self.recurrence_var.set("Once")
        self.custom_frame.grid_remove()
        self.custom_days_var.set("1")
        
        # Reset service
        self.service_var.set("Default")
        
        # Reset template
        self.template_dropdown.current(0)
        
        # Update char count
        self._update_char_count()
        
        # Reset button text
        self.save_button.config(text="Schedule")
        
        # Clear editing ID
        if hasattr(self, 'editing_id'):
            delattr(self, 'editing_id')
    
    def set_new_scheduled_message(self, recipient, message):
        """Set up a new scheduled message with the given recipient and message"""
        # Clear the form first
        self._clear_form()
        
        # Set recipient and message
        self.recipient_var.set(recipient)
        self.message_text.delete("1.0", tk.END)
        self.message_text.insert("1.0", message)
        self._update_char_count()
        
        # Focus on the date picker
        self.date_picker.focus_set() 