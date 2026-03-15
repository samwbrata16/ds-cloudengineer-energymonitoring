import json
import os
import random
import signal
import threading
import time
from datetime import datetime, timezone

import pika
from dotenv import load_dotenv

load_dotenv()

CLOUDAMQP_URL = os.getenv("CLOUDAMQP_URL")
QUEUE_NAME = "energy_telemetry"

RUNNING = True


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_payload(device_id: str) -> dict:
    return {
        "device_id": device_id,
        "voltage": round(random.uniform(120, 250), 2),
        "current": round(random.uniform(1, 10), 2),
        "energy": round(random.uniform(10, 20), 2),
        "power_factor": round(random.uniform(0, 1), 2),
        "frequency": round(random.uniform(50, 60), 2),
        "signal_rssi": random.randint(-95, -50),
        "ts": now_iso(),
    }


def device_loop(device_id: str, interval_range=(2, 6)) -> None:
    params = pika.URLParameters(CLOUDAMQP_URL)
    params.socket_timeout = 5

    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    try:
        while RUNNING:
            payload = make_payload(device_id)
            body = json.dumps(payload)
            channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=body)
            print(f"[PUB] {device_id} -> {body}")
            time.sleep(random.uniform(*interval_range))
    finally:
        connection.close()


def stop_handler(signum, frame) -> None:
    del signum, frame
    global RUNNING
    RUNNING = False


def main(num_devices: int = 20) -> None:
    if not CLOUDAMQP_URL:
        raise RuntimeError("Missing CLOUDAMQP_URL in .env")

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    threads = []
    for i in range(1, num_devices + 1):
        device_id = f"meter-{i:03d}"

        thread = threading.Thread(
            target=device_loop,
            args=(device_id,),
            daemon=True,
        )
        thread.start()
        threads.append(thread)

    while RUNNING:
        time.sleep(1)

    for thread in threads:
        thread.join(timeout=1)


if __name__ == "__main__":
    main()