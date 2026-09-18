# CloudOps Prometheus Integration

## Overview

CloudOps integrates with Prometheus to retrieve infrastructure metrics.

The initial development implementation monitors a Windows development host using `windows_exporter`.

Linux production monitoring will later use Node Exporter.

---

## Architecture

```text
CloudOps API
     |
     v
Prometheus Service Layer
     |
     v
Prometheus HTTP API
     |
     v
Prometheus
     |
     v
windows_exporter
     |
     +-----------+-----------+
     |           |           |
     v           v           v
    CPU        Memory       Disk
```

---

## Development Ports

```text
CloudOps:
127.0.0.1:8001

Prometheus:
127.0.0.1:9090

windows_exporter:
127.0.0.1:9182

PostgreSQL:
127.0.0.1:5432
```

---

## Prometheus Configuration

Local Prometheus configuration is stored in:

```text
prometheus/prometheus.yml
```

Current scrape targets:

```text
Prometheus
127.0.0.1:9090

Windows Exporter
127.0.0.1:9182
```

The local Prometheus server is intentionally bound to the loopback interface during development.

---

## Windows Metrics

CloudOps currently reads:

```text
CPU usage
Memory usage
Logical disk usage
```

from windows_exporter.

---

## CloudOps Metrics API

### Prometheus Health

```http
GET /api/metrics/health
```

Verifies that CloudOps can communicate with the Prometheus query API.

---

### CPU

```http
GET /api/metrics/servers/{server_id}/cpu
```

Example:

```json
{
  "server_id": 1,
  "server_name": "DEV-CLOUDOPS-01",
  "instance": "127.0.0.1:9182",
  "metric": "cpu_usage",
  "value": 25.5,
  "unit": "percent",
  "available": true
}
```

---

### Memory

```http
GET /api/metrics/servers/{server_id}/memory
```

Returns physical-memory utilization as a percentage.

---

### Disk

```http
GET /api/metrics/servers/{server_id}/disk
```

Returns disk utilization for available drive volumes.

---

### Overview

```http
GET /api/metrics/servers/{server_id}/overview
```

Combines:

```text
CPU
Memory
Disk
```

into a dashboard-ready response.

---

## Service Layer

PromQL is kept inside:

```text
app/services/prometheus.py
```

API consumers do not need to know Prometheus query syntax.

Flow:

```text
API Request
    |
    v
Metrics Router
    |
    v
Prometheus Service
    |
    v
PromQL
    |
    v
Prometheus HTTP API
    |
    v
Normalized CloudOps Response
```

---

## RBAC

Infrastructure metrics are read-only.

Access is available to:

```text
Admin
Engineer
Viewer
```

---

## Development Safety

Development exporters and Prometheus are bound to loopback addresses.

Current local bindings:

```text
127.0.0.1:9090
127.0.0.1:9182
```

This avoids exposing development monitoring interfaces to other systems.

---

## Testing

Automated tests mock Prometheus responses.

Tests therefore do not require:

```text
Live Prometheus
Live exporters
External network access
```

This makes the suite suitable for future CI/CD.

---

## Current Status

```text
Prometheus Integration       Implemented
Prometheus HTTP API Client   Implemented
Windows Exporter             Implemented
CPU Metrics                  Implemented
Memory Metrics               Implemented
Disk Metrics                 Implemented
Metrics Overview             Implemented
Metrics RBAC                 Implemented
Automated Tests              Implemented

Node Exporter                Planned
Linux VPS Metrics            Planned
Prometheus Alert Rules       Planned
Grafana                      Future Enhancement
```