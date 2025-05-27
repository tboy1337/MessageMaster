"""
System Tray module for SMS application
Provides cross-platform system tray functionality
"""
import os
import sys
import platform
from pathlib import Path

class SystemTrayIcon:
    """Cross-platform system tray icon implementation"""
    
    def __init__(self, app, icon_path=None, tooltip="MessageMaster"):
        """
        Initialize the system tray icon
        
        Args:
            app: Main application instance
            icon_path: Path to icon file
            tooltip: Tooltip text for the tray icon
        """
        self.app = app
        self.icon_path = icon_path
        self.tooltip = tooltip
        self.tray_icon = None
        self.system = platform.system()
        
        # Initialize appropriate system tray implementation
        if self.system == "Windows":
            self._init_windows_tray()
        elif self.system == "Darwin":  # macOS
            self._init_macos_tray()
        else:  # Linux and others
            self._init_gtk_tray()
    
    def _init_windows_tray(self):
        """Initialize Windows system tray using pystray"""
        try:
            import pystray
            from PIL import Image
            
            # Load icon
            icon_img = self._load_icon_image()
            
            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("Show", self._on_show_window),
                pystray.MenuItem("Send Message", self._on_new_message),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self._on_exit)
            )
            
            # Create tray icon
            self.tray_icon = pystray.Icon("sms_sender", icon_img, self.tooltip, menu)
            
            # Run in a separate thread
            self.tray_icon.run_detached()
            
        except ImportError:
            print("pystray or Pillow not available. System tray functionality disabled.")
    
    def _init_macos_tray(self):
        """Initialize macOS system tray using rumps"""
        try:
            import rumps
            
            # Subclass rumps.App
            class SMSTrayApp(rumps.App):
                def __init__(self, parent, name, icon, quit_button=True):
                    super(SMSTrayApp, self).__init__(name, icon=icon, quit_button=quit_button)
                    self.parent = parent
                
                @rumps.clicked("Show")
                def show(self, _):
                    self.parent._on_show_window()
                
                @rumps.clicked("Send Message")
                def new_message(self, _):
                    self.parent._on_new_message()
            
            # Create tray app
            icon_path = self.icon_path or self._get_default_icon_path()
            self.tray_icon = SMSTrayApp(self, self.tooltip, icon_path)
            
            # Start in a separate thread
            import threading
            self.tray_thread = threading.Thread(target=self.tray_icon.run)
            self.tray_thread.daemon = True
            self.tray_thread.start()
            
        except ImportError:
            print("rumps not available. System tray functionality disabled.")
    
    def _init_gtk_tray(self):
        """Initialize GTK system tray using PyGObject"""
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            gi.require_version('AppIndicator3', '0.1')
            from gi.repository import Gtk, AppIndicator3
            
            # Create indicator
            icon_path = self.icon_path or self._get_default_icon_path()
            self.indicator = AppIndicator3.Indicator.new(
                "sms-sender",
                icon_path,
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            
            # Create menu
            menu = Gtk.Menu()
            
            # Show item
            show_item = Gtk.MenuItem.new_with_label("Show")
            show_item.connect("activate", self._on_show_window)
            menu.append(show_item)
            
            # New message item
            new_msg_item = Gtk.MenuItem.new_with_label("Send Message")
            new_msg_item.connect("activate", self._on_new_message)
            menu.append(new_msg_item)
            
            # Separator
            separator = Gtk.SeparatorMenuItem()
            menu.append(separator)
            
            # Exit item
            exit_item = Gtk.MenuItem.new_with_label("Exit")
            exit_item.connect("activate", self._on_exit)
            menu.append(exit_item)
            
            menu.show_all()
            self.indicator.set_menu(menu)
            self.tray_icon = self.indicator
            
        except (ImportError, ValueError):
            print("PyGObject or AppIndicator3 not available. System tray functionality disabled.")
    
    def _load_icon_image(self):
        """Load icon as PIL Image"""
        try:
            from PIL import Image
            
            # If icon path provided, use it
            if self.icon_path and os.path.exists(self.icon_path):
                return Image.open(self.icon_path)
            
            # Use default icon path
            default_path = self._get_default_icon_path()
            if os.path.exists(default_path):
                return Image.open(default_path)
            
            # Create a simple colored square as fallback
            img = Image.new('RGB', (64, 64), color=(74, 108, 212))
            return img
            
        except ImportError:
            print("Pillow not available. Cannot load icon.")
            return None
    
    def _get_default_icon_path(self):
        """Get default icon path"""
        # Check for icon in assets directory
        script_dir = Path(__file__).parent
        icon_path = script_dir / "assets" / "sms_icon.png"
        
        if icon_path.exists():
            return str(icon_path)
        
        # Try ICO for Windows
        if platform.system() == "Windows":
            ico_path = script_dir / "assets" / "sms_icon.ico"
            if ico_path.exists():
                return str(ico_path)
        
        return None
    
    def _on_show_window(self, *args):
        """Show the main application window"""
        if hasattr(self.app, 'root') and self.app.root:
            self.app.root.deiconify()
            self.app.root.lift()
            self.app.root.focus_force()
    
    def _on_new_message(self, *args):
        """Open new message tab"""
        if hasattr(self.app, 'root') and self.app.root:
            self.app.root.deiconify()
            self.app.notebook.select(0)  # Select message tab
            self.app.root.lift()
            self.app.root.focus_force()
    
    def _on_exit(self, *args):
        """Exit the application"""
        if hasattr(self.app, 'root') and self.app.root:
            self.app.root.destroy()
    
    def shutdown(self):
        """Shutdown the tray icon"""
        if self.tray_icon:
            if hasattr(self.tray_icon, 'stop'):
                self.tray_icon.stop()
            elif hasattr(self.tray_icon, 'remove'):
                self.tray_icon.remove()
            self.tray_icon = None 