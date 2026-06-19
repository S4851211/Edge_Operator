# Edge Operator

Edge-side operator interface for receiving trajectories from VILMA, managing trajectory execution, and controlling the Fairino robot.

## Supported Platform

Officially supported:

* Ubuntu 22.04 LTS

Recommended:

* Docker Engine
* Docker Compose v2
* Python managed through UV

Windows is not currently supported. If required, use Ubuntu through WSL2.

---

# First-Time Setup

## 1. Clone the Repository

```bash
git clone https://github.com/S4851211/Edge_Operator.git

cd Edge_Operator
```

---

## 2. Install Docker

Verify Docker:

```bash
docker --version
```

Verify Docker Compose:

```bash
docker compose version
```

---

## 3. Start Infrastructure Services

Start Zenoh DDS Bridge and Vulcanexus:

```bash
docker compose up -d
```

Verify:

```bash
docker ps
```

Expected containers:

```text
zenoh_edge
vulcanexus_vm
```

View logs:

```bash
docker logs zenoh_edge
```

Stop services:

```bash
docker compose down
```

Restart services:

```bash
docker compose up -d
```

---

## 4. Install UV

Install UV:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify:

```bash
uv --version
```

---

## 5. Create Python Environment

Install all Python dependencies:

```bash
uv sync
```

This creates the project virtual environment automatically.

---

## 6. Activate Environment

```bash
source .venv/bin/activate
```

---

## 7. Launch Edge Operator UI

```bash
streamlit run ui/app.py
```

Open:

```text
http://localhost:8501
```

---

# Daily Startup

## Start Infrastructure

```bash
cd ~/Desktop/Fairino

docker compose up -d
```

---

## Activate Environment

```bash
cd ~/Desktop/Fairino

source .venv/bin/activate
```

---

## Launch UI

```bash
streamlit run ui/app.py
```

---

# Trajectory Receiver

Start receiver:

```bash
cd ~/Desktop/Fairino

source .venv/bin/activate

python services/trajectory_receiver.py
```

Expected output:

```text
Waiting for /learned_trajectory ...
```

---

# Trajectory Workflow

1. Generate trajectory in VILMA.
2. Push trajectory to robot.
3. Receiver saves:

```text
data/trajectories/received_trajectory.csv
```

4. Open Edge Operator UI.
5. Verify trajectory status.
6. Execute trajectory.

---

# Repository Structure

```text
Edge_Operator/

├── assets/
├── config/
├── data/
│   └── trajectories/
├── logs/
├── services/
├── ui/
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# Infrastructure Services

## Zenoh DDS Bridge

Container:

```text
zenoh_edge
```

Image:

```text
eclipse/zenoh-bridge-dds:latest
```

Purpose:

* DDS ↔ Zenoh communication
* Trajectory transfer between VILMA and Edge Operator

---

## Vulcanexus

Container:

```text
vulcanexus_vm
```

Image:

```text
eprosima/vulcanexus:humble-desktop
```

Purpose:

* ROS 2 Humble environment
* DDS tooling
* Future ROS-based development and debugging

---

# Updating the Repository

```bash
git pull

docker compose up -d

uv sync
```

This updates:

* Source code
* Infrastructure services
* Python dependencies
