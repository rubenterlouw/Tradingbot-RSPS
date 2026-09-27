import time
from threading import Lock

from bybit.account import get_account_equity
from bybit.market import get_last_price
from bybit.positions import get_position
from bybit.orders import (
    place_market_order,
    close_partial_position,
    close_position
)
from bybit.instruments import get_quantity_rules

from engine.allocation import calculate_target_values


# =========================================================
# SYMBOLS MANAGED BY RSPS
# =========================================================

SYMBOLS = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT"
}


# =========================================================
# PORTFOLIO MANAGER
# =========================================================

class PortfolioManager:

    def __init__(self):
        self.lock = Lock()

    # =====================================================
    # CREATE REBALANCE PLAN
    # =====================================================

    def create_rebalance_plan(self, state):

        account_equity = get_account_equity()

        if account_equity is None:
            print(
                "\n===== COULD NOT GET ACCOUNT EQUITY ====="
            )
            return None

        targets = calculate_target_values(
            state=state,
            account_equity=account_equity
        )

        target_values = {
            "BTC": targets["btc_target_usd"],
            "ETH": targets["eth_target_usd"],
            "SOL": targets["sol_target_usd"]
        }

        plan = {
            "account_equity": account_equity,
            "strategy": targets,
            "assets": {}
        }

        for asset, symbol in SYMBOLS.items():

            price = get_last_price(symbol)

            if price is None:
                print(
                    f"\n===== COULD NOT GET {symbol} PRICE ====="
                )
                return None

            position = get_position(symbol)

            if position is None:
                print(
                    f"\n===== COULD NOT GET {symbol} POSITION ====="
                )
                return None

            current_signed_qty = position[
                "signed_size"
            ]

            current_usd = (
                current_signed_qty
                *
                price
            )

            target_usd = target_values[
                asset
            ]

            target_signed_qty = (
                target_usd
                /
                price
            )

            difference_qty = (
                target_signed_qty
                -
                current_signed_qty
            )

            difference_usd = (
                target_usd
                -
                current_usd
            )

            plan["assets"][asset] = {
                "symbol": symbol,
                "price": price,
                "current_signed_qty":
                    current_signed_qty,
                "current_usd":
                    current_usd,
                "target_signed_qty":
                    target_signed_qty,
                "target_usd":
                    target_usd,
                "difference_qty":
                    difference_qty,
                "difference_usd":
                    difference_usd
            }

        return plan

    # =====================================================
    # PRINT REBALANCE PLAN
    # =====================================================

    def print_rebalance_plan(self, plan):

        if plan is None:
            return

        strategy = plan[
            "strategy"
        ]

        print(
            "\n"
            "========================================"
        )

        print(
            "          RSPS REBALANCE PLAN"
        )

        print(
            "========================================"
        )

        print(
            f"Account equity: "
            f"${plan['account_equity']:.2f}"
        )

        print(
            f"Regime: "
            f"{strategy['regime']}"
        )

        print(
            f"TOTAL trend: "
            f"{strategy['total_trend']:.4f}"
        )

        print(
            f"ETH/BTC signal: "
            f"{strategy['eth_btc_signal']:.4f}"
        )

        print(
            f"SOL strength: "
            f"{strategy['sol_strength']:.4f}"
        )

        print(
            f"ETH season: "
            f"{strategy['eth_season']:.0f}"
        )

        print(
            "\n----------------------------------------"
        )

        for asset, data in (
            plan["assets"].items()
        ):

            print(
                f"\n{asset}"
            )

            print(
                f"Price: "
                f"${data['price']:.2f}"
            )

            print(
                f"Current: "
                f"${data['current_usd']:.2f}"
            )

            print(
                f"Target: "
                f"${data['target_usd']:.2f}"
            )

            print(
                f"Difference: "
                f"${data['difference_usd']:.2f}"
            )

    # =====================================================
    # GET QUANTITY TOLERANCE
    # =====================================================

    def get_quantity_tolerance(
        self,
        symbol
    ):

        rules = get_quantity_rules(
            symbol
        )

        if rules is None:

            print(
                f"\n===== COULD NOT GET QUANTITY RULES FOR {symbol} ====="
            )

            return None

        try:

            qty_step = float(
                rules["qty_step"]
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            print(
                f"\n===== INVALID QUANTITY RULES FOR {symbol} ====="
            )

            return None

        return qty_step

    # =====================================================
    # VERIFY POSITION
    # =====================================================

    def verify_position(
        self,
        symbol,
        expected_signed_qty,
        attempts=12,
        delay=0.25
    ):

        tolerance = (
            self.get_quantity_tolerance(
                symbol
            )
        )

        if tolerance is None:
            return False

        last_position = None

        for _ in range(
            attempts
        ):

            position = get_position(
                symbol
            )

            if position is None:

                time.sleep(
                    delay
                )

                continue

            last_position = position

            actual_signed_qty = (
                position[
                    "signed_size"
                ]
            )

            difference = abs(
                actual_signed_qty
                -
                expected_signed_qty
            )

            if difference <= tolerance:

                print(
                    f"\n===== {symbol} POSITION VERIFIED ====="
                )

                print(
                    f"Expected: "
                    f"{expected_signed_qty}"
                )

                print(
                    f"Actual:   "
                    f"{actual_signed_qty}"
                )

                print(
                    f"Tolerance: "
                    f"{tolerance}"
                )

                return True

            time.sleep(
                delay
            )

        print(
            f"\n===== {symbol} POSITION VERIFICATION FAILED ====="
        )

        print(
            f"Expected: "
            f"{expected_signed_qty}"
        )

        print(
            f"Tolerance: "
            f"{tolerance}"
        )

        if last_position is not None:

            print(
                f"Actual:   "
                f"{last_position['signed_size']}"
            )

        return False

    # =====================================================
    # REBALANCE SINGLE ASSET
    # =====================================================

    def rebalance_asset(
        self,
        asset_data,
        dry_run=True
    ):

        symbol = asset_data[
            "symbol"
        ]

        current_qty = asset_data[
            "current_signed_qty"
        ]

        target_qty = asset_data[
            "target_signed_qty"
        ]

        print(
            f"\n===== REBALANCING {symbol} ====="
        )

        print(
            f"Current signed qty: "
            f"{current_qty}"
        )

        print(
            f"Target signed qty: "
            f"{target_qty}"
        )

        # -------------------------------------------------
        # CHECK IF ALREADY CLOSE ENOUGH TO TARGET
        # -------------------------------------------------

        tolerance = (
            self.get_quantity_tolerance(
                symbol
            )
        )

        if tolerance is None:
            return False

        difference = abs(
            target_qty
            -
            current_qty
        )

        if difference <= tolerance:

            print(
                f"\n===== {symbol} ALREADY WITHIN TARGET ====="
            )

            print(
                f"Current:    "
                f"{current_qty}"
            )

            print(
                f"Target:     "
                f"{target_qty}"
            )

            print(
                f"Difference: "
                f"{difference}"
            )

            print(
                f"Tolerance:  "
                f"{tolerance}"
            )

            return True

        # -------------------------------------------------
        # DRY RUN
        # -------------------------------------------------

        if dry_run:

            print(
                "DRY RUN - no order placed."
            )

            return True

        # -------------------------------------------------
        # TARGET IS ZERO
        # -------------------------------------------------

        if target_qty == 0:

            if current_qty == 0:

                print(
                    "Already flat."
                )

                return True

            close_side = (
                "Sell"
                if current_qty > 0
                else "Buy"
            )

            result = close_position(
                symbol=symbol,
                side=close_side,
                qty=abs(current_qty)
            )

            if not result[
                "success"
            ]:

                print(
                    f"\n===== {symbol} CLOSE FAILED ====="
                )

                return False

            return self.verify_position(
                symbol=symbol,
                expected_signed_qty=0.0
            )

        # -------------------------------------------------
        # CURRENT POSITION IS ZERO
        # -------------------------------------------------

        if current_qty == 0:

            open_side = (
                "Buy"
                if target_qty > 0
                else "Sell"
            )

            result = place_market_order(
                symbol=symbol,
                side=open_side,
                qty=abs(target_qty),
                reduce_only=False
            )

            if not result[
                "success"
            ]:

                print(
                    f"\n===== {symbol} OPEN FAILED ====="
                )

                return False

            return self.verify_position(
                symbol=symbol,
                expected_signed_qty=target_qty
            )

        # -------------------------------------------------
        # SAME DIRECTION
        # -------------------------------------------------

        same_direction = (
            (
                current_qty > 0
                and
                target_qty > 0
            )
            or
            (
                current_qty < 0
                and
                target_qty < 0
            )
        )

        if same_direction:

            current_size = abs(
                current_qty
            )

            target_size = abs(
                target_qty
            )

            # ---------------------------------------------
            # INCREASE POSITION
            # ---------------------------------------------

            if target_size > current_size:

                increase_qty = (
                    target_size
                    -
                    current_size
                )

                side = (
                    "Buy"
                    if target_qty > 0
                    else "Sell"
                )

                result = place_market_order(
                    symbol=symbol,
                    side=side,
                    qty=increase_qty,
                    reduce_only=False
                )

                if not result[
                    "success"
                ]:

                    print(
                        f"\n===== {symbol} INCREASE FAILED ====="
                    )

                    return False

                return self.verify_position(
                    symbol=symbol,
                    expected_signed_qty=target_qty
                )

            # ---------------------------------------------
            # REDUCE POSITION
            # ---------------------------------------------

            if target_size < current_size:

                reduce_qty = (
                    current_size
                    -
                    target_size
                )

                side = (
                    "Sell"
                    if current_qty > 0
                    else "Buy"
                )

                result = close_partial_position(
                    symbol=symbol,
                    side=side,
                    qty=reduce_qty
                )

                if not result[
                    "success"
                ]:

                    print(
                        f"\n===== {symbol} REDUCTION FAILED ====="
                    )

                    return False

                return self.verify_position(
                    symbol=symbol,
                    expected_signed_qty=target_qty
                )

            print(
                "Position already matches target."
            )

            return True

        # -------------------------------------------------
        # OPPOSITE DIRECTIONS
        # -------------------------------------------------

        print(
            "\nDirection change detected."
        )

        close_side = (
            "Sell"
            if current_qty > 0
            else "Buy"
        )

        close_result = close_position(
            symbol=symbol,
            side=close_side,
            qty=abs(current_qty)
        )

        if not close_result[
            "success"
        ]:

            print(
                "\n===== CLOSE BEFORE REVERSAL FAILED ====="
            )

            return False

        # -------------------------------------------------
        # VERIFY OLD POSITION CLOSED
        # -------------------------------------------------

        position_closed = (
            self.verify_position(
                symbol=symbol,
                expected_signed_qty=0.0
            )
        )

        if not position_closed:

            print(
                "\n===== REVERSAL ABORTED ====="
            )

            print(
                "Old position could not be confirmed closed."
            )

            print(
                "New opposite position will NOT be opened."
            )

            return False

        # -------------------------------------------------
        # OPEN NEW DIRECTION
        # -------------------------------------------------

        open_side = (
            "Buy"
            if target_qty > 0
            else "Sell"
        )

        open_result = place_market_order(
            symbol=symbol,
            side=open_side,
            qty=abs(target_qty),
            reduce_only=False
        )

        if not open_result[
            "success"
        ]:

            print(
                "\n===== NEW POSITION AFTER REVERSAL FAILED ====="
            )

            return False

        return self.verify_position(
            symbol=symbol,
            expected_signed_qty=target_qty
        )

    # =====================================================
    # REBALANCE COMPLETE PORTFOLIO
    # =====================================================

    def rebalance(
        self,
        state,
        dry_run=True
    ):

        with self.lock:

            plan = (
                self.create_rebalance_plan(
                    state
                )
            )

            if plan is None:

                print(
                    "\n===== REBALANCE ABORTED ====="
                )

                return False

            self.print_rebalance_plan(
                plan
            )

            if dry_run:

                print(
                    "\n"
                    "========================================"
                )

                print(
                    "DRY RUN - NO ORDERS WILL BE PLACED"
                )

                print(
                    "========================================"
                )

            success = True

            for asset in [
                "BTC",
                "ETH",
                "SOL"
            ]:

                result = (
                    self.rebalance_asset(
                        plan[
                            "assets"
                        ][
                            asset
                        ],
                        dry_run=dry_run
                    )
                )

                if not result:

                    success = False

                    print(
                        f"\n===== {asset} REBALANCE FAILED ====="
                    )

            if success:

                if dry_run:

                    print(
                        "\n===== DRY RUN SUCCESSFUL ====="
                    )

                else:

                    print(
                        "\n===== PORTFOLIO REBALANCE COMPLETE ====="
                    )

            else:

                print(
                    "\n===== PORTFOLIO REBALANCE COMPLETED WITH ERRORS ====="
                )

            return success