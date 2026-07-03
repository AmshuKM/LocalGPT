import os
import sys
import time
import subprocess

import requests
import webview

# ======================================================
# Configuration
# ======================================================

APP_TITLE = "LocalGPT"

STREAMLIT_PORT = 8501
STREAMLIT_URL = f"http://127.0.0.1:{STREAMLIT_PORT}"

OLLAMA_URL = "http://127.0.0.1:11434"

OLLAMA_START_TIMEOUT = 30
STREAMLIT_START_TIMEOUT = 60

# Flag we pass to a second copy of ourselves to say
# "you are the Streamlit worker, not the launcher".
RUN_STREAMLIT_FLAG = "--run-streamlit"

# Are we running inside a PyInstaller build?
IS_FROZEN = getattr(sys, "frozen", False)

if IS_FROZEN:
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_PATH = os.path.join(BASE_DIR, "app.py")

CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


# ======================================================
# Helper Functions
# ======================================================

def _is_up(url, timeout=1):
    try:
        requests.get(url, timeout=timeout)
        return True
    except Exception:
        return False


def _terminate(process):
    if process is None:
        return
    try:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
    except Exception:
        pass


# ======================================================
# Streamlit worker (runs in the CHILD process, on its
# own main thread, so bootstrap's signal handler works)
# ======================================================

def run_streamlit_worker():
    from streamlit.web import bootstrap
    from streamlit import config as st_config

    st_config.set_option("server.port", STREAMLIT_PORT)
    st_config.set_option("server.headless", True)
    st_config.set_option("global.developmentMode", False)

    bootstrap.run(APP_PATH, False, [], {})


# ======================================================
# Ollama
# ======================================================

def start_ollama():
    if _is_up(OLLAMA_URL):
        print("\u2713 Ollama already running")
        return None

    print("Starting Ollama...")

    try:
        process = subprocess.Popen(
            ["ollama", "serve"],
            creationflags=CREATION_FLAGS
        )
    except FileNotFoundError:
        print(
            "ERROR: 'ollama' was not found on PATH. "
            "Install Ollama from https://ollama.com and try again."
        )
        return None

    deadline = time.time() + OLLAMA_START_TIMEOUT

    while not _is_up(OLLAMA_URL):
        if time.time() > deadline:
            print(f"ERROR: Ollama did not start within {OLLAMA_START_TIMEOUT}s.")
            return process
        time.sleep(1)

    print("\u2713 Ollama ready")
    return process


# ======================================================
# Streamlit launch (from the PARENT process)
# ======================================================

def start_streamlit():
    print("Starting Streamlit...")

    if IS_FROZEN:
        # Re-launch THIS exe with the worker flag. The child runs
        # Streamlit on its own main thread (see run_streamlit_worker),
        # which is required for Streamlit's SIGTERM handler.
        try:
            return subprocess.Popen(
                [sys.executable, RUN_STREAMLIT_FLAG],
                cwd=BASE_DIR,
                creationflags=CREATION_FLAGS,
            )
        except Exception as error:
            print(f"ERROR launching Streamlit worker: {error}")
            return None

    # Dev mode: plain `python -m streamlit run app.py`.
    try:
        return subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                APP_PATH,
                "--server.port",
                str(STREAMLIT_PORT),
                "--server.headless=true",
            ],
            cwd=BASE_DIR,
            creationflags=CREATION_FLAGS,
        )
    except FileNotFoundError:
        print(
            "ERROR: Could not launch Streamlit. "
            "Make sure it is installed:  pip install streamlit"
        )
        return None


def wait_for_streamlit():
    print("Waiting for Streamlit...")

    deadline = time.time() + STREAMLIT_START_TIMEOUT

    while time.time() < deadline:
        if _is_up(STREAMLIT_URL):
            print("\u2713 Streamlit ready")
            return True
        time.sleep(1)

    print(f"ERROR: Streamlit did not start within {STREAMLIT_START_TIMEOUT}s.")
    return False


# ======================================================
# Main (the launcher / parent process)
# ======================================================

def main():

    ollama_process = start_ollama()

    streamlit_process = start_streamlit()

    if not wait_for_streamlit():
        _terminate(streamlit_process)
        _terminate(ollama_process)
        return

    webview.create_window(
        title=APP_TITLE,
        url=STREAMLIT_URL,
        width=1400,
        height=900,
        min_size=(1000, 700),
        resizable=True,
    )

    webview.start(
        gui="edgechromium",
        debug=False
    )

    print("Closing LocalGPT...")

    _terminate(streamlit_process)
    _terminate(ollama_process)

    print("Goodbye!")


# ======================================================
# Entry Point
# ======================================================

if __name__ == "__main__":

    # If we were launched as the Streamlit worker, do only that.
    if RUN_STREAMLIT_FLAG in sys.argv:
        run_streamlit_worker()
    else:
        main()