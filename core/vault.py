import sqlite3
import os
from datetime import datetime
from pathlib import Path

class VaultManager:
    def __init__(self):
        # Uses a dedicated folder in LocalAppData to store the database
        self.base_path = Path(os.getenv('LOCALAPPDATA')) / "RAM_V1"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_path / "vault.db"
        self._init_db()

    def _init_db(self):
        """Initializes tables if they do not exist."""
        with sqlite3.connect(self.db_path) as conn:
            # Table for master password hash and encryption salt
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    id INTEGER PRIMARY KEY, 
                    salt TEXT, 
                    password_hash TEXT, 
                    last_rotation TEXT
                )""")
            
            # Table for account storage
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    user_id TEXT PRIMARY KEY, 
                    username TEXT, 
                    display_name TEXT, 
                    encrypted_cookie TEXT, 
                    status TEXT,
                    added_at TEXT
                )""")
            
            # Table for game management
            conn.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    game_name TEXT PRIMARY KEY, 
                    place_id TEXT
                )""")
            
            # Default game entries
            default_games = [
                ('Blox Fruits', '2753915549'),
                ('Deepwoken', '4111023553'),
                ('Pet Simulator X', '7722306047'),
                ('Adopt Me!', '920587237'),
                ('Tower of Hell', '1962086868'),
                ('Brookhaven', '4924922222'),
                ('MM2', '142823291')
            ]
            
            for game_name, place_id in default_games:
                conn.execute("INSERT OR IGNORE INTO games VALUES (?, ?)", (game_name, place_id))

    def is_initialized(self):
        """Checks if the master password has been set up."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("SELECT COUNT(*) FROM metadata").fetchone()
            return result[0] > 0 if result else False

    def setup_vault(self, password):
        """Initial setup for the master password and salt."""
        import hashlib
        salt = os.urandom(16)
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO metadata (salt, password_hash, last_rotation) VALUES (?, ?, ?)", 
                (salt.hex(), pw_hash, datetime.now().strftime("%Y-%m-%d"))
            )
        
        return salt

    def get_auth_data(self):
        """Retrieves salt and hash for login verification."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("SELECT salt, password_hash FROM metadata WHERE id=1").fetchone()
            return result if result else None

    def add_account(self, uid, user, display, enc_cookie):
        """Saves or updates an account."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO accounts VALUES (?, ?, ?, ?, ?, ?)", 
                (uid, user, display, enc_cookie, 'Active', datetime.now().isoformat())
            )

    def get_accounts(self):
        """Returns all saved accounts as a list of dictionaries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM accounts ORDER BY added_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_account(self, user_id):
        """Deletes an account by user ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))

    def add_game(self, name, pid):
        """Adds a new game to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO games VALUES (?, ?)", (name, pid))

    def get_games(self):
        """Returns a dictionary mapping game names to place IDs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM games ORDER BY game_name")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def delete_game(self, game_name):
        """Deletes a game by name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM games WHERE game_name = ?", (game_name,))