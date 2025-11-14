# Marsh Cyber Content Aggregation Tool

A proof-of-concept cyber content aggregation tool developed for Marsh Asia Cyber and Digital & Tech Team as part of the BT4103 Business Analytics Capstone Project.

---

## Project Credits

- **Industry Partner:** Marsh Mclennan
- **Module:** BT4103 Business Analytics Capstone Project
- **Group 18 Members:**  
  - [Chan Jie Ru](https://www.linkedin.com/in/chan-jie-ru/)
  - [Coco Li](https://www.linkedin.com/in/coco-li-672686228/)
  - [Fong Kai Jun](https://www.linkedin.com/in/kaijunfong141319/)
  - [Isabella Ren](https://www.linkedin.com/in/isabella-ren/)
  - [Ramanen Bharatwa](https://www.linkedin.com/in/ramanen-bh/)

---

## Executive Summary

This project delivers a complete pipeline for automated cyber risk data ingestion, analysis, and PowerPoint generation, designed to support Marsh insurance consultants and Client Executives (CEs).

The system integrates cyber incident data from multiple sources, including public web data and internal proprietary datasets. Based on a user’s query, AI-powered LangGraph workflows retrieve, extract, and summarise relevant incidents. Outputs are evaluated using Arize Phoenix for hallucination detection and summarisation quality before being compiled into polished, standardised PowerPoint decks suitable for client presentations.

These capabilities are exposed through a React-based web application with three main interfaces:

1. **Slide Generation** – Configure queries and generate client-ready decks.  
2. **Dashboard Analytics** – Explore trends across industries, threat actors, and loss types.  
3. **Data Management** – Upload proprietary data and manage the incident repository.

The remainder of this documentation describes the system architecture, key features, technology stack, and setup instructions.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Deployment](#deployment)
- [Documentation & Key Routes](#documentation--key-routes)
- [Acknowledgements](#licence--acknowledgements)

---

## Overview

The Marsh Cyber Content Aggregation Tool is built to help CEs and cyber specialists:

- Reduce manual effort in searching, reading, and collating cyber incident reports.
- Generate consistent, Marsh-branded slide decks in minutes instead of hours.
- Gain a clearer view of the cyber risk landscape through interactive analytics.

At a high level, the system:

1. **Ingests** cyber incident data from public and proprietary sources into MongoDB.  
2. **Retrieves and summarises** relevant incidents via LangGraph workflows.  
3. **Evaluates** responses using Arize Phoenix to control hallucinations and assess summary quality.  
4. **Generates** PowerPoint decks using a Marsh template stored in S3, including logos and speaker notes.  
5. **Surfaces insights** through dashboards and a data management interface.

This is a **proof-of-concept**, not a production system. It is designed to demonstrate value and provide a foundation for future integration into Marsh’s internal infrastructure.

---

## Key Features

### 1. Automated PowerPoint Generation

- Generates Marsh-branded PowerPoint decks directly from incident data.  
- Uses an S3-hosted template with placeholders (e.g. `{{title}}`, `{{executive_summary}}`).  
- Duplicates template slides per incident and fills in background, malicious activity, outcomes, and losses.  
- Optionally fetches company logos via the Logo.dev API and records source URLs in speaker notes.  
- Uploads the generated deck back to S3 and returns a **presigned URL** for secure, time-limited download.

### 2. Interactive Cyber Analytics Dashboard

- Combines **proprietary Marsh claims data** with **public internet incident data**.  
- Visualises trends by industry, threat actor, event type, and time period.  
- Supports filtering by industry, date range, and incident attributes.  
- Helps CEs frame more data-driven conversations with clients.

### 3. Data Management & Repository

- Allows upload of proprietary incident data into a dedicated S3 and MongoDB pipeline.  
- Organises S3 storage into logical folders (`archives/`, `generated/`, `propdata/`, `template/`).  
- Ensures traceability between stored documents, generated presentations, and dashboard views.

### 4. Human-in-the-Loop by Design

- LLMs assist with retrieval and summarisation, but CEs remain in control.  
- Generated content is surfaced in a preview interface so users can review, edit, and curate before export.  
- Post-edit LLM calls can be applied to refine grammar and tone while preserving meaning.

### 5. Evaluation and Quality Assurance

- Uses **LangGraph** to orchestrate retrieval, summarisation, and validation steps.  
- Integrates with **Arize Phoenix** for monitoring, hallucination detection, and summary quality checks.  
- Provides an auditable trail of generated content and its underlying sources.

---

## System Architecture

### High-Level Components

- **Frontend (React UI)**
  - Slide generation interface
  - Dashboard analytics
  - Data repository and upload views

- **Backend (FastAPI + LangGraph)**
  - Query processing and retrieval
  - Summarisation and evaluation workflow
  - PPT generation API
  - S3 integration and presigned URL handling

- **Data Layer**
  - **MongoDB Atlas** for storing incident documents, metadata, and vector embeddings.  
  - **AWS S3** for templates, generated presentations, and proprietary data files.

- **Infrastructure & Deployment**
  - **Frontend:** Hosted on Render with automatic deployment from GitHub.  
  - **Backend:** Hosted on AWS EC2 behind an **Application Load Balancer (ALB)** with **ACM-managed SSL certificates**.  
  - **IaC:** Terraform used to provision and configure S3 buckets and related resources.  
  - **CI/CD:** GitHub Actions used to deploy backend updates to EC2 and trigger frontend builds on Render.

---

## Technology Stack

### Backend

- **Framework:** FastAPI (Python)  
- **Orchestration:** LangGraph, LangChain  
- **LLMs & Evaluation:** OpenAI models, Arize Phoenix  
- **Database:** MongoDB Atlas  
- **Storage:** AWS S3  
- **PPT Generation:** `python-pptx`, Logo.dev API  
- **Infrastructure:** AWS EC2, ALB, ACM, Terraform  
- **CI/CD:** GitHub Actions

### Frontend

- **Framework:** React  
- **UI Library:** Material UI (MUI) / Material Dashboard 2 React  
- **Charts:** Chart.js, `react-chartjs-2`, Google Charts  
- **State Management:** React Context API  
- **Routing:** React Router  

---

## Project Structure

A simplified view of the repository structure:

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── routes/              # API routes (PPT, dashboards, data)
│   │   ├── services/            # LangGraph workflows, PPT generator
│   │   ├── models/              # Pydantic schemas (ArticlePayload, PPTGenerationRequest, etc.)
│   │   └── config/              # Settings, environment loading on AWS secrets manager
├── frontend/
│   ├── src/
│   │   ├── layouts/             # Dashboard, slides, repository views
│   │   ├── components/          # Charts, tables, forms
│   │   ├── context/             # Global state management
│   │   └── utils/apiConfig.js         # API endpoint configuration
└── README.md
```

---

# Getting Started

## Prerequisites

Ensure the following are installed or available:

* **Node.js v16+**
* **Python 3.10+**
* **MongoDB Atlas cluster**
* **AWS account** with S3 and EC2 access

---

## Environment Variables

### Backend `.env`

```bash
MONGO_URL=
TAVILY_API_KEY=
OPENAI_API_KEY=
PHOENIX_API_KEY=
OTEL_EXPORTER_OTLP_HEADERS=
AWS_ACCESS_KEY_ID =
AWS_SECRET_ACCESS_KEY = 
S3_BUCKET_NAME = 
S3_REGION = 
TEMPLATE_S3_KEY = 
LOGO_DEV_TOKEN = 
ENVIRONMENT="DEV"
```

### frontend `.env`

```bash
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
};
```

---

## Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000
```

The API will be available at:

```
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The application will be available at:

```
http://localhost:3000
```

---

# Deployment

## Frontend (Render)

* Connected directly to [GitHub](https://github.com/ramanenb/Marsh_Cyber_Content_Tool).
* Builds and deploys automatically on each push.
* Environment variables for frontend configured in Render Dashboard.

---

## Backend (AWS EC2 + Application Load Balancer)

* Backend runs on **EC2** with **uvicorn** behind **nginx**.
* **ALB + ACM** handles HTTPS termination.
* ALB forwards HTTP traffic to EC2.
* DNS configured with **ALIAS record → ALB DNS name**
  (A records not supported because ALB IPs rotate).

### GitHub Actions CI/CD

* Triggers when backend code changes.
* SSH into EC2.
* Pulls latest code and restarts service.
* Ensures consistent automated deployments.

---

# S3 & Terraform

Terraform provisions:

* S3 bucket with structure:

```
archives/
generated/
propdata/
template/
```

* Versioning and server-side encryption
* Tagging + bucket IAM policies
* Integration with the PowerPoint generator:

  * Template download
  * Generated file upload
  * Presigned URL generation

---

# Documentation & Key Routes

## API Documentation

```
http://127.0.0.1:8000/docs
```

## Key Frontend Routes

| Route                     | Description                         |
| ------------------------- | ----------------------------------- |
| `/dashboard/Marsh`              | Proprietary data dashboard |
| `/dashboard/Internet`     | Public-only internet incident data  |
| `/slides`                 | Slide generation interface          |
| `/repository`             | Document & presentation repository  |
| `login` | Login                               |

---

Special thanks to:

* Marsh Asia Cyber and Digital & Tech Teams (Jaydeep, Joseph, Linden, and Sam)
* Supervisor Professor Rudy Setioo
* Teaching assistant: Ms. Liu Yan