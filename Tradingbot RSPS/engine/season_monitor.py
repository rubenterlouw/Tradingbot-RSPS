import time
from datetime import datetime, timezone

from config import TRADING_ENABLED

from engine.allocation import (
    get_eth_season_value
)

from engine.portfolio_state_store import (
    save_state
)


# =========================================================
# ETH SEASON MONITOR
# =========================================================

class SeasonMonitor:

    def __init__(
        self,
        state,
        portfolio_manager
    ):

        self.state = state

        self.portfolio_manager = (
            portfolio_manager
        )

        self.running = False

    # =====================================================
    # CHECK SEASON
    # =====================================================

    def check_season(self):

        current_season = int(
            get_eth_season_value(
                datetime.now(
                    timezone.utc
                )
            )
        )

        # -------------------------------------------------
        # FIRST CHECK
        # -------------------------------------------------

        if (
            self.state.last_eth_season
            is None
        ):

            self.state.last_eth_season = (
                current_season
            )

            save_state(
                self.state
            )

            print(
                "\n===== ETH SEASON INITIALIZED ====="
            )

            print(
                f"ETH season: "
                f"{current_season}"
            )

            return

        # -------------------------------------------------
        # NO CHANGE
        # -------------------------------------------------

        if (
            current_season
            ==
            self.state.last_eth_season
        ):

            return

        # -------------------------------------------------
        # SEASON CHANGED
        # -------------------------------------------------

        old_season = (
            self.state.last_eth_season
        )

        self.state.last_eth_season = (
            current_season
        )

        save_state(
            self.state
        )

        print(
            "\n"
            "========================================"
        )

        print(
            "          ETH SEASON CHANGED"
        )

        print(
            "========================================"
        )

        print(
            f"Old: {old_season}"
        )

        print(
            f"New: {current_season}"
        )

        # -------------------------------------------------
        # SIGNALS NOT READY
        # -------------------------------------------------

        if not (
            self.state.all_signals_ready()
        ):

            print(
                "Signals are not ready. "
                "Season rebalance skipped."
            )

            return

        # -------------------------------------------------
        # TRADING DISABLED
        # -------------------------------------------------

        if not TRADING_ENABLED:

            print(
                "\n===== TRADING DISABLED ====="
            )

            print(
                "ETH season state was updated."
            )

            print(
                "No Bybit rebalance was executed."
            )

            return

        # -------------------------------------------------
        # REBALANCE
        # -------------------------------------------------

        success = (
            self.portfolio_manager.rebalance(
                state=self.state,
                dry_run=False
            )
        )

        if success:

            print(
                "\n===== ETH SEASON REBALANCE COMPLETE ====="
            )

        else:

            print(
                "\n===== ETH SEASON REBALANCE FAILED ====="
            )

    # =====================================================
    # START MONITOR
    # =====================================================

    def start(self):

        print(
            "\n===== ETH SEASON MONITOR STARTED ====="
        )

        self.running = True

        while self.running:

            try:

                self.check_season()

            except Exception as error:

                print(
                    "\n===== ETH SEASON MONITOR ERROR ====="
                )

                print(
                    repr(error)
                )

            time.sleep(
                60
            )

    # =====================================================
    # STOP MONITOR
    # =====================================================

    def stop(self):

        self.running = False