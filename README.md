# 🚀 Advanced Site Reliability Engineering (SRE) Project
**Website Uptime & Observability Monitoring Stack**

## 📖 Project Overview
This project is an automated, fully containerized Observability Stack designed to simulate a real-world Site Reliability Engineering (SRE) environment. It dynamically monitors website uptime, calculates Service Level Agreements (SLAs), and tracks latency (response times) across various endpoints using modern SRE principles.

---

## 🏗️ Architecture: How Everything Links Together
The project operates in a continuous, automated pipeline:
**FastAPI UI** ➔ **Python Engine** ➔ **Prometheus** ➔ **Grafana**

1. **Python Monitor (The Probe):** Constantly pings targeted websites to check if they are alive and how fast they respond.
2. **Prometheus (The Database):** Reaches out to the Python app every 10 seconds, collects the raw metric data, and saves it in a Time-Series Database.
3. **Grafana (The Dashboard):** Connects to Prometheus to read the historical data and visualizes it into beautiful, real-time graphs.
4. **Docker (The Engine):** Wraps all three of these separate technologies into isolated "containers" so they can communicate with each other safely on any computer via a private virtual network.

---

## 📂 File Structure & Their Importance

### 1. `backend/monitor.py`
* **What it is:** The brain of the project. A Python script running a FastAPI web server.
* **Importance:** It actively probes websites using `asyncio` and exposes the raw results (like uptime status and HTTP codes) on the `/metrics` endpoint using `prometheus_client`.

### 2. `backend/templates/index.html`
* **What it is:** The frontend UI (User Interface) for the Python app.
* **Importance:** Provides a beautiful "Control Center" where users can dynamically add or remove website URLs to monitor without having to restart the code.

### 3. `prometheus/prometheus.yml`
* **What it is:** The configuration file for the Prometheus database.
* **Importance:** Tells Prometheus *where* to look for data. We configured it to point to `monitor:8000`, which links Prometheus directly to our Python app's metrics.

### 4. `grafana/provisioning/datasources/datasource.yml`
* **What it is:** An Infrastructure-as-Code (IaC) file for Grafana.
* **Importance:** Automatically tells Grafana to connect to Prometheus as its primary database. Because of this file, we don't have to manually connect them in the UI.

### 5. `grafana/provisioning/dashboards/sre_dashboard.json` & `dashboard.yml`
* **What it is:** The blueprint for our visual graphs.
* **Importance:** Contains the exact code needed to render the SLA calculations, red/green status boxes, and latency line graphs inside Grafana automatically on startup.

### 6. `backend/Dockerfile`
* **What it is:** The recipe to build the Python container.
* **Importance:** Tells Docker exactly how to install Python, install our `requirements.txt`, and run `monitor.py` in an isolated Linux environment.

### 7. `docker-compose.yml`
* **What it is:** The master conductor.
* **Importance:** This single file links the Python App, Prometheus, and Grafana together. It creates a virtual network so they can talk to each other, maps the ports (8000, 9090, 3001) to your computer, and starts them all simultaneously.

---

## 🛠️ How to Run the Project
1. Make sure **Docker Desktop** is open and running.
2. Open the terminal in this project folder and run:
   ```bash
   docker-compose up -d
   ```
3. Access the Project:
   - **Control Center UI:** [http://localhost:8000](http://localhost:8000)
   - **Grafana Dashboard:** [http://localhost:3001](http://localhost:3001) *(Login: admin / admin)*
   - **Raw Metrics Data:** [http://localhost:8000/metrics](http://localhost:8000/metrics)

To stop the project safely, run:
```bash
docker-compose down
```
