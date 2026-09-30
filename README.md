# Mini Device Fleet Monitor

## 1. What the project does
A lightweight API service built to monitor a fleet of simulated hardware devices. It tracks device registrations, ingests real-time telemetry (heartbeats), and calculates the live `ONLINE`/`OFFLINE` status of the fleet based on a strict 30-second rolling activity window.

## 2. Design & Architecture
- **Framework:** FastAPI (Python) chosen for its high-performance asynchronous routing, built-in data validation (Pydantic), and automatic OpenAPI documentation.
- **State Management:** Abstracted into a separated `store.py` layer. Currently implemented as an in-memory dictionary for simplicity and speed, but structured so it can easily be swapped out for a persistent datastore in the future.
- **Timeout Logic:** Computed dynamically upon read requests (`GET`). The system compares the current UTC time against the timezone-aware timestamp of the last received heartbeat to ensure accuracy regardless of the host machine's local timezone.

## 3. Prerequisites
- Python 3.11+
- `uv` (Rust-based Python package manager)
- (Optional) Docker and Docker Compose

## 4. How to build the application
If running locally:
```bash
# Install uv for lightning-fast dependency resolution
pip install uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt