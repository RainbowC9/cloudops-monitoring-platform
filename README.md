# CloudOps Monitoring Platform

Cloud infrastructure monitoring and incident management platform built with Python, FastAPI, PostgreSQL, Prometheus, Docker, and Linux.

> 🚧 **Project Status:** Active Development
> Current Version: `v0.1.0`

---

## Overview

CloudOps is a production-style portfolio project designed to demonstrate backend development, infrastructure monitoring, incident management, Linux administration, containerization, and DevOps practices.

The platform is intended to provide a centralized view of server health, application availability, operational incidents, alerts, and infrastructure metrics.

The project is being developed incrementally using GitHub Issues, milestones, versioned releases, documentation, and a structured development roadmap.

---

## Project Objectives

The main objectives of CloudOps are to:

* Monitor Linux server health and infrastructure metrics
* Track CPU, memory, disk usage, uptime, and service availability
* Perform application and HTTP health checks
* Maintain a centralized server inventory
* Detect infrastructure problems using configurable alert thresholds
* Automatically create incidents from monitoring alerts
* Manage the complete incident lifecycle
* Maintain incident history and audit trails
* Send external alert notifications
* Provide REST APIs for monitoring and incident management
* Containerize the application using Docker
* Deploy the platform on a Linux server
* Configure HTTPS and reverse proxying through Nginx
* Implement automated testing
* Build a CI/CD pipeline using GitHub Actions

---

## Planned Architecture

```text
                         Internet
                            |
                          HTTPS
                            |
                         Nginx
                    Reverse Proxy
                            |
                            v
                         FastAPI
                    Application API
                   /       |        \
                  /        |         \
                 v         v          v
          PostgreSQL   Prometheus   Alert Engine
                           |
                           v
                     Node Exporter
                           |
                           v
                       Linux Host
```

The architecture will evolve throughout development as monitoring, alerting, deployment, and automation components are introduced.

More detailed architecture documentation is available in:

```text
docs/architecture.md
```

---

## Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn
* REST API

### Database

* PostgreSQL
* SQLAlchemy
* Alembic

### Monitoring

* Prometheus
* Node Exporter
* Application health checks
* HTTP endpoint monitoring

### Infrastructure

* Linux
* Docker
* Docker Compose
* Nginx
* HTTPS / TLS

### DevOps

* Git
* GitHub
* GitHub Issues
* GitHub Projects
* GitHub Actions
* CI/CD

### Testing

* Pytest
* FastAPI TestClient

### Notifications

Planned integrations:

* Discord Webhooks
* Email notifications

---

## Planned Features

### Authentication and Access Control

* User authentication
* Secure password storage
* User roles
* Role-based access control
* Admin, Engineer, and Viewer permissions

### Server Inventory

* Register monitored servers
* Store hostname and IP address
* Define environment such as Production or Staging
* Record operating system information
* View server status
* Edit server information
* Remove inactive servers

### Server Monitoring

CloudOps will monitor metrics including:

* CPU usage
* Memory usage
* Disk usage
* System uptime
* Load average
* Filesystem availability
* Network statistics
* Server availability

### Application Monitoring

The platform will also monitor application-level services.

Planned checks include:

* HTTP status
* API availability
* Response latency
* Database connectivity
* Application health endpoints
* Service availability

### Incident Management

Incidents will support:

* Unique incident numbers
* Incident title
* Description
* Severity
* Status
* Assigned engineer
* Related server
* Created timestamp
* Resolution timestamp

Planned incident statuses:

```text
OPEN
ACKNOWLEDGED
INVESTIGATING
RESOLVED
CLOSED
```

Planned severity levels:

```text
P1 - Critical
P2 - High
P3 - Medium
P4 - Low
```

### Incident Timeline

Every important incident change will be recorded.

Examples include:

* Incident created
* Incident acknowledged
* Engineer assigned
* Investigation started
* Incident updated
* Incident resolved
* Incident closed

This provides an audit trail of the complete incident lifecycle.

### Alert Rules

Administrators will be able to configure monitoring thresholds.

Example:

```text
CPU Warning:      70%
CPU Critical:     90%

Memory Warning:   75%
Memory Critical:  90%

Disk Warning:     80%
Disk Critical:    95%
```

### Automatic Incident Creation

CloudOps will automatically create incidents when monitoring thresholds are exceeded.

Example workflow:

```text
Monitoring detects CPU usage of 94%
                |
                v
Check configured threshold
                |
                v
Critical threshold exceeded
                |
                v
Check for existing active incident
          /             \
        Yes              No
         |                |
         v                v
Update incident     Create incident
         \                /
          \              /
                 v
          Send notification
```

Incident deduplication will help prevent duplicate incidents from being created repeatedly for the same active problem.

### Alert Notifications

Planned notification channels include:

* Discord
* Email

Example notification:

```text
CLOUDOPS ALERT

Severity:
P1 Critical

Server:
PROD-WEB-01

Issue:
CPU Usage Critical

Current Usage:
94%

Threshold:
90%

Incident:
INC-2026-0001
```

---

## Current Features

The project is currently in its database foundation stage.

Completed:

- [x] Repository initialization
- [x] FastAPI project foundation
- [x] Application health endpoint
- [x] Application readiness endpoint
- [x] Interactive FastAPI API documentation
- [x] Environment configuration
- [x] PostgreSQL database setup
- [x] SQLAlchemy integration
- [x] Psycopg PostgreSQL driver
- [x] Database connection validation
- [x] Alembic migration environment
- [x] Initial architecture documentation
- [x] Project development roadmap

Planned:

- [ ] Initial database schema
- [ ] Initial Alembic schema migration
- [ ] Authentication
- [ ] Role-based permissions
- [ ] Server inventory
- [ ] Monitoring engine
- [ ] Prometheus integration
- [ ] Node Exporter integration
- [ ] Monitoring dashboard
- [ ] Incident management
- [ ] Incident timeline
- [ ] Alert rules
- [ ] Automatic incident creation
- [ ] Discord notifications
- [ ] Docker containerization
- [ ] Linux VPS deployment
- [ ] Nginx reverse proxy
- [ ] HTTPS configuration
- [ ] Automated tests
- [ ] GitHub Actions
- [ ] CI/CD
- [ ] Production release

---

## Current API

### Root Endpoint

```http
GET /
```

Returns basic application information.

Example response:

```json
{
  "name": "CloudOps",
  "environment": "development",
  "status": "running",
  "version": "0.1.0"
}
```

### Liveness Check

```http
GET /health
```

Confirms that the CloudOps application is running.

Example response:

```json
{
  "status": "healthy",
  "application": "CloudOps",
  "version": "0.1.0"
}
```

### Readiness Check

```http
GET /ready
```

Confirms that CloudOps is ready to serve requests and can successfully connect to PostgreSQL.

Example response:

```json
{
  "status": "ready",
  "database": "connected",
  "application": "CloudOps",
  "version": "0.1.0"
}
```

If the database is unavailable, the endpoint returns HTTP `503 Service Unavailable`.

Example response:

```json
{
  "status": "not_ready",
  "database": "unavailable",
  "application": "CloudOps",
  "version": "0.1.0"
}
```

---

## API Documentation

FastAPI provides interactive API documentation during development.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

The current API includes:

```text
GET /
GET /health
GET /ready
```

---

## Current Project Structure

```text
cloudops-monitoring-platform/
│
├── app/
│   ├── __init__.py
│   └── main.py
│
├── docs/
│   ├── architecture.md
│   └── project-plan.md
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

The project structure will expand as new components are implemented.

The planned structure includes:

```text
cloudops-monitoring-platform/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── templates/
│   └── static/
│
├── tests/
│
├── migrations/
│
├── prometheus/
│   └── prometheus.yml
│
├── nginx/
│   └── nginx.conf
│
├── docs/
│   ├── architecture.md
│   ├── project-plan.md
│   ├── deployment.md
│   └── screenshots/
│
├── .github/
│   └── workflows/
│
├── .env.example
├── .gitignore
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Local Development

### Requirements

Before running CloudOps locally, install:

* Python 3
* Git
* VS Code or another code editor

PostgreSQL and Docker will be required in later development phases.

---

## Clone the Repository

```bash
git clone https://github.com/RainbowC9/cloudops-monitoring-platform.git
```

Move into the project directory:

```bash
cd cloudops-monitoring-platform
```

---

## Create a Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a local `.env` file when environment variables are required.

The `.env` file must never be committed to GitHub.

Example public configuration is provided in:

```text
.env.example
```

Current example:

```env
APP_NAME=CloudOps
APP_ENV=development
APP_DEBUG=true
APP_VERSION=0.1.0

DATABASE_URL=postgresql://cloudops:password@localhost:5432/cloudops

SECRET_KEY=replace-with-your-secret-key
```

The values above are placeholders only.

Real database passwords, API keys, tokens, and secret keys must only be stored in the private `.env` file or another secure secrets-management system.

---

## Run the Development Server

Start FastAPI using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application should become available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

## Database Design

The planned application database will contain tables such as:

```text
users
roles
servers
services
health_checks
incidents
incident_events
alert_rules
alerts
audit_logs
```

Planned relationships:

```text
Server
  |
  |--- Health Checks
  |
  |--- Services
  |
  |--- Alerts
  |
  `--- Incidents
          |
          `--- Incident Events
```

Database implementation will use PostgreSQL with SQLAlchemy and Alembic migrations.

---

## Planned REST API

### Authentication

```http
POST /api/auth/login
POST /api/auth/logout
```

### Servers

```http
GET    /api/servers
POST   /api/servers
GET    /api/servers/{id}
PUT    /api/servers/{id}
DELETE /api/servers/{id}
```

### Monitoring

```http
GET /api/servers/{id}/health
GET /api/servers/{id}/metrics
```

### Incidents

```http
GET  /api/incidents
POST /api/incidents
GET  /api/incidents/{id}
PUT  /api/incidents/{id}

POST /api/incidents/{id}/acknowledge
POST /api/incidents/{id}/resolve
```

### Alerts

```http
GET  /api/alerts
GET  /api/alert-rules
POST /api/alert-rules
PUT  /api/alert-rules/{id}
```

These endpoints represent the planned API and will be implemented incrementally.

---

## Development Roadmap

CloudOps follows an eight-week development plan.

| Phase   | Focus                               | Status         |
| ------- | ----------------------------------- | -------------- |
| Phase 1 | Foundation & Architecture           | 🚧 In Progress |
| Phase 2 | Authentication & Server Inventory   | ⏳ Planned      |
| Phase 3 | Monitoring Engine                   | ⏳ Planned      |
| Phase 4 | Prometheus & Infrastructure Metrics | ⏳ Planned      |
| Phase 5 | Incident Management                 | ⏳ Planned      |
| Phase 6 | Alert Automation                    | ⏳ Planned      |
| Phase 7 | Docker & Production Deployment      | ⏳ Planned      |
| Phase 8 | CI/CD, Testing & Documentation      | ⏳ Planned      |

Planned development period:

```text
September 5, 2026 - October 31, 2026
```

The complete Gantt chart and weekly milestones are available in:

```text
docs/project-plan.md
```

---

## Development Workflow

The project uses a structured development workflow:

```text
Backlog
   |
   v
Ready
   |
   v
In Progress
   |
   v
Testing
   |
   v
Done
```

GitHub Issues are used to manage individual development tasks.

GitHub Projects is used to track overall development progress.

Milestones are used to group tasks into major releases.

---

## Planned Release Milestones

```text
v0.1 - Foundation
v0.2 - Application Core
v0.3 - Monitoring
v0.4 - Incident Management
v0.5 - Automation
v0.9 - Release Candidate
v1.0 - Production Portfolio Release
```

---

## Deployment Strategy

The final production environment is planned to use a Linux VPS.

Planned deployment architecture:

```text
GitHub
   |
   | git push
   v
GitHub Actions
   |
   | Test
   | Build
   | Deploy
   v
Linux VPS
   |
   |--- Docker
   |--- FastAPI
   |--- PostgreSQL
   |--- Prometheus
   |--- Node Exporter
   `--- Nginx
```

Nginx will act as the reverse proxy and HTTPS entry point.

Docker Compose will manage the application's services.

---

## CI/CD

A GitHub Actions workflow will eventually automate:

```text
Push / Pull Request
        |
        v
Install dependencies
        |
        v
Run linting
        |
        v
Run automated tests
        |
        v
Build Docker image
        |
        v
Deploy to server
```

CI/CD will be introduced later in the development roadmap.

---

## Security

Security is an important part of this project.

The repository must never contain:

* Real passwords
* Database credentials
* SSH private keys
* API keys
* Discord webhook URLs
* Authentication tokens
* Production IP credentials
* `.env` files
* Real company infrastructure information

The following file is ignored by Git:

```text
.env
```

A safe public template is provided instead:

```text
.env.example
```

Demo environments and synthetic data will be used instead of real company infrastructure.

---

## Example Demo Infrastructure

The final demonstration environment may use sample servers such as:

```text
PROD-WEB-01
PROD-DB-01
STAGING-01
BACKUP-01
```

These names represent fictional infrastructure created for demonstration purposes.

---

## Testing

Automated testing will be introduced during development.

Planned testing includes:

* API endpoint testing
* Authentication testing
* Server CRUD testing
* Incident lifecycle testing
* Alert rule testing
* Health check testing
* Database integration testing

Testing tools:

```text
Pytest
FastAPI TestClient
```

---

## Documentation

Project documentation is stored under:

```text
docs/
```

Current documentation:

```text
docs/
├── architecture.md
└── project-plan.md
```

Planned documentation:

```text
docs/
├── architecture.md
├── project-plan.md
├── deployment.md
└── screenshots/
```

---

## Screenshots

Application screenshots will be added once the monitoring dashboard and incident management interface are implemented.

Planned screenshots include:

* Monitoring dashboard
* Server inventory
* Server details
* Infrastructure metrics
* Incident list
* Incident details
* Incident timeline
* Alert configuration
* Swagger API documentation

---

## Project Management

Development progress is managed using:

* GitHub Issues
* GitHub Projects
* GitHub Milestones
* Git commits
* Version releases
* Project documentation

This project is intentionally being developed incrementally to reflect a real software engineering workflow instead of being uploaded as a completed code dump.

---

## Future Enhancements

Potential future improvements after `v1.0` include:

* Multiple monitored agents
* Email alerts
* Slack notifications
* Grafana integration
* WebSocket live metrics
* Kubernetes deployment
* Redis-based task processing
* Background job workers
* Maintenance windows
* Alert escalation rules
* SLA tracking
* Incident analytics
* Mean Time to Acknowledge metrics
* Mean Time to Resolve metrics
* Infrastructure grouping
* Multiple environments
* API key authentication
* Audit log viewer
* Backup monitoring
* SSL certificate expiry monitoring

These features are not part of the initial `v1.0` scope.

---

## Learning Goals

This project is being developed to strengthen practical experience in:

* Python backend development
* FastAPI
* REST API design
* PostgreSQL
* Database modelling
* Linux administration
* Infrastructure monitoring
* Prometheus
* Incident management
* Docker
* Reverse proxies
* HTTPS
* Automated testing
* CI/CD
* GitHub Actions
* Production deployment
* Troubleshooting
* System architecture

---

## Project Status

CloudOps is currently under active development.

Current development phase:

```text
Phase 1 - Foundation & Architecture
```

Current version:

```text
v0.1.0
```

---

## Repository

GitHub:

https://github.com/RainbowC9/cloudops-monitoring-platform

---

## Author

**RainbowC9**

GitHub: https://github.com/RainbowC9

Developed as a software engineering and CloudOps portfolio project.

---

## License

This project is licensed under the MIT License.
