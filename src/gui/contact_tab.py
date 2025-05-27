"""
Contact Tab - UI for managing contacts
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pycountry
import phonenumbers
import csv
import io

class ContactTab:
    """Contact management tab"""
    
    def __init__(self, parent, app):
        """Initialize the contacts tab"""
        self.parent = parent
        self.app = app
        
        # Selection mode flag
        self.selection_mode = False
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create components
        self._create_components()
        
        # Load contacts
        self.load_contacts()
    
    def _create_components(self):
        """Create tab components"""
        # Top frame for search and actions
        top_frame = ttk.Frame(self.frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search field
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.search_button = ttk.Button(search_frame, text="Search", command=self._on_search)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.add_button = ttk.Button(buttons_frame, text="Add Contact", command=self._on_add_contact)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.import_button = ttk.Button(buttons_frame, text="Import", command=self._on_import)
        self.import_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(buttons_frame, text="Export", command=self._on_export)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Contact list
        list_frame = ttk.Frame(self.frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        self.contact_tree = ttk.Treeview(list_frame, columns=("name", "phone", "country"), 
                                         show="headings", selectmode="browse")
        
        # Define headings
        self.contact_tree.heading("name", text="Name")
        self.contact_tree.heading("phone", text="Phone")
        self.contact_tree.heading("country", text="Country")
        
        # Define columns
        self.contact_tree.column("name", width=200, anchor=tk.W)
        self.contact_tree.column("phone", width=150, anchor=tk.W)
        self.contact_tree.column("country", width=100, anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.contact_tree.yview)
        self.contact_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.contact_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.contact_tree.bind("<Double-1>", self._on_contact_selected)
        
        # Context menu
        self._create_context_menu()
        
        # Details/edit frame
        details_frame = ttk.LabelFrame(self.frame, text="Contact Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Contact details form
        form_frame = ttk.Frame(details_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Name field
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Phone field
        ttk.Label(form_frame, text="Phone:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(form_frame, textvariable=self.phone_var, width=30)
        self.phone_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Country dropdown
        ttk.Label(form_frame, text="Country:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(form_frame, textvariable=self.country_var, state="readonly", width=30)
        self.country_dropdown.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Notes field
        ttk.Label(form_frame, text="Notes:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(form_frame, textvariable=self.notes_var, width=50)
        self.notes_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Action buttons
        form_buttons = ttk.Frame(form_frame)
        form_buttons.grid(row=4, column=0, columnspan=3, sticky=tk.E, padx=5, pady=5)
        
        self.save_button = ttk.Button(form_buttons, text="Save", command=self._on_save_contact)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(form_buttons, text="Delete", command=self._on_delete_contact)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(form_buttons, text="Clear", command=self._clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Populate countries
        self._populate_countries()
        
        # Initialize form state
        self._clear_form()
    
    def _create_context_menu(self):
        """Create context menu for contact list"""
        self.context_menu = tk.Menu(self.contact_tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self._on_edit_contact)
        self.context_menu.add_command(label="Delete", command=self._on_delete_contact)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Send Message", command=self._on_send_to_contact)
        
        # Bind right-click event
        self.contact_tree.bind("<Button-3>", self._on_context_menu)
    
    def _on_context_menu(self, event):
        """Show context menu on right-click"""
        # Select the item under the cursor
        item = self.contact_tree.identify_row(event.y)
        if item:
            self.contact_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _populate_countries(self):
        """Populate the country dropdown"""
        # Get all countries from pycountry
        countries = []
        for country in pycountry.countries:
            # Try to get the country calling code
            try:
                phone_code = phonenumbers.country_code_for_region(country.alpha_2)
                if phone_code:
                    countries.append((country.alpha_2, f"{country.name} (+{phone_code})"))
            except:
                pass
                
        # Sort countries alphabetically by name
        countries.sort(key=lambda x: x[1])
        
        # Set dropdown values
        self.country_dropdown['values'] = [country[1] for country in countries]
        self.country_codes = {country[1]: country[0] for country in countries}
        
        # Set default to United States
        for i, country in enumerate(self.country_dropdown['values']):
            if country.startswith("United States"):
                self.country_dropdown.current(i)
                break
    
    def load_contacts(self):
        """Load contacts from the database"""
        # Clear existing items
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)
            
        # Get all contacts
        contacts = self.app.contact_manager.get_all_contacts()
        
        # Add to treeview
        for contact in contacts:
            # Get country name from code
            country_name = contact['country_code']
            try:
                country = pycountry.countries.get(alpha_2=contact['country_code'])
                if country:
                    country_name = country.name
            except:
                pass
                
            self.contact_tree.insert('', tk.END, iid=str(contact['id']), 
                                    values=(contact['name'], contact['phone'], country_name))
    
    def _on_search(self):
        """Handle search button click"""
        query = self.search_var.get().strip()
        
        if not query:
            # If query is empty, load all contacts
            self.load_contacts()
            return
            
        # Search contacts
        contacts = self.app.contact_manager.search_contacts(query)
        
        # Clear existing items
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)
            
        # Add results to treeview
        for contact in contacts:
            # Get country name from code
            country_name = contact['country_code']
            try:
                country = pycountry.countries.get(alpha_2=contact['country_code'])
                if country:
                    country_name = country.name
            except:
                pass
                
            self.contact_tree.insert('', tk.END, iid=str(contact['id']), 
                                    values=(contact['name'], contact['phone'], country_name))
    
    def _on_add_contact(self):
        """Handle add contact button click"""
        self._clear_form()
    
    def _on_edit_contact(self):
        """Handle edit contact action"""
        # Get selected item
        selected = self.contact_tree.selection()
        if not selected:
            messagebox.showinfo("Information", "Please select a contact to edit")
            return
            
        # Get contact ID
        contact_id = int(selected[0])
        
        # Load contact details
        contact = self.app.contact_manager.get_contact(contact_id)
        if not contact:
            messagebox.showerror("Error", "Failed to load contact details")
            return
            
        # Populate form
        self.contact_id = contact_id
        self.name_var.set(contact['name'])
        self.phone_var.set(contact['phone'])
        self.notes_var.set(contact.get('notes', ''))
        
        # Set country
        country_code = contact.get('country_code', 'US')
        country_found = False
        
        for i, country in enumerate(self.country_dropdown['values']):
            # For each country in dropdown, check if it matches the code
            for code, name in self.country_codes.items():
                if name == country_code and code == country:
                    self.country_dropdown.current(i)
                    country_found = True
                    break
                    
            if country_found:
                break
                
        # Enable form fields and buttons
        self._enable_form(True)
        self.name_entry.focus_set()
    
    def _on_contact_selected(self, event):
        """Handle contact selection via double-click"""
        # Get selected item
        selected = self.contact_tree.selection()
        if not selected:
            return
            
        # Get contact ID
        contact_id = int(selected[0])
        
        if self.selection_mode:
            # If in selection mode, load the contact to the message tab
            self.app.load_contact_to_message(contact_id)
            self.selection_mode = False
            return
            
        # Otherwise, load for editing
        self._on_edit_contact()
    
    def _on_save_contact(self):
        """Handle save contact button click"""
        # Get form values
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        country = self.country_var.get()
        notes = self.notes_var.get()
        
        # Validate required fields
        if not name:
            messagebox.showerror("Error", "Name is required")
            self.name_entry.focus_set()
            return
            
        if not phone:
            messagebox.showerror("Error", "Phone number is required")
            self.phone_entry.focus_set()
            return
            
        if not country:
            messagebox.showerror("Error", "Country is required")
            self.country_dropdown.focus_set()
            return
        
        # Get country code from dropdown selection
        country_code = self.country_codes.get(country, "US")
        
        # Save contact
        if hasattr(self, 'contact_id'):
            # Update existing contact
            success = self.app.contact_manager.update_contact(
                self.contact_id, name, phone, country_code, notes)
        else:
            # Add new contact
            success = self.app.contact_manager.add_contact(name, phone, country_code, notes)
        
        if success:
            messagebox.showinfo("Success", "Contact saved successfully")
            self._clear_form()
            self.load_contacts()
        else:
            messagebox.showerror("Error", "Failed to save contact")
    
    def _on_delete_contact(self):
        """Handle delete contact button click"""
        if hasattr(self, 'contact_id'):
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?"):
                # Delete contact
                success = self.app.contact_manager.delete_contact(self.contact_id)
                
                if success:
                    messagebox.showinfo("Success", "Contact deleted successfully")
                    self._clear_form()
                    self.load_contacts()
                else:
                    messagebox.showerror("Error", "Failed to delete contact")
        else:
            # No contact loaded
            selected = self.contact_tree.selection()
            if selected:
                # Get contact ID
                contact_id = int(selected[0])
                
                # Confirm deletion
                if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?"):
                    # Delete contact
                    success = self.app.contact_manager.delete_contact(contact_id)
                    
                    if success:
                        messagebox.showinfo("Success", "Contact deleted successfully")
                        self.load_contacts()
                    else:
                        messagebox.showerror("Error", "Failed to delete contact")
            else:
                messagebox.showinfo("Information", "Please select a contact to delete")
    
    def _on_import(self):
        """Handle import button click"""
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Import Contacts",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Read CSV file
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                csv_data = f.read()
                
            # Import contacts
            success_count, errors = self.app.contact_manager.import_contacts_from_csv(csv_data)
            
            # Show results
            if errors:
                error_msg = "\n".join(errors[:10])
                if len(errors) > 10:
                    error_msg += f"\n... and {len(errors) - 10} more errors"
                    
                messagebox.showwarning("Import Results", 
                                      f"Imported {success_count} contacts with {len(errors)} errors:\n\n{error_msg}")
            else:
                messagebox.showinfo("Import Results", f"Successfully imported {success_count} contacts")
                
            # Reload contacts
            self.load_contacts()
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import contacts: {str(e)}")
    
    def _on_export(self):
        """Handle export button click"""
        # Open file dialog
        file_path = filedialog.asksaveasfilename(
            title="Export Contacts",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Export contacts
            csv_data = self.app.contact_manager.export_contacts_to_csv()
            
            # Write to file
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_data)
                
            messagebox.showinfo("Export Success", "Contacts exported successfully")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export contacts: {str(e)}")
    
    def _on_send_to_contact(self):
        """Send message to selected contact"""
        # Get selected item
        selected = self.contact_tree.selection()
        if not selected:
            messagebox.showinfo("Information", "Please select a contact first")
            return
            
        # Get contact ID
        contact_id = int(selected[0])
        
        # Load contact to message tab
        self.app.load_contact_to_message(contact_id)
    
    def _clear_form(self):
        """Clear the contact form"""
        # Clear form variables
        self.name_var.set("")
        self.phone_var.set("")
        self.notes_var.set("")
        
        # Reset country to default
        for i, country in enumerate(self.country_dropdown['values']):
            if country.startswith("United States"):
                self.country_dropdown.current(i)
                break
        
        # Clear the stored contact ID
        if hasattr(self, 'contact_id'):
            delattr(self, 'contact_id')
            
        # Enable form
        self._enable_form(True)
    
    def _enable_form(self, enabled=True):
        """Enable or disable form fields"""
        state = "normal" if enabled else "disabled"
        
        self.name_entry.config(state=state)
        self.phone_entry.config(state=state)
        self.country_dropdown.config(state="readonly" if enabled else "disabled")
        self.notes_entry.config(state=state)
        
        self.save_button.config(state=state)
        self.delete_button.config(state=state)
    
    def set_selection_mode(self, mode=True):
        """Set selection mode for choosing a contact"""
        self.selection_mode = mode
        
        if mode:
            self.app.set_status("Select a contact for the message")
        else:
            self.app.set_status("Ready") 