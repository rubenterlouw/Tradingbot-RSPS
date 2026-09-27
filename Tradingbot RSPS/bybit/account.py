from bybit.client import session


# =========================================================
# GET ACCOUNT EQUITY
# =========================================================

def get_account_equity():
    """
    Returns the total Bybit Unified account equity in USD.

    Example:
        10000.25

    Returns None if the API request fails.
    """

    try:

        response = session.get_wallet_balance(
            accountType="UNIFIED"
        )

    except Exception as error:

        print("\n===== ACCOUNT EQUITY REQUEST ERROR =====")
        print(repr(error))

        return None

    # -----------------------------------------------------
    # CHECK BYBIT RESPONSE
    # -----------------------------------------------------

    if response["retCode"] != 0:

        print("\n===== ACCOUNT EQUITY REQUEST FAILED =====")
        print(response)

        return None

    accounts = response["result"]["list"]

    if not accounts:

        print("\n===== NO ACCOUNT DATA RETURNED =====")

        return None

    # -----------------------------------------------------
    # TOTAL EQUITY
    # -----------------------------------------------------

    try:

        total_equity = float(
            accounts[0]["totalEquity"]
        )

    except (KeyError, TypeError, ValueError):

        print("\n===== INVALID ACCOUNT EQUITY DATA =====")
        print(response)

        return None

    return total_equity