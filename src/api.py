import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Smart Campus Digital Twin API Gateway",
    description="REST API layer serving real-time IoT metrics from the sensor pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DB CONNECTION FACTORY ---
# cursor_factory cannot live in DB_PARAMS for psycopg2.connect()
# It must be passed separately when creating the cursor
DB_PARAMS = {
   "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "smart_infrastructure_db"),
    "user": os.getenv("DB_USER", "admin_fares"),
    "password": os.getenv("DB_PASSWORD", "SuperSecurePassword2026")
}

def get_connection():
    """Creates and returns a fresh database connection."""
    return psycopg2.connect(**DB_PARAMS)


# --- ENDPOINT: SYSTEM HEALTH CHECK ---
@app.get("/health", tags=["System"])
def health_check():
    """Verifies the API gateway and database are both alive."""
    conn = None
    try:
        conn = get_connection()
        return {"status": "online", "system": "digital-twin-core", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database unreachable: {e}")
    finally:
        if conn:
            conn.close()


# --- ENDPOINT: ALL REGISTERED SENSORS ---
@app.get("/api/sensors", tags=["Sensors"])
def get_all_sensors():
    """Returns the full registry of all sensors in the infrastructure."""
    conn = None
    try:
        conn = get_connection()
        # cursor_factory goes here, not in DB_PARAMS
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT sensor_id, sensor_name, sensor_type, location_zone, status, created_at
            FROM sensors
            ORDER BY created_at DESC;
        """)
        records = cursor.fetchall()
        cursor.close()
        return {"count": len(records), "data": records}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()


# --- ENDPOINT: LIVE SENSOR SNAPSHOTS ---
@app.get("/api/sensors/live", tags=["Telemetry"])
def get_live_sensors():
    """Fetches the latest reading for every registered sensor."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # DISTINCT ON pattern — gets most recent row per sensor
        cursor.execute("""
            SELECT DISTINCT ON (l.sensor_id)
                l.sensor_id,
                s.sensor_type,
                s.location_zone,
                l.reading_value,
                l.recorded_at
            FROM sensor_data_logs l
            JOIN sensors s ON l.sensor_id = s.sensor_id
            ORDER BY l.sensor_id, l.recorded_at DESC;
        """)
        records = cursor.fetchall()
        cursor.close()
        return {"count": len(records), "data": records}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()


# --- ENDPOINT: SENSOR HISTORY ---
@app.get("/api/sensors/{sensor_id}/history", tags=["Telemetry"])
def get_sensor_history(sensor_id: str, limit: int = 50):
    """
    Returns the last N readings for a specific sensor.
    Example: /api/sensors/SENSOR-TEMP-01/history?limit=100
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # First verify the sensor actually exists
        cursor.execute(
            "SELECT sensor_id FROM sensors WHERE sensor_id = %s;",
            (sensor_id,)
        )
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail=f"Sensor '{sensor_id}' not found")

        cursor.execute("""
            SELECT log_id, sensor_id, reading_value, recorded_at
            FROM sensor_data_logs
            WHERE sensor_id = %s
            ORDER BY recorded_at DESC
            LIMIT %s;
        """, (sensor_id, limit))

        records = cursor.fetchall()
        cursor.close()
        return {"sensor_id": sensor_id, "count": len(records), "data": records}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if conn:
            conn.close()