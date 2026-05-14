import schwabdev
import os
from dotenv import load_dotenv

def createClient(key, secret):
    client = schwabdev.Client(
        app_key=key,
        app_secret=secret,
        callback_url="https://127.0.0.1",
        tokens_db="~/.schwabdev/tokens.db",
        encryption=None,
        timeout=10,
        call_on_auth=None,
        open_browser_for_auth=True
    )
    return client

def main():
    load_dotenv()  # Loads variables from .env into os.environ
    app_key = os.getenv("app_key")
    app_secret = os.getenv("app_secret")
    client = createClient(app_key, app_secret)

if __name__ == "__main__":
    main()