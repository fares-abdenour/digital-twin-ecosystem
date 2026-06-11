import json
import psycopg2
from datetime import datetime
import paho.mqtt.client as mqtt

# --- CONFIGURATION CORES ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "campus/sensors/#"

DB_PARAMS = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "smart_infrastructure_db",
    "user": "admin_fares",
    "password": "SuperSecurePassword2026"
}

# --- DATABASE PERSISTENCE LOGIC ---
def save_to_database(payload):
    """Safely injects parsed JSON telemetry into PostgreSQL using parameterized queries."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # 1. Upsert sensor metadata — mapped to the REAL schema column names
        sensor_upsert_query = """
            INSERT INTO sensors (sensor_id, sensor_name, sensor_type, location_zone, status)
            VALUES (%s, %s, %s, %s, 'ACTIVE')
            ON CONFLICT (sensor_id) DO NOTHING;
        """
        cursor.execute(sensor_upsert_query, (
            payload["sensor_id"],
            payload["sensor_id"],   # using sensor_id as name since simulator doesn't send a name
            payload["type"],        # simulator sends "type" -> maps to sensor_type column
            payload["location"]     # simulator sends "location" -> maps to location_zone column
        ))

        # 2. Insert time-series telemetry — mapped to the REAL schema column names
        log_insert_query = """
            INSERT INTO sensor_data_logs (sensor_id, reading_value, recorded_at)
            VALUES (%s, %s, %s);
        """
        cursor.execute(log_insert_query, (
            payload["sensor_id"],
            payload["value"],       # simulator sends "value" -> maps to reading_value column
            payload["timestamp"]    # simulator sends "timestamp" -> maps to recorded_at column
        ))

        conn.commit()
        print(f"[DATABASE SUCCESS] Recorded {payload['sensor_id']} -> {payload['value']} {payload['unit']}")
        cursor.close()

    except Exception as e:
        print(f"[DATABASE ERROR] Failed to write to Postgres: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# --- MQTT LIFECYCLE CALLBACKS ---
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("[SUCCESS] Consumer connected to MQTT Broker.")
        client.subscribe(MQTT_TOPIC, qos=1)
        print(f"[SUBSCRIBED] Listening for streams on: {MQTT_TOPIC}")
    else:
        print(f"[ERROR] Consumer connection failed: {reason_code}")

def on_message(client, userdata, msg):
    """Executes automatically every time a sensor broadcasts a message."""
    try:
        raw_payload = msg.payload.decode("utf-8")
        data_packet = json.loads(raw_payload)
        save_to_database(data_packet)
    except Exception as e:
        print(f"[PARSING ERROR] Malformed message on topic {msg.topic}: {e}")

# --- ORCHESTRATION ENGINE ---
def run_consumer():
    print("=== STARTING SMART INFRASTRUCTURE INGESTION ENGINE ===")

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="Campus_Data_Consumer"
    )

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping Ingestion Engine gracefully...")
    finally:
        client.disconnect()
        print("[SHUTDOWN] Consumer stopped.")

if __name__ == "__main__":
    run_consumer()