import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# --- SYSTEM CONFIGURATION ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
PUBLISH_INTERVAL_SECONDS = 3

# Simulated Sensor Network Inventory
SENSORS_CONFIG = [
    {"id": "SENSOR-TEMP-01", "type": "Temperature", "location": "Amphi-A", "unit": "°C", "range": (18.0, 26.0)},
    {"id": "SENSOR-HUM-01", "type": "Humidity", "location": "Amphi-A", "unit": "%", "range": (40.0, 60.0)},
    {"id": "SENSOR-PWR-01", "type": "Power_Consumption", "location": "Server-Room", "unit": "kWh", "range": (1.2, 5.5)}
]

# --- MQTT LIFECYCLE CALLBACKS ---
def on_connect(client, userdata, flags, reason_code, properties=None):
    """Executes automatically the moment the script authenticates with Mosquitto."""
    if reason_code == 0:
        print("[SUCCESS] Connected to MQTT Broker successfully.")
    else:
        print(f"[ERROR] Connection failed with Reason Code: {reason_code}")

def generate_telemetry_payload(sensor):
    """Simulates real-world data drift and constructs a unified JSON packet."""
    low, high = sensor["range"]
    simulated_value = round(random.uniform(low, high), 2)
    
    payload = {
        "sensor_id": sensor["id"],
        "type": sensor["type"],
        "location": sensor["location"],
        "value": simulated_value,
        "unit": sensor["unit"],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return payload

# --- CORE ORCHESTRATION ENGINE ---
def run_simulator():
    print("=== STARTING SMART INFRASTRUCTURE EDGE SIMULATOR ===")
    
    # Instantiate client utilizing modern explicit v2 Callback Architecture
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="Campus_Edge_Simulator"
    )
    
    # Bind our lifecycle callback functions
    client.on_connect = on_connect
    
    try:
        # Establish network connection to the Docker container
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        # Spin up a non-blocking background thread to process network traffic
        client.loop_start()
        
        while True:
            for sensor in SENSORS_CONFIG:
                # 1. Generate the randomized data point
                data_packet = generate_telemetry_payload(sensor)
                json_payload = json.dumps(data_packet)
                
                # 2. Build a structured enterprise topic path
                topic = f"campus/sensors/{sensor['type'].lower()}/{sensor['id']}"
                
                # 3. Broadcast the data packet to the broker
                client.publish(topic, json_payload, qos=1)
                print(f"[PUBLISHED] Topic: {topic} -> Value: {data_packet['value']} {data_packet['unit']}")
            
            print("-" * 50)
            time.sleep(PUBLISH_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Gracefully stopping simulator streams...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[SHUTDOWN] MQTT disconnected. Cleanup complete.")

if __name__ == "__main__":
    run_simulator()