# RAM - Roblox Account Manager 🔐

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

RAM is a secure desktop application for managing multiple Roblox accounts. It safely stores your account cookies using military-grade encryption and provides one-click launching into any game with optional server selection.

![RAM Vault Screenshot](screenshot.png)

## ✨ Features

- **🔒 Secure Vault** - All cookies are encrypted using AES-GCM with a master password
- **👥 Multiple Accounts** - Store and manage unlimited Roblox accounts
- **🚀 One-Click Launch** - Launch directly into games without manual login
- **🆔 Server Selection** - Optional Job ID support for joining specific roblox games and server
- **🔄 Multi-Instance** - Run multiple Roblox accounts simultaneously
- **🛡️ Anti-Detection** - Stealth cookie injection methods to avoid detection
- **📱 Bloxstrap Support** - Compatible with Bloxstrap and other custom launchers

## 📋 Requirements

- Windows 10/11 (64-bit)
- Python 3.8 or higher
- Google Chrome (for cookie capture)
- Roblox Player installed

## 🚀 Installation

### Option 1: Pre-built Executable (Recommended)
1. Download the latest `RAM_V1.exe` from the [Releases](https://github.com/StarlightShade15/RobloxAccountManager/releases) page
2. Run the executable - no installation required

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/StarlightShade15/RobloxAccountManager.git
cd ram

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
