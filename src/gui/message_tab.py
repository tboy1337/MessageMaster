"""
Message Tab - UI for composing and sending SMS messages
"""
import tkinter as tk
from tkinter import ttk, messagebox
import pycountry
import phonenumbers
from datetime import datetime

class MessageTab:
    """Message composition and sending tab"""
    
    def __init__(self, parent, app):
        """Initialize the message tab"""
        self.parent = parent
        self.app = app
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create components
        self._create_components()
        
        # Populate countries
        self._populate_countries()
        
        # Set up validation and bindings
        self._setup_validation()
    
    def _create_components(self):
        """Create tab components"""
        # Recipient section
        recipient_frame = ttk.LabelFrame(self.frame, text="Recipient")
        recipient_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Country dropdown
        ttk.Label(recipient_frame, text="Country:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(recipient_frame, textvariable=self.country_var, state="readonly", width=40)
        self.country_dropdown.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Phone number entry
        ttk.Label(recipient_frame, text="Phone Number:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.recipient_var = tk.StringVar()
        self.recipient_entry = ttk.Entry(recipient_frame, textvariable=self.recipient_var, width=40)
        self.recipient_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Contact button
        self.contact_button = ttk.Button(recipient_frame, text="Choose Contact", command=self._on_choose_contact)
        self.contact_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Message section
        message_frame = ttk.LabelFrame(self.frame, text="Message")
        message_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Template dropdown
        template_frame = ttk.Frame(message_frame)
        template_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(template_frame, text="Template:").pack(side=tk.LEFT, padx=5)
        self.template_var = tk.StringVar()
        self.template_dropdown = ttk.Combobox(template_frame, textvariable=self.template_var, state="readonly", width=40)
        self.template_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Message text entry
        text_frame = ttk.Frame(message_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.message_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        self.message_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, command=self.message_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.message_text.config(yscrollcommand=scrollbar.set)
        
        # Character counter
        counter_frame = ttk.Frame(message_frame)
        counter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.char_count_var = tk.StringVar(value="0/160 characters")
        ttk.Label(counter_frame, textvariable=self.char_count_var).pack(side=tk.RIGHT, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Send button
        self.send_button = ttk.Button(button_frame, text="Send Message", command=self._on_send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Schedule button
        self.schedule_button = ttk.Button(button_frame, text="Schedule", command=self._on_schedule_message)
        self.schedule_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Clear button
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self._on_clear)
        self.clear_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def _populate_countries(self):
        """Populate the country dropdown"""
        # Get all countries from pycountry
        countries = []
        for country in pycountry.countries:
            # Try to get the country calling code
            try:
                phone_code = phonenumbers.country_code_for_region(country.alpha_2)
                if phone_code:
                    countries.append(f"{country.name} (+{phone_code})")
            except:
                pass
                
        # Sort countries alphabetically
        countries.sort()
        
        # Set dropdown values
        self.country_dropdown['values'] = countries
        
        # Set default to United States
        for i, country in enumerate(countries):
            if country.startswith("United States"):
                self.country_dropdown.current(i)
                break
    
    def _setup_validation(self):
        """Set up validation and event bindings"""
        # Bind text changes to update character count
        self.message_text.bind("<KeyRelease>", self._update_char_count)
        
        # Bind template selection
        self.template_dropdown.bind("<<ComboboxSelected>>", self._on_template_selected)
        
        # Load templates
        self._load_templates()
    
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
    
    def _on_choose_contact(self):
        """Open contact selection dialog"""
        # Switch to contacts tab
        self.app.notebook.select(1)  # Index 1 is the Contacts tab
        
        # Tell the contacts tab we're selecting for the message tab
        self.app.tabs["contacts"].set_selection_mode(True)
    
    def _on_send_message(self):
        """Handle send message button click"""
        # Get recipient and message
        recipient = self.recipient_var.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        # Check if fields are filled
        if not recipient:
            messagebox.showerror("Error", "Please enter a recipient phone number")
            self.recipient_entry.focus_set()
            return
            
        if not message:
            messagebox.showerror("Error", "Please enter a message")
            self.message_text.focus_set()
            return
        
        # Get the country code
        country = self.country_var.get()
        country_code = ""
        if country:
            # Extract the code from the format "Country Name (+123)"
            start = country.rfind("(+")
            if start >= 0:
                end = country.rfind(")")
                if end > start:
                    country_code = country[start+1:end].strip()
        
        # Format the recipient with country code if needed
        if country_code and not recipient.startswith("+"):
            recipient = f"{country_code}{recipient}"
            
        # Send the message
        self.app.send_message(recipient, message)
    
    def _on_schedule_message(self):
        """Open schedule dialog for this message"""
        # Get recipient and message
        recipient = self.recipient_var.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        # Check if fields are filled
        if not recipient:
            messagebox.showerror("Error", "Please enter a recipient phone number")
            self.recipient_entry.focus_set()
            return
            
        if not message:
            messagebox.showerror("Error", "Please enter a message")
            self.message_text.focus_set()
            return
        
        # Get the country code
        country = self.country_var.get()
        country_code = ""
        if country:
            # Extract the code from the format "Country Name (+123)"
            start = country.rfind("(+")
            if start >= 0:
                end = country.rfind(")")
                if end > start:
                    country_code = country[start+1:end].strip()
        
        # Format the recipient with country code if needed
        if country_code and not recipient.startswith("+"):
            recipient = f"{country_code}{recipient}"
        
        # Switch to scheduler tab
        self.app.notebook.select(3)  # Index 3 is the Scheduler tab
        
        # Populate the scheduler with our message
        self.app.tabs["schedule"].set_new_scheduled_message(recipient, message)
    
    def _on_clear(self):
        """Clear the form"""
        self.recipient_var.set("")
        self.message_text.delete("1.0", tk.END)
        self.template_dropdown.current(0)
        self._update_char_count()
        self.recipient_entry.focus_set()
    
    def set_recipient(self, phone):
        """Set the recipient field"""
        self.recipient_var.set(phone)
        self.message_text.focus_set() 