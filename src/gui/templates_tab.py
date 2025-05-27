"""
Templates Tab - UI for managing message templates
"""
import tkinter as tk
from tkinter import ttk, messagebox

class TemplatesTab:
    """Message templates management tab"""
    
    def __init__(self, parent, app):
        """Initialize the templates tab"""
        self.parent = parent
        self.app = app
        
        # Create frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create components
        self._create_components()
        
        # Load templates
        self.load_templates()
    
    def _create_components(self):
        """Create tab components"""
        # Split into left and right panels
        paned_window = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for template list
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=1)
        
        # Right panel for template editor
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=2)
        
        # Create components for each panel
        self._create_list_panel(left_frame)
        self._create_editor_panel(right_frame)
    
    def _create_list_panel(self, parent):
        """Create the template list panel"""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="Templates", style="Title.TLabel").pack(side=tk.LEFT)
        
        new_button = ttk.Button(header_frame, text="New Template", command=self._on_new_template)
        new_button.pack(side=tk.RIGHT)
        
        # Template list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create listbox
        self.template_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.template_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        self.template_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.template_listbox.bind("<<ListboxSelect>>", self._on_template_selected)
        
        # Create context menu
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Create context menu for template list"""
        self.context_menu = tk.Menu(self.template_listbox, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self._on_edit_template)
        self.context_menu.add_command(label="Delete", command=self._on_delete_template)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Use in Message", command=self._on_use_in_message)
        
        # Bind right-click event
        self.template_listbox.bind("<Button-3>", self._on_context_menu)
    
    def _on_context_menu(self, event):
        """Show context menu on right-click"""
        # Get the index under the cursor
        index = self.template_listbox.nearest(event.y)
        if index >= 0:
            # Select the item
            self.template_listbox.selection_clear(0, tk.END)
            self.template_listbox.selection_set(index)
            self.template_listbox.activate(index)
            
            # Show context menu
            self.context_menu.post(event.x_root, event.y_root)
    
    def _create_editor_panel(self, parent):
        """Create the template editor panel"""
        # Header
        self.editor_header = ttk.Label(parent, text="New Template", style="Title.TLabel")
        self.editor_header.pack(padx=5, pady=5, anchor=tk.W)
        
        # Form frame
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Template name
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(name_frame, text="Template Name:").pack(side=tk.LEFT, padx=5)
        
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=40)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Template content
        content_frame = ttk.LabelFrame(form_frame, text="Template Content")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message text editor
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.content_text = tk.Text(text_frame, wrap=tk.WORD, height=15)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Character counter
        counter_frame = ttk.Frame(content_frame)
        counter_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.char_count_var = tk.StringVar(value="0/160 characters")
        ttk.Label(counter_frame, textvariable=self.char_count_var).pack(side=tk.RIGHT)
        
        # Bind text changes to update character count
        self.content_text.bind("<KeyRelease>", self._update_char_count)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.save_button = ttk.Button(button_frame, text="Save Template", command=self._on_save_template)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self._clear_editor)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def _update_char_count(self, event=None):
        """Update the character count display"""
        text = self.content_text.get("1.0", tk.END)
        count = len(text.strip())
        
        # SMS messages are typically limited to 160 characters
        # but can be sent as multiple messages
        parts = count // 160 + (1 if count % 160 > 0 else 0)
        
        if parts > 1:
            self.char_count_var.set(f"{count} characters ({parts} messages)")
        else:
            self.char_count_var.set(f"{count}/160 characters")
    
    def load_templates(self):
        """Load templates from the database"""
        # Clear existing items
        self.template_listbox.delete(0, tk.END)
        
        # Get templates from database
        templates = self.app.db.get_templates()
        
        # Store templates for reference
        self.templates = {}
        
        # Add to listbox
        for template in templates:
            template_id = template['id']
            name = template['name']
            
            self.template_listbox.insert(tk.END, name)
            
            # Store template details
            self.templates[name] = {
                'id': template_id,
                'content': template['content']
            }
    
    def _on_template_selected(self, event=None):
        """Handle template selection"""
        # Get selected item
        selected = self.template_listbox.curselection()
        if not selected:
            return
            
        # Get template name
        index = selected[0]
        name = self.template_listbox.get(index)
        
        # Load template for editing
        self._load_template_for_editing(name)
    
    def _load_template_for_editing(self, name):
        """Load a template into the editor"""
        if name not in self.templates:
            return
            
        # Get template details
        template = self.templates[name]
        
        # Set form fields
        self.name_var.set(name)
        
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", template['content'])
        
        # Update character count
        self._update_char_count()
        
        # Update header
        self.editor_header.config(text=f"Edit Template: {name}")
        
        # Store the template ID for updating
        self.editing_template_id = template['id']
    
    def _on_new_template(self):
        """Create a new template"""
        self._clear_editor()
    
    def _on_edit_template(self):
        """Edit the selected template"""
        selected = self.template_listbox.curselection()
        if not selected:
            messagebox.showinfo("Information", "Please select a template to edit")
            return
            
        # Get template name
        index = selected[0]
        name = self.template_listbox.get(index)
        
        # Load template for editing
        self._load_template_for_editing(name)
    
    def _on_delete_template(self):
        """Delete the selected template"""
        selected = self.template_listbox.curselection()
        if not selected:
            messagebox.showinfo("Information", "Please select a template to delete")
            return
            
        # Get template name
        index = selected[0]
        name = self.template_listbox.get(index)
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the template '{name}'?"):
            return
            
        # Get template ID
        template_id = self.templates[name]['id']
        
        # Delete from database
        success = self.app.db.delete_template(template_id)
        
        if success:
            messagebox.showinfo("Success", f"Template '{name}' deleted successfully")
            
            # Refresh templates
            self.load_templates()
            
            # Clear editor if we were editing this template
            if hasattr(self, 'editing_template_id') and self.editing_template_id == template_id:
                self._clear_editor()
        else:
            messagebox.showerror("Error", f"Failed to delete template '{name}'")
    
    def _on_use_in_message(self):
        """Use the selected template in a new message"""
        selected = self.template_listbox.curselection()
        if not selected:
            messagebox.showinfo("Information", "Please select a template to use")
            return
            
        # Get template name
        index = selected[0]
        name = self.template_listbox.get(index)
        
        # Get template content
        content = self.templates[name]['content']
        
        # Switch to message tab
        self.app.notebook.select(0)  # Index 0 is the Message tab
        
        # Set message content
        message_tab = self.app.tabs["message"]
        message_tab.message_text.delete("1.0", tk.END)
        message_tab.message_text.insert("1.0", content)
        message_tab._update_char_count()
    
    def _on_save_template(self):
        """Save the current template"""
        # Get form values
        name = self.name_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        # Validate inputs
        if not name:
            messagebox.showerror("Error", "Template name is required")
            self.name_entry.focus_set()
            return
            
        if not content:
            messagebox.showerror("Error", "Template content is required")
            self.content_text.focus_set()
            return
        
        # Check for duplicate name when creating new template
        if not hasattr(self, 'editing_template_id'):
            if name in self.templates:
                messagebox.showerror("Error", f"A template with the name '{name}' already exists")
                self.name_entry.focus_set()
                return
        
        # Save to database
        success = self.app.db.save_template(name, content)
        
        if success:
            messagebox.showinfo("Success", f"Template '{name}' saved successfully")
            
            # Refresh templates
            self.load_templates()
            
            # Clear editor
            self._clear_editor()
        else:
            messagebox.showerror("Error", f"Failed to save template '{name}'")
    
    def _clear_editor(self):
        """Clear the template editor"""
        # Clear form fields
        self.name_var.set("")
        self.content_text.delete("1.0", tk.END)
        
        # Update character count
        self._update_char_count()
        
        # Update header
        self.editor_header.config(text="New Template")
        
        # Remove editing ID
        if hasattr(self, 'editing_template_id'):
            delattr(self, 'editing_template_id')
            
        # Set focus
        self.name_entry.focus_set() 