import threading

from flask import (
    Flask,
    request,
    jsonify
)

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

from engine.rebalance_worker import (
    RebalanceWorker
)


# =========================================================
# FLASK
# =========================================================

app = Flask(__name__)


# =========================================================
# STATE
# =========================================================

state = load_state()


# =========================================================
# MANAGERS
# =========================================================

portfolio_manager = (
    PortfolioManager()
)


signal_manager = (
    SignalManager(
        state=state,
        portfolio_manager=portfolio_manager
    )
)


rebalance_worker = (
    RebalanceWorker(
        portfolio_manager=
            portfolio_manager,
        state_provider=
            signal_manager.get_state_snapshot
    )
)


season_monitor = (
    SeasonMonitor(
        state=state,
        portfolio_manager=portfolio_manager
    )
)


# =========================================================
# BACKGROUND SERVICES
# =========================================================

background_services_started = False


def start_background_services():

    global background_services_started

    if background_services_started:
        return

    background_services_started = True

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
    # REBALANCE WORKER
    # -----------------------------------------------------

    rebalance_worker.start()

    # -----------------------------------------------------
    # SEASON MONITOR
    # -----------------------------------------------------

    season_thread = threading.Thread(
        target=season_monitor.start,
        daemon=True
    )

    season_thread.start()

    # -----------------------------------------------------
    # STARTUP RECONCILIATION
    # -----------------------------------------------------

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

    if not TRADING_ENABLED:

        print(
            "Trading disabled."
        )

        print(
            "Startup rebalance skipped."
        )

    elif not (
        state.all_signals_ready()
    ):

        print(
            "Signals not ready."
        )

        print(
            "Startup rebalance skipped."
        )

    else:

        rebalance_worker.request_rebalance(
            reason="startup_reconciliation"
        )


# =========================================================
# START SERVICES
# =========================================================
#
# IMPORTANT:
#
# This executes when Gunicorn imports app:app.
# It is therefore NOT inside __main__.
#
# We run exactly one Gunicorn worker.
# =========================================================

start_background_services()


# =========================================================
# HEALTH
# =========================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({
        "status":
            "online",
        "bot":
            "RSPS",
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

        data = request.get_json(
            silent=True
        )

        if data is None:

            return jsonify({
                "status":
                    "error",
                "message":
                    "Invalid JSON"
            }), 400

        # -------------------------------------------------
        # SECRET
        # -------------------------------------------------

        received_secret = (
            data.get(
                "secret"
            )
        )

        if WEBHOOK_SECRET is None:

            return jsonify({
                "status":
                    "error",
                "message":
                    "Webhook secret not configured"
            }), 500

        if (
            received_secret
            !=
            WEBHOOK_SECRET
        ):

            return jsonify({
                "status":
                    "error",
                "message":
                    "Unauthorized"
            }), 401

        # -------------------------------------------------
        # SAVE SIGNAL
        # -------------------------------------------------

        result = (
            signal_manager.process_payload(
                data
            )
        )

        # -------------------------------------------------
        # QUEUE EXECUTION
        # -------------------------------------------------

        if result.get(
            "rebalance_required",
            False
        ):

            queued = (
                rebalance_worker.request_rebalance(
                    reason=(
                        "TradingView: "
                        f"{result.get('signal')}"
                    )
                )
            )

            if queued:

                result[
                    "status"
                ] = "rebalance_queued"

            else:

                result[
                    "status"
                ] = "rebalance_already_queued"

        # Don't expose internal helper flag.
        result.pop(
            "rebalance_required",
            None
        )

        # -------------------------------------------------
        # FAST HTTP RESPONSE
        # -------------------------------------------------

        return jsonify(
            result
        ), 200

    except ValueError as error:

        print(
            "\n===== WEBHOOK VALIDATION ERROR ====="
        )

        print(
            str(error)
        )

        return jsonify({
            "status":
                "error",
            "message":
                str(error)
        }), 400

    except Exception as error:

        print(
            "\n===== WEBHOOK ERROR ====="
        )

        print(
            repr(error)
        )

        return jsonify({
            "status":
                "error",
            "message":
                "Internal server error"
        }), 500


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
    