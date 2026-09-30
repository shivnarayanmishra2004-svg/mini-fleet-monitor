Here is the full, final, simplified `README.md` ready to be copied and pasted directly into your project.

```markdown
# 📡 Mini Device Fleet Monitor

 What the project does
The Mini Device Fleet Monitor is a backend service designed to track a fleet of simulated devices. It provides REST APIs for devices to register and send periodic telemetry heartbeats. The system automatically determines if a device is `ONLINE` or `OFFLINE` based on a strict 30-second timeout threshold. A built-in simulator is included to generate mock telemetry and test the timeout behavior in real-time.

Design / Architecture
- **Framework:** FastAPI is used for the REST API due to its speed, built-in asynchronous capabilities, and automatic OpenAPI documentation.
- **Data Validation:** Pydantic models ensure all incoming JSON payloads are strictly type-checked and meet exact API requirements.
- **State Management:** Device data and heartbeats are stored in-memory using basic Python dictionaries. This prioritizes speed and simplicity for the scope of this assessment.
- **Timeout Logic:** Timezone-aware UTC datetimes are used to accurately calculate the elapsed time since the last heartbeat.
- **Simulator:** Uses standard Python threading (daemon threads) to run multiple simulated devices concurrently without requiring complex asynchronous event loops.

Prerequisites
- Python 3.11 or higher
- `pip`

## How to build the application
First, create a virtual environment and install the required dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt

```

## How to run the application

With your virtual environment activated, start the API server:

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000

```

*Note: API documentation (Swagger UI) is automatically generated and available at `http://127.0.0.1:8000/docs`.*

## How to run the simulator

While the API is running, open a new terminal tab, activate the virtual environment, and run the simulator script:

```bash
source .venv/bin/activate
python simulator/simulate.py

```

*The simulator registers 5 devices. `device-03` is intentionally programmed to stop sending heartbeats after 4 cycles so you can verify the OFFLINE timeout logic.*

## How to run the tests

Automated tests covering device registration, heartbeats, and the 30-second timeout logic are written using `pytest` and `httpx`.

```bash
pytest tests/ -v

```

## Example API Requests

**1. Register a Device**

```bash
curl -X POST [http://127.0.0.1:8000/devices](http://127.0.0.1:8000/devices) \
     -H "Content-Type: application/json" \
     -d '{"id": "device-01", "name": "Sensor Alpha"}'

```

**2. Send a Heartbeat**

```bash
curl -X POST [http://127.0.0.1:8000/devices/device-01/heartbeat](http://127.0.0.1:8000/devices/device-01/heartbeat) \
     -H "Content-Type: application/json" \
     -d '{"timestamp": "2026-09-30T10:30:00Z", "status": "OK"}'

```

**3. Get Fleet Summary**

```bash
curl [http://127.0.0.1:8000/summary](http://127.0.0.1:8000/summary)
# Example Response: {"total": 5, "online": 4, "offline": 1}

```

## Assumptions you made

* **In-Memory Storage:** Assumed that in-memory data structures are sufficient for the assessment constraints. Device data naturally resets on a server restart.
* **Client Time:** Assumed the timestamp provided by the client in the heartbeat payload is reliable and synchronized.
* **Concurrency:** Assumed Python's Global Interpreter Lock (GIL) provides sufficient atomic safety for simple dictionary updates at this specific scale.

## Known limitations

* **Data Persistence:** All fleet history and registration data is volatile and lost if the API server stops.
* **Horizontal Scaling:** The API is currently bound to a single worker process. Scaling to multiple workers would fail because state is not shared across processes.

## What I would improve if I had one additional day

1. **Proper PostgreSQL Database:** I would replace the in-memory dictionaries with a robust Postgres database (using SQLAlchemy/SQLModel) to persist device state and log historical telemetry safely.
2. **Handle High Concurrency:** I would load-test the API with thousands of devices and optimize the backend to handle massive concurrent incoming signals, potentially introducing a message queue (like RabbitMQ) to buffer heartbeats.
3. **Expanded Telemetry Signals:** I would expand the Pydantic schemas to accept, log, and track more detailed signals from the devices (e.g., CPU load, temperature, battery levels, firmware versions).
4. **Rich Interactive UI:** I would build a dedicated, interactive frontend web page that visualizes the devices and uses WebSockets for true real-time, low-latency updates instead of HTTP polling.

## 🤖 AI Usage

**Which AI tools you used:**

* Gemini

**What you used them for:**

* Generating boilerplate FastAPI endpoints and Pydantic models for data validation.
* Setting up the basic structural scaffolding for the `pytest` suite.

**One suggestion or piece of generated code that you changed, rejected, or improved:**

* The AI initially suggested using `asyncio` and `aiohttp` for the device simulator to handle concurrent requests. I rejected this and rewrote the simulator using standard Python `threading` and the synchronous `requests` library. Since the script only simulates 5 devices, a simple multithreaded approach is far more readable, less prone to event-loop locking issues, and requires fewer complex dependencies.

**One thing you personally verified before submitting:**

* I personally verified the core business logic: the 30-second offline timeout calculation. I ran the simulator, allowed `device-03` to intentionally drop its connection after 4 cycles, and actively monitored the `GET /summary` and `GET /devices` endpoints to guarantee the system successfully detected the missing heartbeats and flipped the device status from `ONLINE` to `OFFLINE` accurately.

```

```
