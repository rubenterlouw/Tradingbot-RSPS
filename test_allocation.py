from datetime import datetime, timezone

from models.portfolio import PortfolioState
from engine.allocation import calculate_target_values


# =========================================================
# CREATE TEST STATE
# =========================================================

state = PortfolioState()


# ---------------------------------------------------------
# TOTAL MARKET TREND
# ---------------------------------------------------------

state.update_signal(
    signal_name="total_daily",
    value=0.3333,
    count=6
)

state.update_signal(
    signal_name="total_weekly",
    value=0.5,
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
# TEST ACCOUNT SIZE
# =========================================================

account_equity = 10000


# =========================================================
# FORCE A DATE FOR REPEATABLE TESTING
# =========================================================
#
# February = ETH season = 1
#
# Using a fixed date means this test always gives the
# same result regardless of when you run it.
# =========================================================

test_date = datetime(
    2026,
    2,
    1,
    tzinfo=timezone.utc
)


# =========================================================
# CALCULATE
# =========================================================

result = calculate_target_values(
    state=state,
    account_equity=account_equity,
    current_datetime=test_date
)


# =========================================================
# PRINT RESULT
# =========================================================

print("\n===== RSPS ALLOCATION TEST =====")

print(
    f"Account equity: "
    f"${result['account_equity']:.2f}"
)

print(
    f"TOTAL trend: "
    f"{result['total_trend']:.4f}"
)

print(
    f"Regime: "
    f"{result['regime']}"
)

print(
    f"ETH season: "
    f"{result['eth_season']:.0f}"
)

print(
    f"ETH/BTC signal: "
    f"{result['eth_btc_signal']:.4f}"
)

print(
    f"SOL strength: "
    f"{result['sol_strength']:.4f}"
)


print("\n===== ALLOCATIONS =====")

print(
    f"BTC: "
    f"{result['btc_allocation'] * 100:.2f}%"
)

print(
    f"ETH: "
    f"{result['eth_allocation'] * 100:.2f}%"
)

print(
    f"SOL: "
    f"{result['sol_allocation'] * 100:.2f}%"
)

print(
    f"Unused / cash: "
    f"{result['cash_allocation'] * 100:.2f}%"
)


print("\n===== TARGET POSITION VALUES =====")

print(
    f"BTC target: "
    f"${result['btc_target_usd']:.2f}"
)

print(
    f"ETH target: "
    f"${result['eth_target_usd']:.2f}"
)

print(
    f"SOL target: "
    f"${result['sol_target_usd']:.2f}"
)