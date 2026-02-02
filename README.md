# Execution Tracking Platform

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-API-black?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql)
![AWS](https://img.shields.io/badge/AWS-Cloud-orange?logo=amazonaws)
![Terraform](https://img.shields.io/badge/Terraform-IaC-purple?logo=terraform)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-orange?logo=linux)
![Git](https://img.shields.io/badge/Git-VersionControl-red?logo=git)

A **Data Engineering + DevOps learning project** that builds a complete execution-tracking system, from API ingestion to cloud infrastructure, orchestration, and transformations.

The project is developed **incrementally, in phases**, with a strong focus on:
- clean architecture
- cloud-native infrastructure
- reproducibility
- real-world tooling (AWS, Terraform, Docker, dbt, Airflow, Kubernetes)

---

## 🧠 Project Goal

Build a production-like platform that:
1. Ingests execution/job metadata via an API
2. Stores raw data in a managed PostgreSQL database
3. Transforms data using dbt
4. Orchestrates workflows with Airflow
5. Runs containerized services on Kubernetes
6. Applies DevOps best practices (IaC, secrets, environments, CI/CD)

## 🏗️ High-Level Architecture (Current & Target)
```text
┌───────────────────────────┐
│ Flask API │ (Docker / K8s)|
│ Ingestion │               |
└─────────────┬─────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ AWS RDS │ ← PostgreSQL (raw / staging) |
└──────────────────┬─────────────────────┘
                   │
┌──────────────────▼─────────────────────┐
│ dbt │ ← transformations                |
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────┐
│ Airflow │ ← orchestration  |
└────────────────────────────┘
```
## ✅ Project Phases

### Phase 1 – Application & API (✅ completed)
- Flask-based ingestion API
- PostgreSQL schema initialization
- `/health` endpoint with environment & version
- `/executions` endpoints (GET / POST)
- Environment-based configuration using `.env`

**Tech**
- Python
- Flask
- psycopg2
- PostgreSQL

---

### Phase 2 – Cloud Infrastructure & DevOps Basics (✅ completed)
- AWS infrastructure provisioned with Terraform
- Custom VPC with public subnets
- Internet Gateway & routing
- EC2 instance running the Flask API
- AWS RDS PostgreSQL instance
- Security Groups for API & DB access
- Manual deployment for learning purposes

**Tech**
- AWS (EC2, RDS, VPC)
- Terraform
- Ubuntu Linux

---

### Phase 3 – Containerization & Orchestration (🚧 next)
- Dockerize the Flask API
- Use docker-compose for local development
- Introduce Kubernetes (local + cloud)
- Move configuration & secrets out of code
- Prepare for scalable deployments

---

### Phase 4 – Data Engineering Layer (🔜 planned)
- dbt project for transformations
- Raw → staging → analytics models
- Versioned transformations
- Documentation & tests in dbt

---

### Phase 5 – Workflow Orchestration (🔜 planned)
- Airflow DAGs for:
  - ingestion checks
  - dbt runs
  - data quality validations
- Scheduling & monitoring

---

### Phase 6 – Production Readiness (🔜 planned)
- CI/CD pipelines
- Terraform remote state
- IAM best practices
- Kubernetes secrets
- Logging & monitoring
- Cost-aware architecture

---

## 📂 Repository Structure (Current)
```text
## 📁 Repository Structure

```text
.
├── ingestion-api/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── app.py          
│   │   ├── config.py       
|   |   ├── requirements.txt
│   │   └── db.py           
│   ├── tests/
│   │   └── tests.py        
│   └── Dockerfile         
│
├── terraform/
│   ├── main.tf             
│   ├── provider.tf         
│   ├── variables.tf        
│   └── outputs.tf         
|
├── .gitignore
└── README.md
```
## 🔐 Configuration

Sensitive values are **not committed**.

Use environment variables or a `.env` file locally:

```env
APP_ENV=dev
APP_VERSION=0.1.0

DB_HOST=...
DB_PORT=5432
DB_NAME=executions_db
DB_USER=postgres
DB_PASSWORD=****
