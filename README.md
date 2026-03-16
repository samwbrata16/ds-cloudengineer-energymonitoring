
---

# Cloud Energy Monitoring IoT Project

A cloud-based IoT telemetry pipeline project for Digital Skola Cloud Engineer Bootcamp using managed services, Python-based device simulation, a simulated fleet of IoT devices sending telemetry to a cloud message broker, a time-series database and a visualized dashboard with Grafana.

---

# Architecture Overview

The system architecture:

```
Python Device Simulators
        │
        ▼
CloudAMQP (LavinMQ) Queue
        │
        ▼
Python Ingestion Service
        │
        ▼
InfluxDB 3 (Time-Series Database)
        │
        ▼
Grafana Dashboards
```

Pipeline flow:

```
Producer(s) → CloudAMQP Queue → Consumer → InfluxDB → Grafana
```

Each component has a clearly defined role:

| Component        | Role                                         |
| ---------------- | -------------------------------------------- |
| Python Producers | Simulated IoT devices sending telemetry      |
| CloudAMQP        | Managed message broker buffering device data |
| Python Consumer  | Reads queue messages and stores them         |
| InfluxDB 3       | Time-series database for telemetry           |
| Grafana          | Visualization dashboards                     |

---

# Project Structure

```
ds-cloudengineer-energymonitoring/
│
├── requirements.txt
├── .env.example
├── README.md
│
├── scripts/
│   ├── test_broker_connection.py
│   └── test_influx_write.py
│
├── producers/
│   ├── single_device_producer.py
│   └── fleet_device_simulator.py
│
└── consumers/
    ├── queue_message_logger.py
    ├── minimal_amqp_to_influx.py
    └── amqp_to_influx_service.py    
└── screenshots/
    ├── Screenshot-Grafana-Dasboard.png
    ├── Screenshot-InfluxDB.png
    ├── Screenshot-LavinMQ.png
    └── dashboard.json        
```

---

# Environment Setup

## 1 Install Python

Recommended:

```
Python 3.10+
```

Check version:

```bash
python --version
```

---

## 2 Create virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

---

## 3 Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies:

| Package          | Purpose                          |
| ---------------- | -------------------------------- |
| pika             | AMQP client for CloudAMQP        |
| influxdb3-python | InfluxDB client                  |
| python-dotenv    | Load environment variables       |
| pandas           | Used for query output formatting |

---

# Environment Configuration

Create a `.env` file from the template.

```bash
cp .env.example .env
```

Edit `.env`:

```
CLOUDAMQP_URL=amqps://USERNAME:PASSWORD@raccoon.lmq.cloudamqp.com/VHOST

INFLUX3_HOST=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUX3_ORG=Dev
INFLUX3_DATABASE=room-monitoring
INFLUX3_TOKEN=YOUR_INFLUX_TOKEN
```

Required values:

| Variable         | Description                     |
| ---------------- | ------------------------------- |
| CLOUDAMQP_URL    | CloudAMQP broker connection URL |
| INFLUX3_HOST     | InfluxDB Cloud endpoint         |
| INFLUX3_ORG      | Influx organization             |
| INFLUX3_DATABASE | Database name                   |
| INFLUX3_TOKEN    | API token                       |

---

# Script Overview

## scripts/

### test_broker_connection.py

Purpose:

Test connectivity to CloudAMQP.

Steps performed:

1. connect to AMQP broker
2. declare queue
3. publish test message
4. close connection

Run:

```bash
python scripts/test_broker_connection.py
```

Expected output:

```
[OK] Queue declared
[OK] Test message published
```

---

### test_influx_write.py

Purpose:

Validate InfluxDB connectivity.

Functions:

* write sample points
* execute SQL query
* print query results

Run:

```bash
python scripts/test_influx_write.py
```

Expected output:

```
STEP 1: Writing test points
STEP 2: Running query
STEP 3: Query results
```

---

# Producer Scripts

Producer scripts simulate IoT devices sending telemetry.

Queue used:

```
energy_telemetry
```

---

## single_device_producer.py

Simulates one IoT device.

Telemetry example:

```json
{
    "device_id": "meter-001",
    "voltage": 230.5,
    "current": 4.2,
    "power": 967.3,
    "energy": 15.6,
    "power_factor": 0.94,
    "signal_rssi": -68,
    "ts": now_iso(),

}
```

Run:

```bash
python producers/single_device_producer.py
```

---

## fleet_device_simulator.py

Simulates multiple devices concurrently.

Features:

* multiple device threads
* randomized telemetry
* random publish intervals

Run:

```bash
python producers/fleet_device_simulator.py
```

Default simulation:

```
20 devices
```

Example output:

```
[PUB] meter-005 -> {...}
[PUB] meter-012 -> {...}
```

---

# Consumer Scripts

Consumers read queue messages and process them.

---

## queue_message_logger.py

Simple debugging consumer.

Purpose:

Inspect raw messages in the queue.

Run:

```bash
python consumers/queue_message_logger.py
```

Output example:

```
[MSG] {"device_id":"meter-001",...}
```

---

## minimal_amqp_to_influx.py

Minimal ingestion pipeline.

Workflow:

```
AMQP Queue → InfluxDB
```

Stores limited fields:

* device_id
* voltage
* current
* power
* energy
* power_factor
* frequency

Run:

```bash
python consumers/minimal_amqp_to_influx.py
```

---

## amqp_to_influx_service.py

Full ingestion service used for the final workshop.

Workflow:

```
Queue message
    ↓
JSON decode
    ↓
InfluxDB Point
    ↓
Write to database
```

Stored fields:

| Tag         | Field         |
| ----------- | ------------- |
| device_id   | voltage       |
|             | current       |
|             | power         |
|             | energy        |
|             | power_factor  |
|             | frequency     |
|             | signal_rssi   |

Run:

```bash
python consumers/amqp_to_influx_service.py
```

Output:

```
[WRITE] meter-004 -> InfluxDB
```

---

# Running the End-to-End Demo

Open two terminals.

---

## Terminal 1

Start ingestion service.

```bash
python consumers/amqp_to_influx_service.py
```

---

## Terminal 2

Start fleet simulator.

```bash
python producers/fleet_device_simulator.py
```

---

## Expected behavior

Producer output:

```
[PUB] meter-003 -> {...}
```

Consumer output:

```
[WRITE] meter-003 -> InfluxDB
```

CloudAMQP:

```
Queue activity visible
```

InfluxDB:

```
Rows increasing
```

---

# Querying Data in InfluxDB

Example SQL queries.

---

## Latest measurements

```sql
SELECT *
FROM energy_telemetry
ORDER BY time DESC
LIMIT 20;
```

---

## Average power consumption

```sql
SELECT
AVG(power)
FROM energy_telemetry;
```

---

## Energy consumption by device

```sql
SELECT
device_id,
SUM(energy)
FROM energy_telemetry
GROUP BY device_id;
```

---

# Grafana Dashboard

Visualizes data from InfluxDB database in a Grafana dashboard.

---

## Prerequesites
Ensure you have the following setup:
* A Grafana account.
* A data source [e.g., InfluxDB]
* Metrics from system/service.

---

## Configure InfluxDB Data Source
1. Open Grafana in web browser.
2. Click Connections > Data sources.
3. Click Add new data source and select InfluxDB.
4. Configure settings (URL, Organization, Bucket, Toekn, etc.)
5. Click Save & Test to ensure connectivity.

---

## Create Dashboard
1. Click Dashboards on the left side menu.
2. Click New and Select New Dashboard
3. Click +Add visualization
4. In the panel editor, select the InfluxDB data source.

---

## Build Query and Visualize Data
Using the Visual Query Builder, select measurement and fields, and apply any filters or aggregations using the graphical interface, and the query will be automatically built and will display a preview of the data in the visualization pane. Or using the Script Editor, copy the generated Flux or SQL code and paste it into the Grafana query editor's Script Editor.

---

Customize visualization by selecting a visualization type from the right side menu (e.g., Time series, Gauge, Stat, etc.), adjust panel options like Title, Units, Colors, and Thresholds as needed, and click Apply to add the panel to the dashboard. Click Save dashboard icon and enter a name to save the dashboard.

## Dashboard Panels

Some panels included in the dashboard

---

## Power consumption over time

```
time series chart
```

Query:

from(bucket: "energy-monitoring")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "energy_telemetry" and r._field == "power")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "mean")

---

## Energy usage by device

```
bar chart
```

Query:

from(bucket: "energy-monitoring")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "energy_telemetry" and r._field == "energy")
  |> group(columns: ["device_id"])
  |> aggregateWindow(every: v.windowPeriod, fn: sum, createEmpty: false)
  |> yield(name: "sum")

---

## Current load monitoring

```
gauge chart
```

Query:

from(bucket: "energy-monitoring")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "energy_telemetry" and r._field == "current")
  |> last()


---

# Troubleshooting

## Broker connection fails

Check:

* CLOUDAMQP_URL
* network connectivity
* TLS port

Test with:

```bash
python scripts/test_broker_connection.py
```

---

## Influx authentication error

Error example:

```
401 unauthorized
```

Solution:

* regenerate API token
* confirm org name
* verify database name

Test with:

```bash
python scripts/test_influx_write.py
```

---

## Queue receives no messages

Check:

* producer running
* queue name matches
* broker dashboard

---

# Summary

This project demonstrates a scalable IoT telemetry pipeline using:

* Python device simulation
* managed AMQP messaging
* time-series storage
* real-time dashboards

---