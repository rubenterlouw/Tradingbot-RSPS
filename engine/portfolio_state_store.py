import json
import os

from models.portfolio import PortfolioState
from initial_signals import INITIAL_SIGNALS


# =========================================================
# FILE LOCATIONS
# =========================================================

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(__file__)
)

STATE_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "state"
)

STATE_FILE = os.path.join(
    STATE_FOLDER,
    "rsps_state.json"
)


# =========================================================
# CREATE STATE FOLDER
# =========================================================

def ensure_state_folder():

    os.makedirs(
        STATE_FOLDER,
        exist_ok=True
    )


# =========================================================
# CREATE STATE FROM MANUAL INITIAL VALUES
# =========================================================

def create_initial_state():

    state = PortfolioState()

    for signal_name, signal_data in INITIAL_SIGNALS.items():

        value = signal_data.get("value")
        count = signal_data.get("count", 0)

        signal = state.get_signal(
            signal_name
        )

        signal.value = value
        signal.count = count

    return state


# =========================================================
# LOAD STATE
# =========================================================

def load_state():

    ensure_state_folder()

    # -----------------------------------------------------
    # NO SAVED STATE YET
    # -----------------------------------------------------

    if not os.path.exists(STATE_FILE):

        print(
            "\n===== NO SAVED RSPS STATE ====="
        )

        print(
            "Using values from initial_signals.py"
        )

        state = create_initial_state()

        save_state(state)

        return state

    # -----------------------------------------------------
    # LOAD SAVED STATE
    # -----------------------------------------------------

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        state = PortfolioState.from_dict(
            data
        )

        print(
            "\n===== RSPS STATE LOADED ====="
        )

        return state

    except Exception as error:

        print(
            "\n===== RSPS STATE LOAD ERROR ====="
        )

        print(
            repr(error)
        )

        print(
            "Falling back to initial_signals.py"
        )

        return create_initial_state()


# =========================================================
# SAVE STATE
# =========================================================

def save_state(state):

    ensure_state_folder()

    temporary_file = (
        STATE_FILE + ".tmp"
    )

    try:

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                state.to_dict(),
                file,
                indent=4
            )

        os.replace(
            temporary_file,
            STATE_FILE
        )

    except Exception as error:

        print(
            "\n===== RSPS STATE SAVE ERROR ====="
        )

        print(
            repr(error)
        )

        # Remove incomplete temporary file
        if os.path.exists(
            temporary_file
        ):

            try:
                os.remove(
                    temporary_file
                )
            except Exception:
                pass