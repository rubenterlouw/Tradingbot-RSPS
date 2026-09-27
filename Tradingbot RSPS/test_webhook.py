import time
import requests


# =========================================================
# LOCAL WEBHOOK
# =========================================================

WEBHOOK_URL = "http://127.0.0.1:5000/webhook"

WEBHOOK_SECRET = "mySuperSecretPassword"


# =========================================================
# WHICH SIGNAL DO YOU WANT TO TEST?
# =========================================================
#
# Options:
#
# total_daily
# total_weekly
# eth_btc_daily
# eth_btc_weekly
# sol_btc
# sol_eth
#
# =========================================================

TEST_SIGNAL = "sol_eth"


# =========================================================
# UNIQUE SIGNAL ID / BAR TIME
# =========================================================

current_time_ms = int(
    time.time() * 1000
)


# =========================================================
# TEST PAYLOADS
# =========================================================

payloads = {

    # =====================================================
    # TOTAL DAILY
    # =====================================================

    "total_daily": {

        "payload_version": 1,

        "secret":
            WEBHOOK_SECRET,

        "strategy":
            "RSPS Daily indicator",

        "symbol":
            "CRYPTOCAP:TOTAL",

        "kama daily":
            "1",

        "Weighted Bull Bears daily":
            1,

        "AFR Daily":
            1,

        "ATREE SS Daily":
            -1,

        "LWMA Daily":
            1,

        "Flexima Daily":
            -1,

        "total_daily":
            0.3333,

        "number of indicators":
            6,

        "timeframe":
            "D",

        "bar_time":
            current_time_ms,

        "signal_id":
            (
                "CRYPTOCAP:TOTAL_"
                "RSPS Daily indicator_"
                f"{current_time_ms}"
            )
    },


    # =====================================================
    # TOTAL WEEKLY
    # =====================================================

    "total_weekly": {

        "payload_version": 1,

        "secret":
            WEBHOOK_SECRET,

        "strategy":
            "RSPS Weekly indicator",

        "symbol":
            "CRYPTOCAP:TOTAL",

        "STC Weekly":
            "1",

        "NBBP Weekly":
            1,

        "PSAR Weekly":
            1,

        "HLTrend Weekly":
            -1,

        "Total Weekly":
            0.5,

        "timeframe":
            "W",

        "bar_time":
            current_time_ms,

        "number of indicators":
            4,

        "signal_id":
            (
                "CRYPTOCAP:TOTAL_"
                "RSPS Weekly indicator_"
                f"{current_time_ms}"
            )
    },


    # =====================================================
    # ETH / BTC DAILY
    # =====================================================

    "eth_btc_daily": {

        "payload_version": 1,

        "secret":
            WEBHOOK_SECRET,

        "strategy":
            "RSPS Daily ETH/BTC indicator",

        "symbol":
            "BINANCE:ETHBTC",

        "Kalman Hull ETH/BTC daily":
            "1",

        "AFR ETH/BTC Daily":
            1,

        "ATREE SS ETH/BTC Daily":
            0,

        "total ETH/BTC daily":
            0.6667,

        "number of indicators":
            3,

        "timeframe":
            "D",

        "bar_time":
            current_time_ms,

        "signal_id":
            (
                "BINANCE:ETHBTC_"
                "RSPS Daily ETH/BTC indicator_"
                f"{current_time_ms}"
            )
    },


    # =====================================================
    # ETH / BTC WEEKLY
    # =====================================================

    "eth_btc_weekly": {

        "payload_version": 1,

        "secret":
            WEBHOOK_SECRET,

        "strategy":
            "RSPS Weekly ETH/BTC indicator",

        "symbol":
            "BINANCE:ETHBTC",

        "ATRSuper ETH/BTC Weekly":
            "1",

        "HLTrend ETH/BTC Weekly":
            0,

        "total ETH/BTC Weekly":
            0.5,

        "timeframe":
            "W",

        "bar_time":
            current_time_ms,

        "number of indicators":
            2,

        "signal_id":
            (
                "BINANCE:ETHBTC_"
                "RSPS Weekly ETH/BTC indicator_"
                f"{current_time_ms}"
            )
    },


    # =====================================================
    # SOL / BTC DAILY
    # =====================================================

    "sol_btc": {

        "payload_version": 1,

        "secret":
            WEBHOOK_SECRET,

        "strategy":
            "RSPS Daily SOL/BTC indicator",

        "symbol":
            "BINANCE:SOLBTC",

        "AwO SOL/BTC daily":
            "1",

        "Vacc SOL/BTC Daily":
            1,

        "AFR SOL/BTC Daily":
            1,

        "ATREE SS SOL/BTC Daily":
            0,

        "total SOL/BTC daily":
            0.75,

        "number of indicators":
            4,

        "timeframe":
            "D",

        "bar_time":
            current_time_ms,

        "signal_id":
            (
                "BINANCE:SOLBTC_"
                "RSPS Daily SOL/BTC indicator_"
                f"{current_time_ms}"
            )
    },


    # =====================================================
    # SOL / ETH DAILY
    # =====================================================

    "sol_eth": {

        "payload_version": 1,

        "secret":
            WEBHOOK_SECRET,

        "strategy":
            "RSPS Daily SOL/ETH indicator",

        "symbol":
            "BINANCE:SOLETH",

        "Dope Dpo SOL/ETH daily":
            "1",

        "Trend Sniper SOL/ETH Daily":
            1,

        "AFR SOL/ETH Daily":
            0,

        "ATREE SS SOL/ETH Daily":
            0,

        "total SOL/ETH daily":
            0.5,

        "number of indicators":
            4,

        "timeframe":
            "D",

        "bar_time":
            current_time_ms,

        "signal_id":
            (
                "BINANCE:SOLETH_"
                "RSPS Daily SOL/ETH indicator_"
                f"{current_time_ms}"
            )
    }
}


# =========================================================
# SELECT PAYLOAD
# =========================================================

if TEST_SIGNAL not in payloads:

    print(
        f"Unknown TEST_SIGNAL: "
        f"{TEST_SIGNAL}"
    )

    raise SystemExit


payload = payloads[
    TEST_SIGNAL
]


# =========================================================
# PRINT TEST
# =========================================================

print(
    "\n"
    "========================================"
)

print(
    "          RSPS WEBHOOK TEST"
)

print(
    "========================================"
)

print(
    f"Signal: {TEST_SIGNAL}"
)

print(
    f"Signal ID: "
    f"{payload['signal_id']}"
)


# =========================================================
# SEND REQUEST
# =========================================================

try:

    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=30
    )

except requests.RequestException as error:

    print(
        "\n===== REQUEST FAILED ====="
    )

    print(
        repr(error)
    )

    raise SystemExit


# =========================================================
# RESPONSE
# =========================================================

print(
    f"\nHTTP status: "
    f"{response.status_code}"
)

try:

    print(
        "Response:"
    )

    print(
        response.json()
    )

except ValueError:

    print(
        response.text
    )