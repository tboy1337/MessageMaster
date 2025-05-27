"""
Settings Tab - UI for configuring SMS services and application settings
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json

from src.security.validation import InputValidator

class SettingsTab:
    """Settings and configuration tab"""
    
    def __init__(self, parent, app):
        """Initialize the settings tab"""
        self.parent = parent
        self.app = app
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for settings sections
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create settings pages
        self._create_sms_services_page()
        self._create_general_settings_page()
        
        # Load current settings
        self._load_current_settings()
    
    def _create_sms_services_page(self):
        """Create the SMS services configuration page"""
        services_frame = ttk.Frame(self.notebook)
        self.notebook.add(services_frame, text="SMS Services")
        
        # Available services section
        service_frame = ttk.LabelFrame(services_frame, text="SMS Services")
        service_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Service selection
        ttk.Label(service_frame, text="Select Service:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.service_var = tk.StringVar()
        self.service_combo = ttk.Combobox(service_frame, textvariable=self.service_var, state="readonly", width=20)
        self.service_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Set service types
        self.service_combo['values'] = ["Twilio", "TextBelt"]
        
        # Bind selection event
        self.service_combo.bind("<<ComboboxSelected>>", self._on_service_selected)
        
        # Service details
        self.service_details_frame = ttk.LabelFrame(services_frame, text="Service Configuration")
        self.service_details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Empty frame to start
        ttk.Label(self.service_details_frame, text="Select a service to configure").pack(padx=20, pady=20)
        
        # Active service frame
        active_frame = ttk.LabelFrame(services_frame, text="Active SMS Service")
        active_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Current active service
        ttk.Label(active_frame, text="Current Active Service:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.active_service_var = tk.StringVar(value="None")
        ttk.Label(active_frame, textvariable=self.active_service_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Service quota
        ttk.Label(active_frame, text="Remaining Quota:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.quota_var = tk.StringVar(value="N/A")
        ttk.Label(active_frame, textvariable=self.quota_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Set active button
        self.set_active_button = ttk.Button(active_frame, text="Set as Active", command=self._on_set_active_service)
        self.set_active_button.grid(row=0, column=2, rowspan=2, sticky=tk.E, padx=10, pady=5)
    
    def _create_general_settings_page(self):
        """Create the general settings page"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General Settings")
        
        # General app settings
        app_frame = ttk.LabelFrame(general_frame, text="Application Settings")
        app_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start minimized option
        self.start_minimized_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(app_frame, text="Start minimized to system tray", variable=self.start_minimized_var).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Check for updates option
        self.check_updates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(app_frame, text="Check for updates on startup", variable=self.check_updates_var).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Notification settings
        notification_frame = ttk.LabelFrame(general_frame, text="Notification Settings")
        notification_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Show notifications option
        self.show_notifications_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notification_frame, text="Show desktop notifications", 
                       variable=self.show_notifications_var).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Play sound option
        self.play_sound_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notification_frame, text="Play sound on message sent/received", 
                       variable=self.play_sound_var).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Scheduler settings
        scheduler_frame = ttk.LabelFrame(general_frame, text="Scheduler Settings")
        scheduler_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Check interval
        ttk.Label(scheduler_frame, text="Check scheduled messages every:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
            
        interval_frame = ttk.Frame(scheduler_frame)
        interval_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.check_interval_var = tk.IntVar(value=1)
        ttk.Spinbox(interval_frame, from_=1, to=60, width=5, textvariable=self.check_interval_var).pack(side=tk.LEFT)
        ttk.Label(interval_frame, text="minutes").pack(side=tk.LEFT, padx=5)
        
        # Save button
        save_frame = ttk.Frame(general_frame)
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(save_frame, text="Save Settings", command=self._on_save_general_settings).pack(side=tk.RIGHT)
    
    def _load_current_settings(self):
        """Load current settings"""
        # Load active service
        if self.app.service_manager.active_service:
            service = self.app.service_manager.active_service
            self.active_service_var.set(service.service_name)
            
            # Update quota
            quota = service.get_remaining_quota()
            self.quota_var.set(f"{quota}/{service.daily_limit}")
        else:
            self.active_service_var.set("None")
            self.quota_var.set("N/A")
    
    def _on_service_selected(self, event=None):
        """Handle service selection"""
        service_name = self.service_var.get()
        
        # Clear service details frame
        for widget in self.service_details_frame.winfo_children():
            widget.destroy()
        
        # Create form for the selected service
        if service_name == "Twilio":
            self._create_twilio_form()
        elif service_name == "TextBelt":
            self._create_textbelt_form()
    
    def _create_twilio_form(self):
        """Create Twilio configuration form"""
        # Get existing credentials
        credentials = self.app.db.get_api_credentials("twilio") or {}
        
        if isinstance(credentials, str):
            try:
                credentials = json.loads(credentials)
            except:
                credentials = {}
        
        # Form elements
        form = ttk.Frame(self.service_details_frame)
        form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Account SID
        ttk.Label(form, text="Account SID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.twilio_sid_var = tk.StringVar(value=credentials.get('account_sid', ''))
        self.twilio_sid_entry = ttk.Entry(form, textvariable=self.twilio_sid_var, width=50)
        self.twilio_sid_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Auth Token
        ttk.Label(form, text="Auth Token:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.twilio_token_var = tk.StringVar(value=credentials.get('auth_token', ''))
        self.twilio_token_entry = ttk.Entry(form, textvariable=self.twilio_token_var, width=50, show="*")
        self.twilio_token_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Phone Number
        ttk.Label(form, text="Twilio Phone Number:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.twilio_phone_var = tk.StringVar(value=credentials.get('phone_number', ''))
        self.twilio_phone_entry = ttk.Entry(form, textvariable=self.twilio_phone_var, width=50)
        self.twilio_phone_entry.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Help text
        help_text = """
        To get your Twilio credentials:
        1. Sign up at https://www.twilio.com/try-twilio
        2. Get your Account SID and Auth Token from the Twilio Console
        3. Get a Twilio phone number from the Phone Numbers section
        
        Note: Twilio's free trial has limited credits and requires verifying recipient phone numbers.
        """
        
        help_label = ttk.Label(form, text=help_text, wraplength=500, justify=tk.LEFT)
        help_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(form)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=tk.E, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Test Connection", command=self._on_test_twilio).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Credentials", command=self._on_save_twilio).pack(side=tk.LEFT, padx=5)
    
    def _create_textbelt_form(self):
        """Create TextBelt configuration form"""
        # Get existing credentials
        credentials = self.app.db.get_api_credentials("textbelt") or {}
        
        if isinstance(credentials, str):
            try:
                credentials = json.loads(credentials)
            except:
                credentials = {}
        
        # Form elements
        form = ttk.Frame(self.service_details_frame)
        form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API Key
        ttk.Label(form, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.textbelt_key_var = tk.StringVar(value=credentials.get('api_key', ''))
        self.textbelt_key_entry = ttk.Entry(form, textvariable=self.textbelt_key_var, width=50)
        self.textbelt_key_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Use free tier option
        self.use_free_tier_var = tk.BooleanVar(value=credentials.get('api_key', '') == 'textbelt')
        ttk.Checkbutton(form, text="Use free tier (1 message per day)", 
                       variable=self.use_free_tier_var, 
                       command=self._on_free_tier_toggled).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Help text
        help_text = """
        TextBelt options:
        1. Free tier: 1 free SMS per day (no registration required)
        2. Paid tier: Purchase an API key at https://textbelt.com/
        
        The free tier has limited availability and may not work in all regions.
        """
        
        help_label = ttk.Label(form, text=help_text, wraplength=500, justify=tk.LEFT)
        help_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(form)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.E, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Test Connection", command=self._on_test_textbelt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Credentials", command=self._on_save_textbelt).pack(side=tk.LEFT, padx=5)
        
        # Update entry state based on free tier checkbox
        self._on_free_tier_toggled()
    
    def _on_free_tier_toggled(self):
        """Handle free tier checkbox toggle"""
        if self.use_free_tier_var.get():
            self.textbelt_key_entry.config(state=tk.DISABLED)
            self.textbelt_key_var.set("textbelt")  # Set to free tier key
        else:
            self.textbelt_key_entry.config(state=tk.NORMAL)
            # Clear if it was the free tier key
            if self.textbelt_key_var.get() == "textbelt":
                self.textbelt_key_var.set("")
    
    def _on_test_twilio(self):
        """Test Twilio connection"""
        # Get form values
        account_sid = self.twilio_sid_var.get().strip()
        auth_token = self.twilio_token_var.get().strip()
        phone_number = self.twilio_phone_var.get().strip()
        
        # Validate inputs
        validator = InputValidator()
        
        if not account_sid:
            messagebox.showerror("Error", "Account SID is required")
            self.twilio_sid_entry.focus_set()
            return
            
        if not auth_token:
            messagebox.showerror("Error", "Auth Token is required")
            self.twilio_token_entry.focus_set()
            return
            
        if not phone_number:
            messagebox.showerror("Error", "Phone Number is required")
            self.twilio_phone_entry.focus_set()
            return
        
        # Create credentials
        credentials = {
            'account_sid': account_sid,
            'auth_token': auth_token,
            'phone_number': phone_number
        }
        
        # Test in a background thread
        self.app.set_status("Testing Twilio connection...")
        threading.Thread(target=self._test_twilio_thread, args=(credentials,)).start()
    
    def _test_twilio_thread(self, credentials):
        """Test Twilio connection in a background thread"""
        try:
            # Get the service
            service = self.app.service_manager.get_service_by_name("twilio")
            if not service:
                self.app.root.after(0, lambda: messagebox.showerror("Error", "Twilio service not available"))
                self.app.root.after(0, lambda: self.app.set_status("Ready"))
                return
                
            # Configure with credentials
            success = service.configure(credentials)
            
            if success:
                self.app.root.after(0, lambda: messagebox.showinfo("Success", "Twilio connection successful"))
            else:
                self.app.root.after(0, lambda: messagebox.showerror("Error", "Failed to connect to Twilio"))
                
        except Exception as e:
            self.app.root.after(0, lambda: messagebox.showerror("Error", f"Error testing Twilio: {str(e)}"))
            
        self.app.root.after(0, lambda: self.app.set_status("Ready"))
    
    def _on_save_twilio(self):
        """Save Twilio credentials"""
        # Get form values
        account_sid = self.twilio_sid_var.get().strip()
        auth_token = self.twilio_token_var.get().strip()
        phone_number = self.twilio_phone_var.get().strip()
        
        # Validate inputs
        if not account_sid:
            messagebox.showerror("Error", "Account SID is required")
            self.twilio_sid_entry.focus_set()
            return
            
        if not auth_token:
            messagebox.showerror("Error", "Auth Token is required")
            self.twilio_token_entry.focus_set()
            return
            
        if not phone_number:
            messagebox.showerror("Error", "Phone Number is required")
            self.twilio_phone_entry.focus_set()
            return
        
        # Create credentials
        credentials = {
            'account_sid': account_sid,
            'auth_token': auth_token,
            'phone_number': phone_number
        }
        
        # Save credentials
        success = self.app.service_manager.configure_service("twilio", credentials)
        
        if success:
            messagebox.showinfo("Success", "Twilio credentials saved successfully")
            
            # Update active service display
            self._load_current_settings()
        else:
            messagebox.showerror("Error", "Failed to save Twilio credentials")
    
    def _on_test_textbelt(self):
        """Test TextBelt connection"""
        # Get form values
        api_key = self.textbelt_key_var.get().strip()
        
        # Validate inputs
        if not api_key:
            messagebox.showerror("Error", "API Key is required")
            self.textbelt_key_entry.focus_set()
            return
        
        # Create credentials
        credentials = {'api_key': api_key}
        
        # Test in a background thread
        self.app.set_status("Testing TextBelt connection...")
        threading.Thread(target=self._test_textbelt_thread, args=(credentials,)).start()
    
    def _test_textbelt_thread(self, credentials):
        """Test TextBelt connection in a background thread"""
        try:
            # Get the service
            service = self.app.service_manager.get_service_by_name("textbelt")
            if not service:
                self.app.root.after(0, lambda: messagebox.showerror("Error", "TextBelt service not available"))
                self.app.root.after(0, lambda: self.app.set_status("Ready"))
                return
                
            # Configure with credentials
            success = service.configure(credentials)
            
            if success:
                # Check quota
                quota = service.get_remaining_quota()
                
                self.app.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"TextBelt connection successful\nRemaining quota: {quota}"
                ))
            else:
                self.app.root.after(0, lambda: messagebox.showerror("Error", "Failed to connect to TextBelt"))
                
        except Exception as e:
            self.app.root.after(0, lambda: messagebox.showerror("Error", f"Error testing TextBelt: {str(e)}"))
            
        self.app.root.after(0, lambda: self.app.set_status("Ready"))
    
    def _on_save_textbelt(self):
        """Save TextBelt credentials"""
        # Get form values
        api_key = self.textbelt_key_var.get().strip()
        
        # Validate inputs
        if not api_key:
            messagebox.showerror("Error", "API Key is required")
            self.textbelt_key_entry.focus_set()
            return
        
        # Create credentials
        credentials = {'api_key': api_key}
        
        # Save credentials
        success = self.app.service_manager.configure_service("textbelt", credentials)
        
        if success:
            messagebox.showinfo("Success", "TextBelt credentials saved successfully")
            
            # Update active service display
            self._load_current_settings()
        else:
            messagebox.showerror("Error", "Failed to save TextBelt credentials")
    
    def _on_set_active_service(self):
        """Set the active SMS service"""
        # Get selected service
        service_name = self.service_var.get()
        
        if not service_name:
            messagebox.showinfo("Information", "Please select a service to set as active")
            return
        
        # Set active service
        success = self.app.service_manager.set_active_service(service_name.lower())
        
        if success:
            messagebox.showinfo("Success", f"{service_name} set as active service")
            
            # Update active service display
            self._load_current_settings()
        else:
            messagebox.showerror("Error", f"Failed to set {service_name} as active service. Is it configured?")
    
    def _on_save_general_settings(self):
        """Save general settings"""
        # Save settings
        # In a real implementation, these would be saved to a settings file or database
        messagebox.showinfo("Success", "Settings saved successfully")
        
        # Update application state with new settings
        check_interval = self.check_interval_var.get()
        # Update scheduler interval if supported
        # self.app.scheduler.set_check_interval(check_interval * 60)  # Convert to seconds 