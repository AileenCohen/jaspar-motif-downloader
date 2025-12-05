import sys
import os
import tkinter as tk
try:
    import requests
except ImportError:
    # Error handling moved here for clear setup instructions
    print("Error: The 'requests' library is required. Please install it with: pip install requests")
    sys.exit(1)

# The GUI logic is imported here
from motif_search_gui import JasparDownloaderApp

def main():
    """Application entry point."""
    try:
        # Check if the app is run in a way that requires file system access
        # If running in a constrained environment like some web platforms, file handling might fail.
        print("Starting JASPAR Motif Downloader...")
        app = JasparDownloaderApp()
        app.mainloop()
    except Exception as e:
        print(f"An application error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()