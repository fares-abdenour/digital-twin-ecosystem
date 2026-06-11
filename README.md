\#  Smart Campus Digital Twin Ecosystem



A real-time IoT data pipeline that captures simulated smart building metrics, streams them through an MQTT message broker, persists them in a relational database, and exposes them via a REST API — all orchestrated with Docker.



\---



\##  System Architecture



\[Python Edge Simulator]

│

│  MQTT (port 1883, QoS 1)

▼

\[Eclipse Mosquitto Broker]

│

│  Subscribe (campus/sensors/#)

▼

\[Python Ingestion Consumer]

│

│  psycopg2

▼

\[PostgreSQL Database] ──── \[FastAPI REST Gateway]

│

│  HTTP (port 8000)

▼

\[Live Web Dashboard]



\##  Tech Stack



| Layer | Technology |

|---|---|

| Edge Simulation | Python 3.13, Paho MQTT v2 |

| Message Broker | Eclipse Mosquitto 2.0 |

| Ingestion Engine | Python 3.13, psycopg2 |

| Database | PostgreSQL 15 (Alpine) |

| API Gateway | FastAPI, Uvicorn |

| Infrastructure | Docker, Docker Compose |



\---



\##  How to Run the Full Ecosystem



\### Prerequisites

\- Docker Desktop installed and running

\- Python 3.10+ installed

\- Git



\### 1. Clone the repository

```bash

git clone https://github.com/YOUR\_USERNAME/digital-twin-ecosystem.git

cd digital-twin-ecosystem

```



\### 2. Configure environment variables

```bash

\# Copy the example env file

cp .env.example .env

\# Open .env and fill in your credentials

```



\### 3. Launch the infrastructure

```bash

docker compose up -d

```



Both containers will start:

\- `digital\_twin\_postgres` — PostgreSQL database on port 5432

\- `digital\_twin\_mqtt` — Mosquitto broker on port 1883



\### 4. Install Python dependencies

```bash

pip install -r requirements.txt

```



\### 5. Start the ingestion consumer

```bash

python src/consumer.py

```



\### 6. Start the edge simulator (new terminal)

```bash

python src/simulator.py

```



\### 7. Start the API gateway (new terminal)

```bash

uvicorn src.api:app --reload --port 8000

```



\### 8. Verify the pipeline

Open your browser at:

\- \*\*API Docs:\*\* http://127.0.0.1:8000/docs

\- \*\*Live Data:\*\* http://127.0.0.1:8000/api/sensors/live

\- \*\*Health Check:\*\* http://127.0.0.1:8000/health



\---



\##  API Endpoints



| Method | Endpoint | Description |

|---|---|---|

| GET | `/health` | System and database health check |

| GET | `/api/sensors` | All registered sensors |

| GET | `/api/sensors/live` | Latest reading per sensor |

| GET | `/api/sensors/{id}/history` | Historical readings for one sensor |



\---



\##  Database Schema



\### `sensors` — Asset Registry

| Column | Type | Description |

|---|---|---|

| sensor\_id | VARCHAR PK | Unique sensor identifier |

| sensor\_name | VARCHAR | Human-readable name |

| sensor\_type | VARCHAR | TEMPERATURE, HUMIDITY, POWER |

| location\_zone | VARCHAR | Physical location |

| status | VARCHAR | ACTIVE, MAINTENANCE, OFFLINE |



\### `sensor\_data\_logs` — Telemetry Store

| Column | Type | Description |

|---|---|---|

| log\_id | BIGSERIAL PK | Auto-increment log ID |

| sensor\_id | VARCHAR FK | References sensors table |

| reading\_value | NUMERIC | The measured value |

| recorded\_at | TIMESTAMP | UTC timestamp from edge node |



\---



\##  Security Notes

\- All credentials are stored in `.env` and never committed to version control

\- `.env.example` is provided as a safe template with no real values

\- MQTT is configured for local development only (anonymous auth disabled in production)



\---



\##  Project Structure



digital-twin-ecosystem/

│   docker-compose.yml      # Infrastructure orchestration

│   requirements.txt        # Python dependencies

│   .env.example            # Credential template

│   README.md

│

├───database/

│       schema.sql          # PostgreSQL table definitions

│

├───mosquitto/

│   └───config/

│           mosquitto.conf  # Broker configuration

│

└───src/

simulator.py        # IoT edge device simulation

consumer.py         # MQTT to PostgreSQL ingestion

api.py              # FastAPI REST gateway





\---



\##  Author

\*\*Fares\*\* — Computer Science Student, incoming M1 MIAGE



