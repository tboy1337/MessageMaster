#!/usr/bin/env python3
"""
MessageMaster Application - Main Entry Point
"""
import os
import sys
import tkinter as tk
import argparse
import logging
from dotenv import load_dotenv

# Add the project root to the Python path if it's not already there
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv()

from src.gui.app import SMSApplication
from src.cli.cli import main as cli_main
from src.utils.logger import setup_logger
from src.services.config_service import ConfigService
from src.services.notification_service import NotificationService

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="MessageMaster")
    parser.add_argument("--minimized", action="store_true", help="Start application minimized")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", type=str, help="Path to custom config file")
    parser.add_argument("--cli", action="store_true", help="Run in command line mode")
    
    # Only parse known args to allow for CLI-specific arguments
    args, _ = parser.parse_known_args()
    return args

def main():
    """Main entry point for the MessageMaster application"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger("message_master", log_level)
    logger.info("Starting MessageMaster application")
    
    # If CLI mode is requested, run in CLI mode
    if args.cli:
        logger.info("Running in CLI mode")
        # Remove the --cli flag and call the CLI main function
        if "--cli" in sys.argv:
            sys.argv.remove("--cli")
        return cli_main()
    
    # Otherwise run in GUI mode
    logger.info("Running in GUI mode")
    
    # Initialize services
    config = ConfigService("message_master")
    notification = NotificationService("MessageMaster")
    
    # Get window settings from config
    window_width = config.get("ui.window_width", 900)
    window_height = config.get("ui.window_height", 700)
    start_minimized = args.minimized or config.get("general.start_minimized", False)
    
    # Initialize Tkinter
    root = tk.Tk()
    root.title("MessageMaster")
    
    # Set application icon
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "gui", "assets", "messagemaster_icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        logger.warning("Failed to set application icon")
    
    # Set minimum window size
    root.minsize(800, 600)
    
    # Center the window on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    
    # Create and run the application
    app = SMSApplication(root, config=config, notification=notification)
    
    # If start minimized, withdraw the window
    if start_minimized:
        root.withdraw()
        notification.send_notification(
            "MessageMaster", 
            "Application started and running in background"
        )
    
    # Save window size and position on close
    def on_close():
        if config.get("general.save_window_position", True):
            config.set("ui.window_width", root.winfo_width())
            config.set("ui.window_height", root.winfo_height())
        app._on_close()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    # Start the application
    root.mainloop()
    
    logger.info("Application shutdown")

if __name__ == "__main__":
    main() 