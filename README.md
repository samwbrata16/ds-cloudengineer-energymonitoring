\---

# Cloud Energy Monitoring IoT Project

A cloud-based IoT telemetry pipeline project for Digital Skola Cloud Engineer Bootcamp using managed services, Python-based device simulation, a simulated fleet of IoT devices sending telemetry to a cloud message broker, a time-series database and a visualized dashboard with Grafana.

\---

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

|Component|Role|
|-|-|
|Python Producers|Simulated IoT devices sending telemetry|
|CloudAMQP|Managed message broker buffering device data|
|Python Consumer|Reads queue messages and stores them|
|InfluxDB 3|Time-series database for telemetry|
|Grafana|Visualization dashboards|

\---

# Project Structure

```
ds-cloudengineer-energymonitoring/
│
├── requirements.txt
├── .env.example
├── README.md
│
├── scripts/
│   ├── test\\\_broker\\\_connection.py
│   └── test\\\_influx\\\_write.py
│
├── producers/
│   ├── single\\\_device\\\_producer.py
│   └── fleet\\\_device\\\_simulator.py
│
└── consumers/
    ├── queue\\\_message\\\_logger.py
    ├── minimal\\\_amqp\\\_to\\\_influx.py
    └── amqp\\\_to\\\_influx\\\_service.py    
└── screenshots/
    ├── Screenshot-Grafana-Dasboard.png
    ├── Screenshot-InfluxDB.png
    ├── Screenshot-LavinMQ.png
    └── dashboard.json        
```

\---

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

\---

## 2 Create virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\\\\Scripts\\\\activate
```

\---

## 3 Install dependencies

```bash
pip install -r requirements.txt
```

Dependencies:

|Package|Purpose|
|-|-|
|pika|AMQP client for CloudAMQP|
|influxdb3-python|InfluxDB client|
|python-dotenv|Load environment variables|
|pandas|Used for query output formatting|

\---

# Environment Configuration

Create a `.env` file from the template.

```bash
cp .env.example .env
```

Edit `.env`:

```
CLOUDAMQP\\\_URL=amqps://USERNAME:PASSWORD@raccoon.lmq.cloudamqp.com/VHOST

INFLUX3\\\_HOST=https://us-east-1-1.aws.cloud2.influxdata.com
INFLUX3\\\_ORG=Dev
INFLUX3\\\_DATABASE=room-monitoring
INFLUX3\\\_TOKEN=YOUR\\\_INFLUX\\\_TOKEN
```

Required values:

|Variable|Description|
|-|-|
|CLOUDAMQP\_URL|CloudAMQP broker connection URL|
|INFLUX3\_HOST|InfluxDB Cloud endpoint|
|INFLUX3\_ORG|Influx organization|
|INFLUX3\_DATABASE|Database name|
|INFLUX3\_TOKEN|API token|

\---

# Script Overview

## scripts/

### test\_broker\_connection.py

Purpose:

Test connectivity to CloudAMQP.

Steps performed:

1. connect to AMQP broker
2. declare queue
3. publish test message
4. close connection

Run:

```bash
python scripts/test\\\_broker\\\_connection.py
```

Expected output:

```
\\\[OK] Queue declared
\\\[OK] Test message published
```

\---

### test\_influx\_write.py

Purpose:

Validate InfluxDB connectivity.

Functions:

* write sample points
* execute SQL query
* print query results

Run:

```bash
python scripts/test\\\_influx\\\_write.py
```

Expected output:

```
STEP 1: Writing test points
STEP 2: Running query
STEP 3: Query results
```

\---

# Producer Scripts

Producer scripts simulate IoT devices sending telemetry.

Queue used:

```
energy\\\_telemetry
```

\---

## single\_device\_producer.py

Simulates one IoT device.

Telemetry example:

```json
{
    "device\\\_id": "meter-001",
    "voltage": 230.5,
    "current": 4.2,
    "power": 967.3,
    "energy": 15.6,
    "power\\\_factor": 0.94,
    "signal\\\_rssi": -68,
    "ts": now\\\_iso(),

}
```

Run:

```bash
python producers/single\\\_device\\\_producer.py
```

\---

## fleet\_device\_simulator.py

Simulates multiple devices concurrently.

Features:

* multiple device threads
* randomized telemetry
* random publish intervals

Run:

```bash
python producers/fleet\\\_device\\\_simulator.py
```

Default simulation:

```
20 devices
```

Example output:

```
\\\[PUB] meter-005 -> {...}
\\\[PUB] meter-012 -> {...}
```

\---

# Consumer Scripts

Consumers read queue messages and process them.

\---

## queue\_message\_logger.py

Simple debugging consumer.

Purpose:

Inspect raw messages in the queue.

Run:

```bash
python consumers/queue\\\_message\\\_logger.py
```

Output example:

```
\\\[MSG] {"device\\\_id":"meter-001",...}
```

\---

## minimal\_amqp\_to\_influx.py

Minimal ingestion pipeline.

Workflow:

```
AMQP Queue → InfluxDB
```

Stores limited fields:

* device\_id
* voltage
* current
* power
* energy
* power\_factor
* frequency

Run:

```bash
python consumers/minimal\\\_amqp\\\_to\\\_influx.py
```

\---

## amqp\_to\_influx\_service.py

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

|Tag|Field|
|-|-|
|device\_id|voltage|
||current|
||power|
||energy|
||power\_factor|
||frequency|
||signal\_rssi|

Run:

```bash
python consumers/amqp\\\_to\\\_influx\\\_service.py
```

Output:

```
\\\[WRITE] meter-004 -> InfluxDB
```

\---

# Running the End-to-End Demo

Open two terminals.

\---

## Terminal 1

Start ingestion service.

```bash
python consumers/amqp\\\_to\\\_influx\\\_service.py
```

\---

## Terminal 2

Start fleet simulator.

```bash
python producers/fleet\\\_device\\\_simulator.py
```

\---

## Expected behavior

Producer output:

```
\\\[PUB] meter-003 -> {...}
```

Consumer output:

```
\\\[WRITE] meter-003 -> InfluxDB
```

CloudAMQP:

```
Queue activity visible
```

InfluxDB:

```
Rows increasing
```

\---

# Querying Data in InfluxDB

Example SQL queries.

\---

## Latest measurements

```sql
SELECT \\\*
FROM energy\\\_telemetry
ORDER BY time DESC
LIMIT 20;
```

\---

## Average power consumption

```sql
SELECT
AVG(power)
FROM energy\\\_telemetry;
```

\---

## Energy consumption by device

```sql
SELECT
device\\\_id,
SUM(energy)
FROM energy\\\_telemetry
GROUP BY device\\\_id;
```

\---

# Grafana Dashboard

Visualizes data from InfluxDB database in a Grafana dashboard.

\---

## Prerequesites

Ensure you have the following setup:

* A Grafana account.
* A data source \[e.g., InfluxDB]
* Metrics from system/service.

\---

## Configure InfluxDB Data Source

1. Open Grafana in web browser.
2. Click Connections > Data sources.
3. Click Add new data source and select InfluxDB.
4. Configure settings (URL, Organization, Bucket, Toekn, etc.)
5. Click Save \& Test to ensure connectivity.

\---

## Create Dashboard

1. Click Dashboards on the left side menu.
2. Click New and Select New Dashboard
3. Click +Add visualization
4. In the panel editor, select the InfluxDB data source.

\---

## Build Query and Visualize Data

Using the Visual Query Builder, select measurement and fields, and apply any filters or aggregations using the graphical interface, and the query will be automatically built and will display a preview of the data in the visualization pane. Or using the Script Editor, copy the generated Flux or SQL code and paste it into the Grafana query editor's Script Editor.

\---

Customize visualization by selecting a visualization type from the right side menu (e.g., Time series, Gauge, Stat, etc.), adjust panel options like Title, Units, Colors, and Thresholds as needed, and click Apply to add the panel to the dashboard. Click Save dashboard icon and enter a name to save the dashboard.

\---

## Dashboard Panels

Some panels included in the dashboard

\---

## Power consumption over time

```
time series chart
```

Query:

from(bucket: "energy-monitoring")
|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
|> filter(fn: (r) => r.\_measurement == "energy\_telemetry" and r.\_field == "power")
|> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
|> yield(name: "mean")

\---

## Energy usage by device

```
bar chart
```

Query:

from(bucket: "energy-monitoring")
|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
|> filter(fn: (r) => r.\_measurement == "energy\_telemetry" and r.\_field == "energy")
|> group(columns: \["device\_id"])
|> aggregateWindow(every: v.windowPeriod, fn: sum, createEmpty: false)
|> yield(name: "sum")

\---

## Current load monitoring

```
gauge chart
```

Query:

from(bucket: "energy-monitoring")
|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
|> filter(fn: (r) => r.\_measurement == "energy\_telemetry" and r.\_field == "current")
|> last()

\---

# Screenshots folder

This folder contains screenshot images from the Grafana dashboard, InfluxDB database, and LavinMQ queue.

\---

# Troubleshooting

## Broker connection fails

Check:

* CLOUDAMQP\_URL
* network connectivity
* TLS port

Test with:

```bash
python scripts/test\\\_broker\\\_connection.py
```

\---

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
python scripts/test\\\_influx\\\_write.py
```

\---

## Queue receives no messages

Check:

* producer running
* queue name matches
* broker dashboard

\---

# Summary

This project demonstrates a scalable IoT telemetry pipeline using:

* Python device simulation
* managed AMQP messaging
* time-series storage
* real-time dashboards

\---

