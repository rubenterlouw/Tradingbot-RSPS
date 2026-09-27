from threading import Lock

from config import TRADING_ENABLED

from engine.portfolio_state_store import (
    save_state
)


# =========================================================
# TRADINGVIEW SIGNAL DEFINITIONS
# =========================================================

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


# =========================================================
# SIGNAL MANAGER
# =========================================================

class SignalManager:

    def __init__(
        self,
        state,
        portfolio_manager
    ):

        self.state = state

        self.portfolio_manager = (
            portfolio_manager
        )

        self.lock = Lock()

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
    # VALIDATE SIGNAL VALUE
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
            # DUPLICATE PROTECTION
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
                    "status": "duplicate_ignored"
                }

            # ---------------------------------------------
            # IDENTIFY SIGNAL
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
            # PARSE VALUES
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
            # PRINT UPDATE
            # ---------------------------------------------

            old_signal = (
                self.state.get_signal(
                    signal_name
                )
            )

            old_value = (
                old_signal.value
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
                f"Old value: {old_value}"
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
            # UPDATE STATE
            # ---------------------------------------------

            self.state.update_signal(
                signal_name=signal_name,
                value=value,
                count=count,
                timeframe=timeframe,
                bar_time=bar_time,
                signal_id=signal_id
            )

            save_state(
                self.state
            )

            # ---------------------------------------------
            # WAIT UNTIL ALL SIX SIGNALS EXIST
            # ---------------------------------------------

            if not (
                self.state.all_signals_ready()
            ):

                print(
                    "\n===== WAITING FOR REMAINING SIGNALS ====="
                )

                self.state.remember_signal(
                    signal_id
                )

                save_state(
                    self.state
                )

                return {
                    "success": True,
                    "status":
                        "signal_saved_waiting",
                    "signal":
                        signal_name
                }

            # ---------------------------------------------
            # MASTER TRADING SWITCH
            # ---------------------------------------------

            if not TRADING_ENABLED:

                print(
                    "\n"
                    "========================================"
                )

                print(
                    "          TRADING DISABLED"
                )

                print(
                    "========================================"
                )

                print(
                    "Signal state updated and saved."
                )

                print(
                    "No Bybit orders will be placed."
                )

                self.state.remember_signal(
                    signal_id
                )

                save_state(
                    self.state
                )

                return {
                    "success": True,
                    "status":
                        "signal_saved_trading_disabled",
                    "signal":
                        signal_name,
                    "value":
                        value
                }

            # ---------------------------------------------
            # REBALANCE
            # ---------------------------------------------

            print(
                "\n===== RECALCULATING PORTFOLIO ====="
            )

            success = (
                self.portfolio_manager.rebalance(
                    state=self.state,
                    dry_run=False
                )
            )

            # ---------------------------------------------
            # FAILED
            # ---------------------------------------------

            if not success:

                print(
                    "\n===== SIGNAL REBALANCE FAILED ====="
                )

                return {
                    "success": False,
                    "status":
                        "rebalance_failed",
                    "signal":
                        signal_name
                }

            # ---------------------------------------------
            # SUCCESS
            # ---------------------------------------------

            self.state.remember_signal(
                signal_id
            )

            save_state(
                self.state
            )

            return {
                "success": True,
                "status": "rebalanced",
                "signal": signal_name,
                "value": value
            }