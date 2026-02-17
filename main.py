#!/usr/bin/env python
# RAM V1 - Roblox Account Manager (with Direct Downloader)
# Main entry point

try:
    from ui.app import RAMApp
except ImportError:
    print("[!] Note: RAMApp UI module not found. This is expected if this is just the downloader component.")
    
    # Create a placeholder if needed
    class RAMApp:
        def mainloop(self):
            print("[!] RAM V1 UI not available - running in downloader-only mode")

def run_ram_app():
    """Run the original RAM V1 application"""
    try:
        app = RAMApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   Starting RAM V1 - Roblox Account Manager")
    print("=" * 60)
    print()
    
    run_ram_app()
