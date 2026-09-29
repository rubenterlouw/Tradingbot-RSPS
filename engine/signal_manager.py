import copy
from threading import Lock

from config import TRADING_ENABLED

from engine.portfolio_state_store import (
    save_state
)


SIGNAL_DEFINITIONS = {

    "total_daily": {
        "field": "total_daily",
        "minimum": -1.0,
        "maximum": 1.0
    },

    "total_weekly": {
        "field": "Total Weekly",
        "minimum": -1.0,
        "maximum": 1.0
    },

    "eth_btc_daily": {
        "field": "total ETH/BTC daily",
        "minimum": 0.0,
        "maximum": 1.0
    },

    "eth_btc_weekly": {
        "field": "total ETH/BTC Weekly",
        "minimum": 0.0,
        "maximum": 1.0
    },

    "sol_btc": {
        "field": "total SOL/BTC daily",
        "minimum": 0.0,
        "maximum": 1.0
    },

    "sol_eth": {
        "field": "total SOL/ETH daily",
        "minimum": 0.0,
        "maximum": 1.0
    }
}


class SignalManager:

    def __init__(
        self,
        state,
        portfolio_manager=None
    ):

        self.state = state

        # Kept for compatibility with our previous app.py
        self.portfolio_manager = (
            portfolio_manager
        )

        self.lock = Lock()

    # =====================================================
    # STATE SNAPSHOT
    # =====================================================

    def get_state_snapshot(self):

        with self.lock:

            return copy.deepcopy(
                self.state
            )

    # =====================================================
    # IDENTIFY SIGNAL
    # =====================================================

    def identify_signal(
        self,
        payload
    ):

        matches = []

        for (
            signal_name,
            definition
        ) in SIGNAL_DEFINITIONS.items():

            field = definition[
                "field"
            ]

            if field in payload:

                matches.append(
                    signal_name
                )

        if len(matches) == 0:

            raise ValueError(
                "Could not identify RSPS signal."
            )

        if len(matches) > 1:

            raise ValueError(
                "Payload contains multiple RSPS total fields."
            )

        return matches[0]

    # =====================================================
    # VALIDATE VALUE
    # =====================================================

    def validate_value(
        self,
        signal_name,
        value
    ):

        definition = (
            SIGNAL_DEFINITIONS[
                signal_name
            ]
        )

        minimum = definition[
            "minimum"
        ]

        maximum = definition[
            "maximum"
        ]

        if (
            value < minimum
            or
            value > maximum
        ):

            raise ValueError(
                f"{signal_name} value "
                f"{value} is outside "
                f"{minimum} to {maximum}."
            )

    # =====================================================
    # PROCESS PAYLOAD
    # =====================================================

    def process_payload(
        self,
        payload
    ):

        with self.lock:

            required_fields = [
                "number of indicators",
                "timeframe",
                "bar_time",
                "signal_id"
            ]

            for field in required_fields:

                if field not in payload:

                    raise ValueError(
                        f"Missing field: {field}"
                    )

            signal_id = str(
                payload[
                    "signal_id"
                ]
            )

            # ---------------------------------------------
            # DUPLICATE
            # ---------------------------------------------

            if self.state.is_duplicate(
                signal_id
            ):

                print(
                    "\n===== DUPLICATE SIGNAL IGNORED ====="
                )

                print(
                    signal_id
                )

                return {
                    "success": True,
                    "status":
                        "duplicate_ignored",
                    "rebalance_required":
                        False
                }

            # ---------------------------------------------
            # IDENTIFY
            # ---------------------------------------------

            signal_name = (
                self.identify_signal(
                    payload
                )
            )

            definition = (
                SIGNAL_DEFINITIONS[
                    signal_name
                ]
            )

            value_field = (
                definition[
                    "field"
                ]
            )

            # ---------------------------------------------
            # PARSE
            # ---------------------------------------------

            try:

                value = float(
                    payload[
                        value_field
                    ]
                )

                count = int(
                    payload[
                        "number of indicators"
                    ]
                )

                bar_time = int(
                    payload[
                        "bar_time"
                    ]
                )

            except (
                TypeError,
                ValueError
            ):

                raise ValueError(
                    "Invalid numeric value in payload."
                )

            if count <= 0:

                raise ValueError(
                    "Number of indicators must "
                    "be greater than zero."
                )

            self.validate_value(
                signal_name,
                value
            )

            timeframe = str(
                payload[
                    "timeframe"
                ]
            )

            # ---------------------------------------------
            # PRINT
            # ---------------------------------------------

            old_signal = (
                self.state.get_signal(
                    signal_name
                )
            )

            print(
                "\n"
                "========================================"
            )

            print(
                "          RSPS SIGNAL RECEIVED"
            )

            print(
                "========================================"
            )

            print(
                f"Signal: {signal_name}"
            )

            print(
                f"Old value: {old_signal.value}"
            )

            print(
                f"New value: {value}"
            )

            print(
                f"Indicators: {count}"
            )

            print(
                f"Timeframe: {timeframe}"
            )

            # ---------------------------------------------
            # UPDATE
            # ---------------------------------------------

            self.state.update_signal(
                signal_name=signal_name,
                value=value,
                count=count,
                timeframe=timeframe,
                bar_time=bar_time,
                signal_id=signal_id
            )

            # Remember it immediately.
            #
            # If the server dies after HTTP 200 but before
            # execution, startup reconciliation will later
            # restore the portfolio from this saved state.
            self.state.remember_signal(
                signal_id
            )

            save_state(
                self.state
            )

            # ---------------------------------------------
            # NOT READY
            # ---------------------------------------------

            if not (
                self.state.all_signals_ready()
            ):

                return {
                    "success": True,
                    "status":
                        "signal_saved_waiting",
                    "signal":
                        signal_name,
                    "rebalance_required":
                        False
                }

            # ---------------------------------------------
            # TRADING DISABLED
            # ---------------------------------------------

            if not TRADING_ENABLED:

                print(
                    "\n===== TRADING DISABLED ====="
                )

                print(
                    "Signal saved. "
                    "No order execution."
                )

                return {
                    "success": True,
                    "status":
                        "signal_saved_trading_disabled",
                    "signal":
                        signal_name,
                    "value":
                        value,
                    "rebalance_required":
                        False
                }

            # ---------------------------------------------
            # BACKGROUND REBALANCE REQUIRED
            # ---------------------------------------------

            return {
                "success": True,
                "status":
                    "signal_saved",
                "signal":
                    signal_name,
                "value":
                    value,
                "rebalance_required":
                    True
            }