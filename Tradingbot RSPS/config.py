import os
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# BYBIT
# =========================================================

USE_DEMO = (
    os.getenv(
        "USE_DEMO",
        "True"
    ).lower()
    == "true"
)


BYBIT_API_KEY_DEMO = os.getenv(
    "BYBIT_API_KEY_DEMO"
)


BYBIT_API_SECRET_DEMO = os.getenv(
    "BYBIT_API_SECRET_DEMO"
)


# =========================================================
# WEBHOOK
# =========================================================

WEBHOOK_SECRET = os.getenv(
    "WEBHOOK_SECRET"
)


# =========================================================
# MASTER TRADING SWITCH
# =========================================================

TRADING_ENABLED = (
    os.getenv(
        "TRADING_ENABLED",
        "False"
    ).lower()
    == "true"
)


