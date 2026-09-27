import os
import threading

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from config import (
    WEBHOOK_SECRET,
    TRADING_ENABLED
)

from engine.portfolio_state_store import (
    load_state
)

from engine.portfolio_manager import (
    PortfolioManager
)

from engine.signal_manager import (
    SignalManager
)

from engine.season_monitor import (
    SeasonMonitor
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)


# =========================================================
# RSPS STATE
# =========================================================

state = load_state()


# =========================================================
# PORTFOLIO MANAGER
# =========================================================

portfolio_manager = (
    PortfolioManager()
)


# =========================================================
# SIGNAL MANAGER
# =========================================================

signal_manager = (
    SignalManager(
        state=state,
        portfolio_manager=portfolio_manager
    )
)


# =========================================================
# ETH SEASON MONITOR
# =========================================================

season_monitor = (
    SeasonMonitor(
        state=state,
        portfolio_manager=portfolio_manager
    )
)


# =========================================================
# STARTUP RECONCILIATION
# =========================================================

def reconcile_on_startup():

    print(
        "\n"
        "========================================"
    )

    print(
        "       STARTUP PORTFOLIO CHECK"
    )

    print(
        "========================================"
    )

    # -----------------------------------------------------
    # TRADING DISABLED
    # -----------------------------------------------------

    if not TRADING_ENABLED:

        print(
            "Trading is disabled."
        )

        print(
            "Startup rebalance skipped."
        )

        return

    # -----------------------------------------------------
    # SIGNALS NOT READY
    # -----------------------------------------------------

    if not state.all_signals_ready():

        print(
            "Not all RSPS signals are available."
        )

        print(
            "Startup rebalance skipped."
        )

        return

    # -----------------------------------------------------
    # REBALANCE
    # -----------------------------------------------------

    print(
        "Trading enabled."
    )

    print(
        "Reconciling Bybit positions "
        "with saved RSPS state..."
    )

    try:

        success = (
            portfolio_manager.rebalance(
                state=state,
                dry_run=False
            )
        )

    except Exception as error:

        print(
            "\n===== STARTUP REBALANCE ERROR ====="
        )

        print(
            repr(error)
        )

        return

    if success:

        print(
            "\n===== STARTUP REBALANCE COMPLETE ====="
        )

    else:

        print(
            "\n===== STARTUP REBALANCE FAILED ====="
        )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({
        "status": "online",
        "bot": "RSPS",
        "trading_enabled":
            TRADING_ENABLED,
        "signals_ready":
            state.all_signals_ready()
    })


# =========================================================
# WEBHOOK
# =========================================================

@app.route(
    "/webhook",
    methods=["POST"]
)
def webhook():

    try:

        # -------------------------------------------------
        # PARSE JSON
        # -------------------------------------------------

        data = request.get_json(
            silent=True
        )

        if data is None:

            return jsonify({
                "status": "error",
                "message": "Invalid JSON"
            }), 400

        # -------------------------------------------------
        # CHECK SECRET
        # -------------------------------------------------

        received_secret = (
            data.get(
                "secret"
            )
        )

        if WEBHOOK_SECRET is None:

            print(
                "\n===== WEBHOOK_SECRET NOT CONFIGURED ====="
            )

            return jsonify({
                "status": "error",
                "message":
                    "Webhook secret not configured"
            }), 500

        if (
            received_secret
            !=
            WEBHOOK_SECRET
        ):

            print(
                "\n===== INVALID WEBHOOK SECRET ====="
            )

            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401

        # -------------------------------------------------
        # PROCESS SIGNAL
        # -------------------------------------------------

        result = (
            signal_manager.process_payload(
                data
            )
        )

        # -------------------------------------------------
        # REBALANCE FAILURE
        # -------------------------------------------------

        if not result[
            "success"
        ]:

            return jsonify(
                result
            ), 500

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        return jsonify(
            result
        ), 200

    # =====================================================
    # VALIDATION ERROR
    # =====================================================

    except ValueError as error:

        print(
            "\n===== WEBHOOK VALIDATION ERROR ====="
        )

        print(
            str(error)
        )

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    # =====================================================
    # UNEXPECTED ERROR
    # =====================================================

    except Exception as error:

        print(
            "\n===== WEBHOOK ERROR ====="
        )

        print(
            repr(error)
        )

        return jsonify({
            "status": "error",
            "message":
                "Internal server error"
        }), 500


# =========================================================
# START BOT
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # PRINT STARTUP STATE
    # -----------------------------------------------------

    print(
        "\n"
        "========================================"
    )

    print(
        "          RSPS BOT STARTING"
    )

    print(
        "========================================"
    )

    print(
        f"Signals ready: "
        f"{state.all_signals_ready()}"
    )

    print(
        f"Trading enabled: "
        f"{TRADING_ENABLED}"
    )

    # -----------------------------------------------------
    # START ETH SEASON MONITOR
    # -----------------------------------------------------

    season_thread = threading.Thread(
        target=season_monitor.start,
        daemon=True
    )

    season_thread.start()

    # -----------------------------------------------------
    # STARTUP PORTFOLIO RECONCILIATION
    # -----------------------------------------------------

    reconcile_on_startup()

    # -----------------------------------------------------
    # START FLASK
    # -----------------------------------------------------

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )