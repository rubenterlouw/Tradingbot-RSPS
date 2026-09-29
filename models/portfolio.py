from dataclasses import dataclass, field
from typing import Optional


# =========================================================
# INDIVIDUAL SIGNAL
# =========================================================

@dataclass
class SignalState:

    value: Optional[float] = None
    count: int = 0

    timeframe: Optional[str] = None
    bar_time: Optional[int] = None
    signal_id: Optional[str] = None

    # -----------------------------------------------------
    # CONVERT TO DICTIONARY
    # -----------------------------------------------------

    def to_dict(self):

        return {
            "value": self.value,
            "count": self.count,
            "timeframe": self.timeframe,
            "bar_time": self.bar_time,
            "signal_id": self.signal_id
        }

    # -----------------------------------------------------
    # CREATE FROM DICTIONARY
    # -----------------------------------------------------

    @classmethod
    def from_dict(cls, data):

        if data is None:
            return cls()

        return cls(
            value=data.get("value"),
            count=data.get("count", 0),
            timeframe=data.get("timeframe"),
            bar_time=data.get("bar_time"),
            signal_id=data.get("signal_id")
        )


# =========================================================
# COMPLETE RSPS STATE
# =========================================================

@dataclass
class PortfolioState:

    # TOTAL market trend
    total_daily: SignalState = field(
        default_factory=SignalState
    )

    total_weekly: SignalState = field(
        default_factory=SignalState
    )

    # ETH / BTC relative strength
    eth_btc_daily: SignalState = field(
        default_factory=SignalState
    )

    eth_btc_weekly: SignalState = field(
        default_factory=SignalState
    )

    # SOL relative strength
    sol_btc: SignalState = field(
        default_factory=SignalState
    )

    sol_eth: SignalState = field(
        default_factory=SignalState
    )

    # Duplicate signal protection
    processed_signal_ids: list = field(
        default_factory=list
    )

    # ETH season state
    last_eth_season: Optional[int] = None

    # -----------------------------------------------------
    # GET SIGNAL
    # -----------------------------------------------------

    def get_signal(self, signal_name):

        if not hasattr(self, signal_name):

            raise ValueError(
                f"Unknown signal name: {signal_name}"
            )

        return getattr(
            self,
            signal_name
        )

    # -----------------------------------------------------
    # UPDATE SIGNAL
    # -----------------------------------------------------

    def update_signal(
        self,
        signal_name,
        value,
        count,
        timeframe=None,
        bar_time=None,
        signal_id=None
    ):

        signal = self.get_signal(
            signal_name
        )

        signal.value = float(
            value
        )

        signal.count = int(
            count
        )

        signal.timeframe = timeframe
        signal.bar_time = bar_time
        signal.signal_id = signal_id

    # -----------------------------------------------------
    # CHECK IF ALL SIGNALS EXIST
    # -----------------------------------------------------

    def all_signals_ready(self):

        required_signals = [
            self.total_daily,
            self.total_weekly,
            self.eth_btc_daily,
            self.eth_btc_weekly,
            self.sol_btc,
            self.sol_eth
        ]

        for signal in required_signals:

            if signal.value is None:
                return False

            if signal.count <= 0:
                return False

        return True

    # -----------------------------------------------------
    # DUPLICATE SIGNAL CHECK
    # -----------------------------------------------------

    def is_duplicate(self, signal_id):

        if signal_id is None:
            return False

        return (
            signal_id
            in self.processed_signal_ids
        )

    # -----------------------------------------------------
    # REMEMBER SIGNAL ID
    # -----------------------------------------------------

    def remember_signal(self, signal_id):

        if signal_id is None:
            return

        if (
            signal_id
            in self.processed_signal_ids
        ):
            return

        self.processed_signal_ids.append(
            signal_id
        )

        # Keep only most recent 1000 IDs
        if len(
            self.processed_signal_ids
        ) > 1000:

            self.processed_signal_ids = (
                self.processed_signal_ids[-1000:]
            )

    # -----------------------------------------------------
    # CONVERT COMPLETE STATE TO DICTIONARY
    # -----------------------------------------------------

    def to_dict(self):

        return {
            "total_daily":
                self.total_daily.to_dict(),

            "total_weekly":
                self.total_weekly.to_dict(),

            "eth_btc_daily":
                self.eth_btc_daily.to_dict(),

            "eth_btc_weekly":
                self.eth_btc_weekly.to_dict(),

            "sol_btc":
                self.sol_btc.to_dict(),

            "sol_eth":
                self.sol_eth.to_dict(),

            "processed_signal_ids":
                self.processed_signal_ids,

            "last_eth_season":
                self.last_eth_season
        }

    # -----------------------------------------------------
    # CREATE COMPLETE STATE FROM DICTIONARY
    # -----------------------------------------------------

    @classmethod
    def from_dict(cls, data):

        return cls(

            total_daily=SignalState.from_dict(
                data.get("total_daily")
            ),

            total_weekly=SignalState.from_dict(
                data.get("total_weekly")
            ),

            eth_btc_daily=SignalState.from_dict(
                data.get("eth_btc_daily")
            ),

            eth_btc_weekly=SignalState.from_dict(
                data.get("eth_btc_weekly")
            ),

            sol_btc=SignalState.from_dict(
                data.get("sol_btc")
            ),

            sol_eth=SignalState.from_dict(
                data.get("sol_eth")
            ),

            processed_signal_ids=data.get(
                "processed_signal_ids",
                []
            ),

            last_eth_season=data.get(
                "last_eth_season"
            )
        )