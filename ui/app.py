import customtkinter as 
import threading
import hashlib
from core.vault import VaultManager
from core.crypto import CryptoEngine
from core.validator import validate_cookie
from core.launcher import RobloxAutomation

class RAMApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RAM V1 - Secure Vault")
        self.geometry("950x600")
        self.configure(fg_color="#1A1625")
        self.vault = VaultManager()
        self.session_key = None
        self.launch_method = None
        self.init_ui()

    def init_ui(self):
        if not self.vault.is_initialized(): 
            self.show_auth("setup")
        else: 
            self.show_auth("login")

    def show_auth(self, mode):
        self.auth = ctk.CTkFrame(self, fg_color="#2D2640")
        self.auth.place(relx=0.5, rely=0.5, anchor="center")
        
        title = "Setup Master Password" if mode == "setup" else "Vault Locked"
        ctk.CTkLabel(self.auth, text=title, font=("Arial", 18, "bold")).pack(pady=20, padx=40)
        
        self.pe = ctk.CTkEntry(self.auth, show="*", width=200)
        self.pe.pack(pady=10)
        
        ctk.CTkButton(self.auth, text="Unlock", fg_color="#9D85FF", text_color="black", 
                      command=lambda: self.handle_auth(mode)).pack(pady=20)

    def handle_auth(self, mode):
        pw = self.pe.get()
        if not pw: 
            return
            
        if mode == "setup":
            salt = self.vault.setup_vault(pw)
            self.session_key = CryptoEngine.derive_key(pw, salt)
        else:
            data = self.vault.get_auth_data()
            if hashlib.sha256(pw.encode()).hexdigest() == data[1]:
                self.session_key = CryptoEngine.derive_key(pw, bytes.fromhex(data[0]))
        
        if self.session_key:
            self.auth.destroy() 
            self.main_view()

    def main_view(self):
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color="#2D2640", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="RAM VAULT", text_color="#9D85FF", 
                    font=("Arial", 20, "bold")).pack(pady=30)
        
        ctk.CTkButton(self.sidebar, text="Accounts", fg_color="transparent", 
                     command=self.draw_accounts).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.sidebar, text="Settings", fg_color="transparent", 
                     command=self.draw_settings).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.sidebar, text="+ Add Account", fg_color="#9D85FF", 
                     text_color="black", command=self.add_acc_thread).pack(fill="x", padx=10, pady=20)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.draw_accounts()

    def draw_accounts(self):
        for w in self.container.winfo_children(): 
            w.destroy()
            
        games = self.vault.get_games()
        
        # Header for Game/Job ID and Launch Method
        header = ctk.CTkFrame(self.container, fg_color="#2D2640")
        header.pack(fill="x", pady=(0,10))
        
        # Game selection
        game_frame = ctk.CTkFrame(header, fg_color="transparent")
        game_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(game_frame, text="Game:", width=50).pack(side="left", padx=5)
        self.g_sel = ctk.CTkOptionMenu(game_frame, values=list(games.keys()), fg_color="#1A1625", width=150)
        self.g_sel.pack(side="left", padx=5)
        
        # Job ID
        job_frame = ctk.CTkFrame(header, fg_color="transparent")
        job_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(job_frame, text="Job ID:", width=50).pack(side="left", padx=5)
        self.j_id = ctk.CTkEntry(job_frame, placeholder_text="Optional Server ID", width=250)
        self.j_id.pack(side="left", padx=5)
        
        # Launch Method Selection
        method_frame = ctk.CTkFrame(header, fg_color="transparent")
        method_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(method_frame, text="Method:", width=50).pack(side="left", padx=5)
        self.method_sel = ctk.CTkOptionMenu(
            method_frame, 
            values=RobloxAutomation.get_available_methods(),
            fg_color="#1A1625",
            width=250
        )
        self.method_sel.set(RobloxAutomation.METHOD_DIRECT)  # Default to direct method
        self.method_sel.pack(side="left", padx=5)

        self.scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self.refresh_accounts()

    def refresh_accounts(self):
        for w in self.scroll.winfo_children(): 
            w.destroy()
            
        accounts = self.vault.get_accounts()
        if not accounts:
            # Show empty state
            empty_frame = ctk.CTkFrame(self.scroll, fg_color="#2D2640", height=100)
            empty_frame.pack(fill="x", pady=20)
            ctk.CTkLabel(
                empty_frame, 
                text="No accounts saved yet.\nClick '+ Add Account' to get started.",
                font=("Arial", 14)
            ).pack(pady=30)
            return
            
        for acc in accounts:
            f = ctk.CTkFrame(self.scroll, fg_color="#2D2640", height=60)
            f.pack(fill="x", pady=5)
            
            ctk.CTkLabel(f, text=f"{acc['display_name']} (@{acc['username']})", 
                        font=("Arial", 13)).pack(side="left", padx=20)
            
            ctk.CTkButton(f, text="Launch", width=80, fg_color="#9D85FF", text_color="black", 
                          command=lambda a=acc: self.launch_account(a)).pack(side="right", padx=10)

    def draw_settings(self):
        for w in self.container.winfo_children(): 
            w.destroy()
            
        s_frame = ctk.CTkFrame(self.container, fg_color="#2D2640")
        s_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(s_frame, text="Game Manager", font=("Arial", 18, "bold")).pack(pady=20)
        
        # Add new game
        add_frame = ctk.CTkFrame(s_frame, fg_color="#1A1625")
        add_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(add_frame, text="Add New Game:", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.new_g_name = ctk.CTkEntry(add_frame, placeholder_text="Game Name (e.g. Pet Sim)", width=300)
        self.new_g_name.pack(pady=5)
        
        self.new_g_id = ctk.CTkEntry(add_frame, placeholder_text="Place ID (e.g. 12345)", width=300)
        self.new_g_id.pack(pady=5)
        
        ctk.CTkButton(add_frame, text="Add Game", fg_color="#9D85FF", 
                     text_color="black", command=self.save_new_game).pack(pady=10)
        
        # Show existing games
        games_frame = ctk.CTkFrame(s_frame, fg_color="#1A1625")
        games_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(games_frame, text="Saved Games:", font=("Arial", 14, "bold")).pack(pady=10)
        
        games = self.vault.get_games()
        for game_name, place_id in games.items():
            game_row = ctk.CTkFrame(games_frame, fg_color="#2D2640")
            game_row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(game_row, text=f"{game_name}: {place_id}").pack(side="left", padx=10)

    def save_new_game(self):
        name = self.new_g_name.get()
        pid = self.new_g_id.get()
        if name and pid:
            self.vault.add_game(name, pid)
            self.draw_settings()
            # Update game dropdown in accounts view
            self.draw_accounts()

    def add_acc_thread(self):
        def run():
            try:
                # Show loading indicator
                loading = ctk.CTkToplevel(self)
                loading.title("")
                loading.geometry("300x150")
                loading.configure(fg_color="#2D2640")
                loading.transient(self)
                loading.grab_set()
                
                ctk.CTkLabel(loading, text="Waiting for Roblox login...", 
                            font=("Arial", 14)).pack(pady=20)
                ctk.CTkLabel(loading, text="Please log in to Roblox in the browser that opens", 
                            font=("Arial", 10)).pack()
                ctk.CTkLabel(loading, text="The browser will close automatically after login", 
                            font=("Arial", 10)).pack()
                
                ck = RobloxAutomation.capture_session()
                loading.destroy()
                
                if ck:
                    # Verify the cookie
                    data = validate_cookie(ck)
                    if data:
                        # Encrypt and save
                        enc = CryptoEngine.encrypt(ck, self.session_key)
                        self.vault.add_account(
                            str(data['id']), 
                            data['name'], 
                            data['displayName'], 
                            enc
                        )
                        self.after(0, self.draw_accounts)
                        
                        # Show success message
                        self.after(0, lambda: self.show_message("Success", 
                            f"Account {data['displayName']} added successfully!"))
                    else:
                        self.after(0, lambda: self.show_message("Error", 
                            "Invalid cookie - please try again"))
                else:
                    self.after(0, lambda: self.show_message("Error", 
                        "Failed to capture cookie - login cancelled or timed out"))
            except Exception as e:
                self.after(0, lambda: self.show_message("Error", f"Failed to add account: {str(e)}"))
        
        threading.Thread(target=run, daemon=True).start()

    def launch_account(self, acc):
        def launch():
            try:
                # Show launching status
                status_frame = ctk.CTkFrame(self.container, fg_color="#2D2640")
                status_frame.pack(fill="x", pady=5)
                
                status_label = ctk.CTkLabel(
                    status_frame, 
                    text=f"Launching {acc['display_name']}...", 
                    font=("Arial", 12)
                )
                status_label.pack(pady=5)
                
                # Force UI update
                self.update()
                
                # Get the place ID
                games = self.vault.get_games()
                selected_game = self.g_sel.get()
                place_id = games.get(selected_game)
                
                if not place_id:
                    self.after(0, lambda: self.show_message("Error", "Please select a game first"))
                    status_frame.destroy()
                    return
                
                # Decrypt the cookie
                cookie = CryptoEngine.decrypt(acc['encrypted_cookie'], self.session_key)
                
                if not cookie:
                    self.after(0, lambda: self.show_message("Error", "Failed to decrypt cookie"))
                    status_frame.destroy()
                    return
                
                # Verify cookie and get user data
                status_label.configure(text="Verifying cookie...")
                self.update()
                
                user_data = RobloxAutomation.verify_cookie(cookie)
                if not user_data:
                    self.after(0, lambda: self.show_message("Error", 
                        "Cookie is invalid or expired. Please re-add the account."))
                    status_frame.destroy()
                    return
                
                # Get selected launch method
                selected_method = self.method_sel.get()
                
                # Launch Roblox with selected method
                status_label.configure(text=f"Launching with {selected_method}...")
                self.update()
                
                job_id = self.j_id.get() if self.j_id.get() else None
                
                # Run in a separate thread to not block UI
                def run_launch():
                    try:
                        success = RobloxAutomation.launch(
                            place_id, 
                            cookie, 
                            job_id, 
                            selected_method,
                            user_data.get('id')  # Pass user_id for appStorage.json
                        )
                        if success:
                            self.after(0, lambda: status_label.configure(
                                text="Launch successful! Roblox should open shortly."))
                        else:
                            self.after(0, lambda: status_label.configure(
                                text="Launch may have failed. Check console for details."))
                        self.after(5000, status_frame.destroy)
                    except Exception as e:
                        self.after(0, lambda: status_label.configure(text=f"Error: {str(e)}"))
                        self.after(5000, status_frame.destroy)
                
                threading.Thread(target=run_launch, daemon=True).start()
                
            except Exception as e:
                self.after(0, lambda: self.show_message("Error", f"Launch failed: {str(e)}"))
                if 'status_frame' in locals():
                    self.after(0, status_frame.destroy)
        
        threading.Thread(target=launch, daemon=True).start()

    def show_message(self, title, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.configure(fg_color="#2D2640")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=message, wraplength=250).pack(pady=30, padx=20)
        ctk.CTkButton(dialog, text="OK", fg_color="#9D85FF", text_color="black",
                     command=dialog.destroy).pack()

if __name__ == "__main__":
    app = RAMApp()
    app.mainloop()