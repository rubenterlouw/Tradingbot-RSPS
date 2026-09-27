# =========================================================
# RSPS INITIAL SIGNAL VALUES
# =========================================================
#
# These values are only used when the bot has no saved
# RSPS state yet.
#
# Enter the CURRENT values from TradingView before starting
# the bot for the first time.
#
# After startup, TradingView webhook updates will replace
# these values automatically and they will be saved to state.
#
# Leave a value as None if you do not know it yet.
# The bot will not trade until all six values are available.
# =========================================================


INITIAL_SIGNALS = {
    #----------------------------------------------------
    # Total Market Trend
    # Range: -1 to 1 
    #----------------------------------------------------

    "total_daily": {
        "value": 1,
        "count": 6
    },

    "total_weekly": {
        "value": 1,
        "count": 4
    },

    # -----------------------------------------------------
    # ETH / BTC RELATIVE STRENGTH
    # Range: 0 to 1
    # ----------------------------------------------------- 

    "eth_btc_daily": {
        "value": 1,
        "count": 3
    },

    "eth_btc_weekly": {
        "value": 1,
        "count": 2
    },

    # -----------------------------------------------------
    # SOL RELATIVE STRENGTH
    # Range: 0 to 1
    # -----------------------------------------------------

    "sol_btc": {
        "value": 1,
        "count": 4
    },

    "sol_eth": {
        "value": 1,
        "count": 4
    }
}