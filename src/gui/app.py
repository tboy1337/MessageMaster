"""
Main SMSMaster Application GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
import pycountry
import os

from src.models.database import Database
from src.api.service_manager import SMSServiceManager
from src.models.contact_manager import ContactManager
from src.automation.scheduler import MessageScheduler
from src.security.validation import InputValidator
from src.gui.message_tab import MessageTab
from src.gui.contact_tab import ContactTab
from src.gui.history_tab import HistoryTab
from src.gui.schedule_tab import ScheduleTab
from src.gui.settings_tab import SettingsTab
from src.gui.templates_tab import TemplatesTab

class SMSApplication:
    """Main SMSMaster Application"""
    
    def __init__(self, root, config=None, notification=None):
        """Initialize the application with the given root window"""
        self.root = root
        self.root.title("SMSMaster")
        
        # Save references to services
        self.config = config
        self.notification = notification
        
        # Set app icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "SMSMaster_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # Icon not found, continue without it
        
        # Configure the style
        self._configure_style()
        
        # Create components
        self._create_components()
        
        # Initialize services
        self._initialize_services()
        
        # Create tabs
        self._create_tabs()
        
        # Set up event bindings
        self._setup_bindings()
        
        # Start background threads
        self._start_background_tasks()
        
        # Set default focus
        self.tabs["message"].recipient_entry.focus_set()
    
    def _configure_style(self):
        """Configure the application style"""
        style = ttk.Style()
        
        # Use system theme as base
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure colors and fonts
        bg_color = "#f5f5f5"
        accent_color = "#4a6cd4"
        
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TNotebook", background=bg_color)
        style.configure("TNotebook.Tab", padding=[10, 4], font=("Segoe UI", 10))
        
        # Configure custom styles
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9))
        
        style.configure("Primary.TButton", background=accent_color)
        
        # Set root background
        self.root.configure(background=bg_color)
    
    def _create_components(self):
        """Create main application components"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="SMSMaster", style="Header.TLabel").pack(side=tk.LEFT)
        
        # Create status bar
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT)
        
        self.service_status = ttk.Label(self.status_bar, text="No SMS service configured", 
                                       style="Status.TLabel")
        self.service_status.pack(side=tk.RIGHT)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _initialize_services(self):
        """Initialize application services"""
        # Database connection
        self.db = Database()
        
        # SMS service manager
        self.service_manager = SMSServiceManager(self.db)
        
        # Contact manager
        self.contact_manager = ContactManager(self.db)
        
        # Message scheduler
        self.scheduler = MessageScheduler(self.db, self.service_manager)
        
        # Input validator
        self.validator = InputValidator()
        
        # Start the scheduler
        self.scheduler.start()
        
        # Register scheduler callbacks
        self.scheduler.register_callback('message_sent', self._on_scheduled_message_sent)
        self.scheduler.register_callback('message_failed', self._on_scheduled_message_failed)
    
    def _create_tabs(self):
        """Create application tabs"""
        self.tabs = {}
        
        # Message Tab
        message_frame = ttk.Frame(self.notebook)
        self.tabs["message"] = MessageTab(message_frame, self)
        self.notebook.add(message_frame, text="Send Message")
        
        # Contacts Tab
        contacts_frame = ttk.Frame(self.notebook)
        self.tabs["contacts"] = ContactTab(contacts_frame, self)
        self.notebook.add(contacts_frame, text="Contacts")
        
        # History Tab
        history_frame = ttk.Frame(self.notebook)
        self.tabs["history"] = HistoryTab(history_frame, self)
        self.notebook.add(history_frame, text="Message History")
        
        # Schedule Tab
        schedule_frame = ttk.Frame(self.notebook)
        self.tabs["schedule"] = ScheduleTab(schedule_frame, self)
        self.notebook.add(schedule_frame, text="Scheduler")
        
        # Templates Tab
        templates_frame = ttk.Frame(self.notebook)
        self.tabs["templates"] = TemplatesTab(templates_frame, self)
        self.notebook.add(templates_frame, text="Templates")
        
        # Settings Tab
        settings_frame = ttk.Frame(self.notebook)
        self.tabs["settings"] = SettingsTab(settings_frame, self)
        self.notebook.add(settings_frame, text="Settings")
    
    def _setup_bindings(self):
        """Set up event bindings"""
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _start_background_tasks(self):
        """Start background tasks"""
        # Start status updater
        self.status_update_thread = threading.Thread(target=self._update_status_periodically)
        self.status_update_thread.daemon = True
        self.status_update_thread.start()
        
        # Initialize system tray if available
        try:
            from src.gui.systemtray import SystemTrayIcon
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "SMSMaster_icon.ico")
            self.tray_icon = SystemTrayIcon(self, icon_path=icon_path)
        except ImportError:
            # System tray functionality not available
            self.tray_icon = None
    
    def _update_status_periodically(self):
        """Update status information periodically"""
        while True:
            try:
                self._update_service_status()
                time.sleep(5)  # Update every 5 seconds
            except:
                # Ignore errors in background thread
                pass
    
    def _update_service_status(self):
        """Update the SMS service status display"""
        if not self.service_manager.active_service:
            service_text = "No SMS service configured"
        else:
            service = self.service_manager.active_service
            quota = service.get_remaining_quota()
            service_text = f"Service: {service.service_name} | Remaining: {quota}/{service.daily_limit}"
            
        # Update in the main thread
        self.root.after(0, lambda: self.service_status.config(text=service_text))
    
    def _on_tab_changed(self, event):
        """Handle tab changed event"""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        
        # Refresh data when switching to certain tabs
        if current_tab == "Message History":
            self.tabs["history"].load_history()
        elif current_tab == "Contacts":
            self.tabs["contacts"].load_contacts()
        elif current_tab == "Scheduler":
            self.tabs["schedule"].load_scheduled_messages()
        elif current_tab == "Templates":
            self.tabs["templates"].load_templates()
    
    def _on_scheduled_message_sent(self, data):
        """Handle scheduled message sent event"""
        # Update the UI in the main thread
        self.root.after(0, lambda: self._update_after_scheduled_send(data))
    
    def _update_after_scheduled_send(self, data):
        """Update UI after scheduled message is sent"""
        self.set_status(f"Scheduled message to {data['recipient']} sent successfully")
        
        # Refresh relevant tabs if they're currently visible
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == "Message History":
            self.tabs["history"].load_history()
        elif current_tab == "Scheduler":
            self.tabs["schedule"].load_scheduled_messages()
    
    def _on_scheduled_message_failed(self, data):
        """Handle scheduled message failed event"""
        # Update the UI in the main thread
        self.root.after(0, lambda: self._update_after_scheduled_failure(data))
    
    def _update_after_scheduled_failure(self, data):
        """Update UI after scheduled message fails"""
        self.set_status(f"Failed to send scheduled message to {data['recipient']}: {data.get('error', 'Unknown error')}")
        
        # Refresh scheduler tab if visible
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == "Scheduler":
            self.tabs["schedule"].load_scheduled_messages()
    
    def send_message(self, recipient, message, service_name=None):
        """Send an SMS message"""
        # Validate inputs
        valid_phone, phone_error = self.validator.validate_phone_input(recipient)
        if not valid_phone:
            messagebox.showerror("Invalid Phone Number", phone_error)
            return False
            
        valid_msg, msg_error = self.validator.validate_message(message)
        if not valid_msg:
            messagebox.showerror("Invalid Message", msg_error)
            return False
        
        # Send in a background thread to avoid blocking UI
        threading.Thread(
            target=self._send_message_thread,
            args=(recipient, message, service_name)
        ).start()
        
        return True
    
    def _send_message_thread(self, recipient, message, service_name):
        """Send message in a background thread"""
        try:
            # Update status
            self.set_status(f"Sending message to {recipient}...")
            
            # Send the message
            response = self.service_manager.send_sms(recipient, message, service_name)
            
            # Handle the response in the main thread
            self.root.after(0, lambda: self._handle_send_response(response, recipient))
            
        except Exception as e:
            # Handle errors in the main thread
            self.root.after(0, lambda: self._handle_send_error(str(e), recipient))
    
    def _handle_send_response(self, response, recipient):
        """Handle send message response"""
        if response.success:
            self.set_status(f"Message sent successfully to {recipient}")
            messagebox.showinfo("Success", f"Message sent successfully to {recipient}")
            
            # Refresh history tab if it's visible
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            if current_tab == "Message History":
                self.tabs["history"].load_history()
                
        else:
            self.set_status(f"Failed to send message: {response.error}")
            messagebox.showerror("Error", f"Failed to send message: {response.error}")
            
        # Update service status
        self._update_service_status()
    
    def _handle_send_error(self, error, recipient):
        """Handle send message error"""
        self.set_status(f"Error sending message to {recipient}")
        messagebox.showerror("Error", f"Error sending message: {error}")
    
    def set_status(self, message):
        """Set the status bar message"""
        self.status_label.config(text=message)
    
    def load_contact_to_message(self, contact_id):
        """Load a contact into the message tab"""
        contact = self.contact_manager.get_contact(contact_id)
        if contact:
            # Switch to message tab
            self.notebook.select(0)
            
            # Set recipient
            self.tabs["message"].set_recipient(contact["phone"])
    
    def _on_close(self):
        """Handle application close"""
        try:
            # Stop background threads
            self.scheduler.stop()
            
            # Shutdown tray icon if active
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.shutdown()
            
            # Close database connection
            self.db.close()
        except Exception as e:
            print(f"Error during shutdown: {e}")
            
        # Destroy the window
        self.root.destroy() 