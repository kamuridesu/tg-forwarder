import os

if os.path.isfile(".env"):
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                name = line.split("=")[0]
                value = line.split("=")[1].strip()
                os.environ.setdefault(name, value)

if not os.path.exists("db"):
    os.makedirs("db")
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
API_SERVER = os.getenv("TELEGRAM_API_SERVER")
SESSION_STRING = os.getenv("TELEGRAM_SESSION_STRING")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE = os.path.join("db", "telegram.db")
