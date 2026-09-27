from bybit.client import session


# =========================================================
# GET POSITION
# =========================================================

def get_position(symbol):
    """
    Returns the current one-way Bybit position.

    Example LONG:

        {
            "symbol": "BTCUSDT",
            "side": "Buy",
            "size": 0.01,
            "signed_size": 0.01,
            "avg_price": 65000.0
        }

    Example SHORT:

        {
            "symbol": "BTCUSDT",
            "side": "Sell",
            "size": 0.01,
            "signed_size": -0.01,
            "avg_price": 65000.0
        }

    No position:

        signed_size = 0

    Returns None if the API request fails.
    """

    try:

        response = session.get_positions(
            category="linear",
            symbol=symbol
        )

    except Exception as error:

        print("\n===== POSITION REQUEST ERROR =====")
        print(repr(error))

        return None

    # -----------------------------------------------------
    # CHECK RESPONSE
    # -----------------------------------------------------

    if response["retCode"] != 0:

        print("\n===== GET POSITION FAILED =====")
        print(response)

        return None

    positions = response["result"]["list"]

    # -----------------------------------------------------
    # FIND ACTIVE POSITION
    # -----------------------------------------------------

    active_positions = []

    for position in positions:

        size = float(
            position.get("size", 0)
        )

        if size <= 0:
            continue

        active_positions.append(
            position
        )

    # -----------------------------------------------------
    # NO POSITION
    # -----------------------------------------------------

    if not active_positions:

        return {
            "symbol": symbol,
            "side": "",
            "size": 0.0,
            "signed_size": 0.0,
            "avg_price": 0.0
        }

    # -----------------------------------------------------
    # SAFETY CHECK
    # -----------------------------------------------------
    #
    # This RSPS bot is designed for Bybit One-Way Mode.
    # Hedge Mode could return separate LONG and SHORT
    # positions for the same symbol.
    # -----------------------------------------------------

    if len(active_positions) > 1:

        print(
            f"\n===== MULTIPLE POSITIONS FOUND FOR {symbol} ====="
        )

        print(
            "RSPS currently requires Bybit One-Way Mode."
        )

        return None

    position = active_positions[0]

    side = position["side"]

    size = float(
        position["size"]
    )

    avg_price = float(
        position.get("avgPrice", 0) or 0
    )

    # -----------------------------------------------------
    # CREATE SIGNED SIZE
    # -----------------------------------------------------

    if side == "Buy":

        signed_size = size

    elif side == "Sell":

        signed_size = -size

    else:

        signed_size = 0.0

    return {
        "symbol": symbol,
        "side": side,
        "size": size,
        "signed_size": signed_size,
        "avg_price": avg_price
    }


# =========================================================
# SIGNED POSITION SIZE
# =========================================================

def get_signed_position_size(symbol):

    position = get_position(
        symbol
    )

    if position is None:
        return None

    return position[
        "signed_size"
    ]


# =========================================================
# OLD COMPATIBILITY FUNCTION
# =========================================================

def get_position_size(symbol, direction):
    """
    Compatibility helper for older code.

    LONG returns current long size.
    SHORT returns current short size.
    """

    position = get_position(
        symbol
    )

    if position is None:
        return None

    if (
        direction == "LONG"
        and position["side"] == "Buy"
    ):

        return position["size"]

    if (
        direction == "SHORT"
        and position["side"] == "Sell"
    ):

        return position["size"]

    return 0.0