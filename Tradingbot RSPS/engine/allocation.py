from datetime import datetime, timezone


# =========================================================
# STRATEGY CONSTANTS
# =========================================================

BTC_ETH_POOL = 0.80

MAX_SOL_ALLOCATION = 0.20

MIN_BTC_ETH_SHARE = 0.20
MAX_BTC_ETH_SHARE = 0.80

ETH_SEASON_INDICATOR_COUNT = 1

ZERO_TOLERANCE = 1e-9


# =========================================================
# BASIC HELPERS
# =========================================================

def clamp(value, minimum, maximum):

    return max(
        minimum,
        min(maximum, value)
    )


# =========================================================
# WEIGHTED SIGNAL
# =========================================================

def weighted_signal(*signals):
    """
    Combines normalized signals while respecting the
    number of indicators behind each signal.

    Example:

        Daily:
            value = 0.3333
            count = 6

        Weekly:
            value = 0.5
            count = 4

        Result:
            approximately 0.40
    """

    weighted_total = 0.0
    total_count = 0

    for signal in signals:

        if signal.value is None:
            raise ValueError(
                "Cannot calculate weighted signal: "
                "signal value is missing."
            )

        if signal.count <= 0:
            raise ValueError(
                "Cannot calculate weighted signal: "
                "indicator count must be greater than zero."
            )

        weighted_total += (
            float(signal.value) *
            int(signal.count)
        )

        total_count += int(
            signal.count
        )

    if total_count <= 0:

        raise ValueError(
            "Cannot calculate weighted signal: "
            "total indicator count is zero."
        )

    return weighted_total / total_count


# =========================================================
# ETH SEASON
# =========================================================

def get_eth_season_value(current_datetime=None):
    """
    ETH season:

        January 1 through May 31 = 1
        June 1 through December 31 = 0

    It has the same weighting as one normal indicator.
    """

    if current_datetime is None:

        current_datetime = datetime.now(
            timezone.utc
        )

    month = current_datetime.month

    if 1 <= month <= 5:
        return 1.0

    return 0.0


# =========================================================
# TOTAL MARKET TREND
# =========================================================

def calculate_total_trend(state):

    total_trend = weighted_signal(
        state.total_daily,
        state.total_weekly
    )

    # Small protection against values outside the
    # theoretical -1 to +1 range.
    return clamp(
        total_trend,
        -1.0,
        1.0
    )


# =========================================================
# ETH / BTC SIGNAL
# =========================================================

def calculate_eth_btc_signal(
    state,
    current_datetime=None
):

    eth_season = get_eth_season_value(
        current_datetime
    )

    daily = state.eth_btc_daily
    weekly = state.eth_btc_weekly

    if daily.value is None:
        raise ValueError(
            "ETH/BTC Daily signal is missing."
        )

    if weekly.value is None:
        raise ValueError(
            "ETH/BTC Weekly signal is missing."
        )

    if daily.count <= 0:
        raise ValueError(
            "ETH/BTC Daily indicator count is invalid."
        )

    if weekly.count <= 0:
        raise ValueError(
            "ETH/BTC Weekly indicator count is invalid."
        )

    # -----------------------------------------------------
    # DAILY + WEEKLY + ETH SEASON
    # -----------------------------------------------------

    weighted_total = (
        float(daily.value) * daily.count
        +
        float(weekly.value) * weekly.count
        +
        eth_season * ETH_SEASON_INDICATOR_COUNT
    )

    total_count = (
        daily.count
        +
        weekly.count
        +
        ETH_SEASON_INDICATOR_COUNT
    )

    value = (
        weighted_total /
        total_count
    )

    # ETH/BTC signal is expected between 0 and 1.
    return clamp(
        value,
        0.0,
        1.0
    )


# =========================================================
# SOL SIGNAL
# =========================================================

def calculate_sol_strength(state):
    """
    Combines SOL/BTC and SOL/ETH.

    Their indicator counts are respected so changing
    the number of indicators later does not require
    changing the Python strategy.
    """

    value = weighted_signal(
        state.sol_btc,
        state.sol_eth
    )

    return clamp(
        value,
        0.0,
        1.0
    )


# =========================================================
# BTC / ETH SPLIT
# =========================================================

def calculate_btc_eth_split(
    eth_btc_signal,
    regime
):
    """
    Returns BTC and ETH shares of the 80% BTC/ETH pool.

    LONG:
        ETH/BTC 0.70
        -> ETH 70%
        -> BTC 30%

    SHORT:
        ETH/BTC 0.70
        -> BTC 70%
        -> ETH 30%

    Neither asset can receive less than 20%
    of the BTC/ETH pool.
    """

    signal = clamp(
        eth_btc_signal,
        0.0,
        1.0
    )

    # -----------------------------------------------------
    # LONG REGIME
    # -----------------------------------------------------

    if regime == "LONG":

        eth_share = clamp(
            signal,
            MIN_BTC_ETH_SHARE,
            MAX_BTC_ETH_SHARE
        )

        btc_share = (
            1.0 - eth_share
        )

    # -----------------------------------------------------
    # SHORT REGIME
    # -----------------------------------------------------

    elif regime == "SHORT":

        btc_share = clamp(
            signal,
            MIN_BTC_ETH_SHARE,
            MAX_BTC_ETH_SHARE
        )

        eth_share = (
            1.0 - btc_share
        )

    else:

        return {
            "btc_share": 0.0,
            "eth_share": 0.0
        }

    return {
        "btc_share": btc_share,
        "eth_share": eth_share
    }


# =========================================================
# COMPLETE PORTFOLIO ALLOCATION
# =========================================================

def calculate_allocations(
    state,
    current_datetime=None
):
    """
    Calculates target portfolio allocations.

    Positive TOTAL:
        BTC + ETH = 80% LONG
        SOL = 0-20% LONG
        unused SOL allocation remains cash

    Negative TOTAL:
        BTC + ETH = 80% SHORT
        SOL = 0
        remaining 20% is unused

    TOTAL == 0:
        no positions
    """

    if not state.all_signals_ready():

        raise ValueError(
            "Cannot calculate allocations: "
            "not all six signals are available."
        )

    # -----------------------------------------------------
    # CALCULATE STRATEGY SIGNALS
    # -----------------------------------------------------

    total_trend = calculate_total_trend(
        state
    )

    eth_btc_signal = (
        calculate_eth_btc_signal(
            state,
            current_datetime
        )
    )

    sol_strength = calculate_sol_strength(
        state
    )

    eth_season = get_eth_season_value(
        current_datetime
    )

    # -----------------------------------------------------
    # DETERMINE MARKET REGIME
    # -----------------------------------------------------

    if abs(total_trend) <= ZERO_TOLERANCE:

        regime = "CASH"

    elif total_trend > 0:

        regime = "LONG"

    else:

        regime = "SHORT"

    # -----------------------------------------------------
    # CASH REGIME
    # -----------------------------------------------------

    if regime == "CASH":

        return {
            "regime": "CASH",

            "total_trend": total_trend,
            "eth_btc_signal": eth_btc_signal,
            "sol_strength": sol_strength,
            "eth_season": eth_season,

            "btc_allocation": 0.0,
            "eth_allocation": 0.0,
            "sol_allocation": 0.0,

            "cash_allocation": 1.0
        }

    # -----------------------------------------------------
    # BTC / ETH SPLIT
    # -----------------------------------------------------

    split = calculate_btc_eth_split(
        eth_btc_signal,
        regime
    )

    btc_allocation = (
        BTC_ETH_POOL *
        split["btc_share"]
    )

    eth_allocation = (
        BTC_ETH_POOL *
        split["eth_share"]
    )

    # -----------------------------------------------------
    # LONG REGIME
    # -----------------------------------------------------

    if regime == "LONG":

        sol_allocation = (
            MAX_SOL_ALLOCATION *
            sol_strength
        )

        cash_allocation = (
            1.0
            -
            btc_allocation
            -
            eth_allocation
            -
            sol_allocation
        )

    # -----------------------------------------------------
    # SHORT REGIME
    # -----------------------------------------------------

    else:

        # No SOL short position.
        sol_allocation = 0.0

        # BTC/ETH total short exposure is 80%.
        # The remaining 20% is unused.
        cash_allocation = (
            1.0 - BTC_ETH_POOL
        )

    return {
        "regime": regime,

        "total_trend": total_trend,
        "eth_btc_signal": eth_btc_signal,
        "sol_strength": sol_strength,
        "eth_season": eth_season,

        "btc_allocation": btc_allocation,
        "eth_allocation": eth_allocation,
        "sol_allocation": sol_allocation,

        "cash_allocation": cash_allocation
    }


# =========================================================
# CONVERT ALLOCATIONS TO USD TARGETS
# =========================================================

def calculate_target_values(
    state,
    account_equity,
    current_datetime=None
):
    """
    Converts the target portfolio percentages into
    USD position values.

    SHORT values are returned as negative numbers.
    """

    allocations = calculate_allocations(
        state,
        current_datetime
    )

    equity = float(
        account_equity
    )

    if equity <= 0:

        raise ValueError(
            "Account equity must be greater than zero."
        )

    regime = allocations["regime"]

    # -----------------------------------------------------
    # CASH
    # -----------------------------------------------------

    if regime == "CASH":

        btc_target = 0.0
        eth_target = 0.0
        sol_target = 0.0

    # -----------------------------------------------------
    # LONG
    # -----------------------------------------------------

    elif regime == "LONG":

        btc_target = (
            equity *
            allocations["btc_allocation"]
        )

        eth_target = (
            equity *
            allocations["eth_allocation"]
        )

        sol_target = (
            equity *
            allocations["sol_allocation"]
        )

    # -----------------------------------------------------
    # SHORT
    # -----------------------------------------------------

    else:

        btc_target = -(
            equity *
            allocations["btc_allocation"]
        )

        eth_target = -(
            equity *
            allocations["eth_allocation"]
        )

        sol_target = 0.0

    return {
        **allocations,

        "account_equity": equity,

        "btc_target_usd": btc_target,
        "eth_target_usd": eth_target,
        "sol_target_usd": sol_target
    }