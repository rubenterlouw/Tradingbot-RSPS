from queue import Queue, Full
from threading import Thread

from config import TRADING_ENABLED


class RebalanceWorker:

    def __init__(
        self,
        portfolio_manager,
        state_provider
    ):

        self.portfolio_manager = (
            portfolio_manager
        )

        self.state_provider = (
            state_provider
        )

        # Only one pending rebalance is needed.
        #
        # If several TradingView alerts arrive quickly,
        # the worker will use the latest complete state.
        self.queue = Queue(
            maxsize=1
        )

        self.started = False

    # =====================================================
    # START WORKER
    # =====================================================

    def start(self):

        if self.started:
            return

        self.started = True

        thread = Thread(
            target=self._worker_loop,
            daemon=True
        )

        thread.start()

        print(
            "\n===== REBALANCE WORKER STARTED ====="
        )

    # =====================================================
    # REQUEST REBALANCE
    # =====================================================

    def request_rebalance(
        self,
        reason="unknown"
    ):

        try:

            self.queue.put_nowait(
                reason
            )

            print(
                "\n===== REBALANCE QUEUED ====="
            )

            print(
                f"Reason: {reason}"
            )

            return True

        except Full:

            print(
                "\n===== REBALANCE ALREADY QUEUED ====="
            )

            print(
                "Latest saved state will be used."
            )

            return False

    # =====================================================
    # WORKER LOOP
    # =====================================================

    def _worker_loop(self):

        while True:

            reason = (
                self.queue.get()
            )

            try:

                print(
                    "\n"
                    "========================================"
                )

                print(
                    "       BACKGROUND REBALANCE"
                )

                print(
                    "========================================"
                )

                print(
                    f"Reason: {reason}"
                )

                if not TRADING_ENABLED:

                    print(
                        "Trading disabled. "
                        "Rebalance skipped."
                    )

                    continue

                state = (
                    self.state_provider()
                )

                if not (
                    state.all_signals_ready()
                ):

                    print(
                        "Signals not ready. "
                        "Rebalance skipped."
                    )

                    continue

                success = (
                    self.portfolio_manager.rebalance(
                        state=state,
                        dry_run=False
                    )
                )

                if success:

                    print(
                        "\n===== BACKGROUND REBALANCE COMPLETE ====="
                    )

                else:

                    print(
                        "\n===== BACKGROUND REBALANCE FAILED ====="
                    )

            except Exception as error:

                print(
                    "\n===== REBALANCE WORKER ERROR ====="
                )

                print(
                    repr(error)
                )

            finally:

                self.queue.task_done()