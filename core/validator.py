import requests

def validate_cookie(cookie):
    """
    Validates a Roblox .ROBLOSECURITY cookie by making an authenticated request
    Returns user data if valid, None if invalid
    """
    try:
        headers = {
            "Cookie": f".ROBLOSECURITY={cookie}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(
            "https://users.roblox.com/v1/users/authenticated", 
            headers=headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Cookie validation failed with status: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("Cookie validation timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Cookie validation error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in cookie validation: {e}")
        return None