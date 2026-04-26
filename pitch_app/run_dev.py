import subprocess
import sys
import signal
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
WATCHER = BASE_DIR / "materials_watcher.py"

def main():
    watcher = subprocess.Popen([sys.executable, str(WATCHER)])

    api = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "pitch_app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ])

    def shutdown(*_):
        for proc in (api, watcher):
            if proc and proc.poll() is None:
                proc.terminate()
        time.sleep(0.5)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        api.wait()
    finally:
        shutdown()

if __name__ == "__main__":
    main()