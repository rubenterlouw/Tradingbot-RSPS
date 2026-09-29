from bybit.client import session
from bybit.instruments import normalize_quantity


# =========================================================
# GENERIC MARKET ORDER
# =========================================================

def place_market_order(
    symbol,
    side,
    qty,
    reduce_only=False
):
    """
    Places a market order.

    side:
        Buy
        Sell

    reduce_only:
        False -> open/increase position
        True  -> reduce/close position
    """

    normalized_qty = normalize_quantity(
        symbol,
        qty
    )

    if normalized_qty is None:

        return {
            "success": False,
            "error": "Invalid quantity for instrument"
        }

    try:

        response = session.place_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=normalized_qty,
            reduceOnly=reduce_only,
            positionIdx=0
        )

    except Exception as error:

        print("\n===== MARKET ORDER ERROR =====")
        print(repr(error))

        return {
            "success": False,
            "error": str(error)
        }

    print("\n===== MARKET ORDER RESPONSE =====")
    print(response)

    if response["retCode"] == 0:

        return {
            "success": True,
            "order_id":
                response["result"]["orderId"]
        }

    return {
        "success": False,
        "error": response
    }


# =========================================================
# PARTIAL CLOSE
# =========================================================

def close_partial_position(
    symbol,
    side,
    qty
):

    return place_market_order(
        symbol=symbol,
        side=side,
        qty=qty,
        reduce_only=True
    )


# =========================================================
# FULL CLOSE
# =========================================================

def close_position(
    symbol,
    side,
    qty
):

    return place_market_order(
        symbol=symbol,
        side=side,
        qty=qty,
        reduce_only=True
    )