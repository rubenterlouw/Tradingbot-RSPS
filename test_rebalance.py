from models.portfolio import PortfolioState
from engine.portfolio_manager import PortfolioManager


# =========================================================
# CREATE TEST STATE
# =========================================================

state = PortfolioState()


# ---------------------------------------------------------
# TOTAL
# ---------------------------------------------------------

state.update_signal(
    signal_name="total_daily",
    value=-0.3333,
    count=6
)

state.update_signal(
    signal_name="total_weekly",
    value=-0.5,
    count=4
)


# ---------------------------------------------------------
# ETH / BTC
# ---------------------------------------------------------

state.update_signal(
    signal_name="eth_btc_daily",
    value=1.0,
    count=3
)

state.update_signal(
    signal_name="eth_btc_weekly",
    value=1.0,
    count=2
)


# ---------------------------------------------------------
# SOL
# ---------------------------------------------------------

state.update_signal(
    signal_name="sol_btc",
    value=0.8,
    count=4
)

state.update_signal(
    signal_name="sol_eth",
    value=0.8,
    count=4
)


# =========================================================
# PORTFOLIO MANAGER
# =========================================================

manager = PortfolioManager()


# =========================================================
# DRY RUN
# =========================================================
#
# IMPORTANT:
#
# dry_run=True means:
#
#   - account equity is read
#   - market prices are read
#   - current positions are read
#   - target portfolio is calculated
#   - differences are calculated
#
# BUT NO ORDERS ARE SENT.
#
# =========================================================

success = manager.rebalance(
    state=state,
    dry_run=False
)


print(
    "\n===== TEST FINISHED ====="
)

print(
    f"Success: {success}"
)